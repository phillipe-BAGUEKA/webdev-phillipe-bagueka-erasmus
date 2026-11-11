"""Real PostgreSQL wait chains through the public creation service only."""

from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Event, local
from time import monotonic
from typing import Any
from unittest.mock import patch

import pytest
from django.db import connection, connections

from src.data import booking_creation as data
from src.data.models import Booking, Laboratory, User, Workstation
from src.services.access import Actor
from src.services.booking_creation import (
    BookingError,
    CreatedBooking,
    PersonalConflict,
    QuotaExceeded,
    WorkstationConflict,
    create_booking,
)

pytestmark = pytest.mark.django_db(transaction=True)
NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)
START = NOW + timedelta(hours=2)
WAIT_SECONDS = 15


@dataclass(frozen=True)
class Request:
    actor: Actor
    workstation_id: int
    starts_at: datetime


@dataclass(frozen=True)
class Outcome:
    pid: int
    result: CreatedBooking | None
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


def run_competing_requests(
    first: Request, second: Request, *, lock_name: str, table: str,
    initial_ids: set[int],
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

    def worker(index: int, request: Request) -> Outcome:
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
            assert User.objects.filter(pk=request.actor.user_id).exists()
            assert Workstation.objects.filter(pk=request.workstation_id).exists()
            ready[index].set()
            try:
                result = create_booking(
                    request.actor, request.workstation_id, request.starts_at,
                    request.starts_at + timedelta(hours=1), clock=lambda: NOW,
                )
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


@pytest.mark.parametrize("scenario", ["station", "personal", "quota"],
                         ids=["AC-22", "AC-23", "AC-24"])
def test_concurrent_creation(scenario: str) -> None:
    database_identity()
    student = User.objects.create_user("concurrent@tests.example")
    other = User.objects.create_user("other-concurrent@tests.example")
    actor = Actor(student.pk, student.email, student.role, True)
    other_actor = Actor(other.pk, other.email, other.role, True)
    lab = Laboratory.objects.create(name="Concurrent isolated laboratory")
    station = Workstation.objects.create(laboratory=lab, name="A")
    second_station = Workstation.objects.create(laboratory=lab, name="B")
    first = Request(actor, station.pk, START)
    second = Request(other_actor, station.pk, START)
    lock_name, table = "lock_workstation", "data_workstation"
    expected_error = WorkstationConflict
    expected_count = 1
    if scenario != "station":
        second = Request(actor, second_station.pk, START)
        lock_name, table = "lock_actor", "data_user"
        expected_error = PersonalConflict
    if scenario == "quota":
        # Four disjoint intervals: no exclusion can accidentally enforce quota.
        for hour in (10, 12):
            start = START.replace(hour=hour)
            Booking.objects.create(
                owner=student, workstation=station, starts_at=start,
                ends_at=start + timedelta(hours=1),
            )
        second = Request(actor, second_station.pk, START + timedelta(hours=1))
        expected_error = QuotaExceeded
        expected_count = 3
    initial_rows = list(Booking.objects.order_by("pk").values())
    initial_ids = {row["id"] for row in initial_rows}
    outcomes = run_competing_requests(
        first, second, lock_name=lock_name, table=table, initial_ids=initial_ids,
    )
    success, refusal = outcomes
    actual_count = Booking.objects.count()
    print(f"{scenario}: distinct PIDs {success.pid}/{refusal.pid}; "
          f"observed PostgreSQL lock wait; "
          f"results={[(type(item.result).__name__, type(item.refusal).__name__) for item in outcomes]}; "
          f"final bookings={actual_count}")
    assert actual_count == expected_count
    assert success.pid != refusal.pid
    assert success.result is not None and success.refusal is None
    assert refusal.result is None and type(refusal.refusal) is expected_error
    new_rows = list(Booking.objects.exclude(pk__in=initial_ids))
    assert len(new_rows) == 1
    row = new_rows[0]
    assert row.pk == success.result.booking_id
    assert (row.owner_id, row.workstation_id, row.starts_at, row.ends_at) == (
        first.actor.user_id, first.workstation_id, first.starts_at,
        first.starts_at + timedelta(hours=1),
    )
    assert row.cancelled_at is None
    assert row.created_at == NOW
    assert list(Booking.objects.filter(pk__in=initial_ids).order_by("pk").values()) == initial_rows
    assert Booking.objects.filter(
        owner=student, starts_at__gt=NOW, cancelled_at__isnull=True,
    ).count() == expected_count
