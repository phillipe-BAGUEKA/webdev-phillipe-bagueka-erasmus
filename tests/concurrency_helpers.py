"""Test-only real PostgreSQL lock-wait coordination, shared by 2C and 2D."""

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from threading import Event, local
from time import monotonic
from typing import Any
from unittest.mock import patch

from django.db import connection, connections

from src.data import booking_creation as data
from src.data.models import Booking
from src.services.booking_creation import BookingError

WAIT_SECONDS = 15


@dataclass(frozen=True)
class Outcome:
    pid: int
    result: object | None
    refusal: BookingError | None


def database_identity() -> int:
    """Refuse the development database before touching any business row."""
    assert connection.vendor == "postgresql"
    assert connection.get_autocommit()
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_backend_pid(), current_database(), inet_server_port()")
        pid, database, port = cursor.fetchone()
    assert database == "test_lab_booking_1a"
    assert port == 5433
    return pid


def wait_for_blocker(blocked_pid: int, holder_pid: int, table: str) -> None:
    """Require a real server-observed SELECT FOR UPDATE wait, not just threads."""
    deadline = monotonic() + 5
    poll = Event()
    while monotonic() < deadline:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_blocking_pids(pid), wait_event_type, query "
                "FROM pg_stat_activity WHERE pid = %s "
                "AND datname = current_database()",
                [blocked_pid],
            )
            state = cursor.fetchone()
        if (state and holder_pid in state[0] and state[1] == "Lock"
                and "FOR UPDATE" in state[2] and table in state[2]):
            return
        # Poll a database condition; this delay is not the concurrency proof.
        poll.wait(0.01)
    raise AssertionError("PostgreSQL did not show the expected row-lock wait.")


def run_locked_operations(
    first: Callable[[], object], second: Callable[[], object],
    *, lock_name: str, table: str, initial_ids: set[int],
) -> tuple[Outcome, Outcome]:
    """Hold one real lock until the observer proves that its peer is blocked."""
    observer_pid = database_identity()
    held = Event()
    release = Event()
    ready = [Event(), Event()]
    worker_state = local()
    pids: dict[int, int] = {}
    real_lock = getattr(data, lock_name)

    def instrumented_lock(identifier: int) -> Any:
        result = real_lock(identifier)
        if worker_state.index == 0:
            held.set()
            assert release.wait(WAIT_SECONDS), "Observer did not release leader."
        return result

    def worker(index: int, operation: Callable[[], object]) -> Outcome:
        worker_state.index = index
        # Django's connections are thread-local; never pass the main wrapper.
        worker_connection = connections["default"]
        try:
            pid = database_identity()
            pids[index] = pid
            with worker_connection.cursor() as cursor:
                cursor.execute("SET lock_timeout = '10s'")
                cursor.execute("SET statement_timeout = '12s'")
            assert set(Booking.objects.values_list("pk", flat=True)) == initial_ids
            ready[index].set()
            try:
                result = operation()
                return Outcome(pid, result, None)
            except BookingError as refusal:
                return Outcome(pid, None, refusal)
        finally:
            worker_connection.close()

    futures: list[Future[Outcome]] = []
    with patch.object(data, lock_name, side_effect=instrumented_lock):
        with ThreadPoolExecutor(max_workers=2) as executor:
            try:
                futures.append(executor.submit(worker, 0, first))
                assert held.wait(WAIT_SECONDS), "Leader did not acquire lock."
                futures.append(executor.submit(worker, 1, second))
                assert ready[1].wait(WAIT_SECONDS), "Peer did not connect."
                assert len({observer_pid, pids[0], pids[1]}) == 3
                wait_for_blocker(pids[1], pids[0], table)
            finally:
                # Release even when an assertion fails. SQL and event waits are
                # bounded, and every future's exception is retrieved below.
                release.set()
                done, pending = wait(futures, timeout=WAIT_SECONDS)
                errors = [future.exception() for future in done]
                assert not pending, "A worker did not finish within the limit."
                unexpected = [error for error in errors if error is not None]
                if unexpected:
                    raise ExceptionGroup("Unexpected worker failure", unexpected)
            return futures[0].result(), futures[1].result()
