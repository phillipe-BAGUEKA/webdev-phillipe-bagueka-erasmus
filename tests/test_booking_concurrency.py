"""Real PostgreSQL wait chains through the public creation service only."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from src.data.models import Booking, Laboratory, User, Workstation
from src.services.access import Actor
from src.services.booking_creation import (
    CreatedBooking,
    PersonalConflict,
    QuotaExceeded,
    WorkstationConflict,
    create_booking,
)

from tests.concurrency_helpers import (
    Outcome, database_identity, run_locked_operations,
)

pytestmark = pytest.mark.django_db(transaction=True)
NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)
START = NOW + timedelta(hours=2)


@dataclass(frozen=True)
class Request:
    actor: Actor
    workstation_id: int
    starts_at: datetime


def run_competing_requests(
    first: Request, second: Request, *, lock_name: str, table: str,
    initial_ids: set[int],
) -> tuple[Outcome, Outcome]:
    def operation(request: Request) -> CreatedBooking:
        assert User.objects.filter(pk=request.actor.user_id).exists()
        assert Workstation.objects.filter(pk=request.workstation_id).exists()
        return create_booking(
            request.actor, request.workstation_id, request.starts_at,
            request.starts_at + timedelta(hours=1), clock=lambda: NOW,
        )

    return run_locked_operations(
        lambda: operation(first), lambda: operation(second),
        lock_name=lock_name, table=table, initial_ids=initial_ids,
    )


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
