"""AC-10 and AC-11: real PostgreSQL waits between state changes and bookings."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from queue import Queue
from threading import Event

import pytest
from django.db import connections

from src.data.models import Booking, Laboratory, User, Workstation
from src.services.access import Actor
from src.services.booking_creation import (
    BookingError, CreatedBooking, WorkstationUnavailable, create_booking,
)
from src.services.staff_catalogue import set_workstation_state
from tests.concurrency_helpers import (
    WAIT_SECONDS, Outcome, database_identity, wait_for_blocker,
)


NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)
OCCUPIED_START = NOW + timedelta(hours=1)
FREE_START = OCCUPIED_START + timedelta(hours=1)


def run_with_workstation_lock_wait(
    first: Callable[[], object], second: Callable[[], object],
) -> tuple[Outcome, Outcome]:
    """Pause after the leader's row lock and observe the follower wait."""
    observer_pid = database_identity()
    lock_held = Event()
    release_lock = Event()
    first_pid_queue: Queue[int] = Queue()
    second_pid_queue: Queue[int] = Queue()

    def pause_after_lock(
        execute: Callable[..., object], sql: str, params: object,
        many: bool, context: object,
    ) -> object:
        result = execute(sql, params, many, context)
        if "FOR UPDATE" in sql and '"data_workstation"' in sql:
            lock_held.set()
            assert release_lock.wait(WAIT_SECONDS), "Observer did not release."
        return result

    def worker(
        operation: Callable[[], object], pid_queue: Queue[int],
        *, leader: bool,
    ) -> Outcome:
        # Each thread owns its Django connection. The observer keeps its own.
        worker_connection = connections["default"]
        try:
            pid = database_identity()
            with worker_connection.cursor() as cursor:
                cursor.execute("SET lock_timeout = '10s'")
                cursor.execute("SET statement_timeout = '12s'")
            pid_queue.put(pid)
            instrument = (
                worker_connection.execute_wrapper(pause_after_lock)
                if leader else nullcontext()
            )
            try:
                with instrument:
                    result = operation()
            except BookingError as refusal:
                return Outcome(pid, None, refusal)
            return Outcome(pid, result, None)
        finally:
            worker_connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        leader = executor.submit(worker, first, first_pid_queue, leader=True)
        try:
            holder_pid = first_pid_queue.get(timeout=WAIT_SECONDS)
            assert lock_held.wait(WAIT_SECONDS), "Leader did not lock the row."
            follower = executor.submit(
                worker, second, second_pid_queue, leader=False,
            )
            blocked_pid = second_pid_queue.get(timeout=WAIT_SECONDS)
            assert len({observer_pid, holder_pid, blocked_pid}) == 3
            wait_for_blocker(blocked_pid, holder_pid, "data_workstation")
        finally:
            release_lock.set()
        return (
            leader.result(timeout=WAIT_SECONDS),
            follower.result(timeout=WAIT_SECONDS),
        )


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "disable_first", [True, False],
    ids=["AC-10-AC-11-disable-first", "AC-10-AC-11-book-first"],
)
def test_state_change_and_booking_share_workstation_lock(
    disable_first: bool,
) -> None:
    database_identity()
    staff = User.objects.create_user(
        "state-staff@tests.example", role=User.Role.PERSONNEL,
    )
    student = User.objects.create_user("state-student@tests.example")
    staff_actor = Actor(staff.pk, staff.email, staff.role, True)
    student_actor = Actor(student.pk, student.email, student.role, True)
    lab = Laboratory.objects.create(name="Workstation state concurrency")
    station = Workstation.objects.create(laboratory=lab, name="Poste A")
    booking = Booking.objects.create(
        owner=student, workstation=station, starts_at=OCCUPIED_START,
        ends_at=FREE_START,
    )
    original = Booking.objects.values().get(pk=booking.pk)

    def disable() -> object:
        return set_workstation_state(staff_actor, lab.pk, station.pk, False)

    def book() -> CreatedBooking:
        return create_booking(
            student_actor, station.pk, FREE_START,
            FREE_START + timedelta(hours=1),
            clock=lambda: NOW,
        )

    first, second = run_with_workstation_lock_wait(
        disable if disable_first else book, book if disable_first else disable,
    )
    change, creation = (first, second) if disable_first else (second, first)
    assert change.refusal is None
    assert change.result == {
        "id": station.pk, "laboratory_id": lab.pk, "is_operational": False,
    }
    station.refresh_from_db()
    assert station.is_operational is False
    assert Booking.objects.values().get(pk=booking.pk) == original

    if disable_first:
        assert type(creation.refusal) is WorkstationUnavailable
        assert creation.result is None
        assert Booking.objects.count() == 1
    else:
        assert creation.refusal is None
        assert isinstance(creation.result, CreatedBooking)
        new_booking = Booking.objects.get(pk=creation.result.booking_id)
        assert new_booking.owner_id == student.pk
        assert new_booking.workstation_id == station.pk
        assert new_booking.starts_at == FREE_START
        assert new_booking.ends_at == FREE_START + timedelta(hours=1)
        assert new_booking.cancelled_at is None
        assert Booking.objects.count() == 2
