"""Controlled cancellation/create orders, with server-observed lock waits."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from src.data import booking_cancellation as data
from src.data.models import Booking, Laboratory, User, Workstation
from src.services.access import Actor
from src.services.booking_cancellation import cancel_booking
from src.services.booking_creation import (
    QuotaExceeded, WorkstationConflict, create_booking,
)
from tests.concurrency_helpers import database_identity, run_locked_operations

pytestmark = pytest.mark.django_db(transaction=True)
NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)
START = NOW + timedelta(hours=2)


def prepare() -> tuple[Actor, Actor, Workstation, Workstation, Booking]:
    database_identity()
    owner = User.objects.create_user("concurrent-cancel@tests.example")
    other = User.objects.create_user("concurrent-new@tests.example")
    lab = Laboratory.objects.create(name="Concurrent cancellation tests")
    first = Workstation.objects.create(laboratory=lab, name="A")
    second = Workstation.objects.create(laboratory=lab, name="B")
    booking = Booking.objects.create(
        owner=owner, workstation=first, starts_at=START,
        ends_at=START + timedelta(hours=1),
    )
    return (Actor(owner.pk, owner.email, owner.role, True),
            Actor(other.pk, other.email, other.role, True),
            first, second, booking)


@pytest.mark.parametrize("criterion", ["AC-25-double-cancellation"], ids=str)
def test_two_cancellations_make_one_transition(criterion: str) -> None:
    actor, _, _, _, booking = prepare()
    before = Booking.objects.values().get(pk=booking.pk)
    with patch.object(data, "mark_cancelled", wraps=data.mark_cancelled) as update:
        first, second = run_locked_operations(
            lambda: cancel_booking(actor, booking.pk, clock=lambda: NOW),
            lambda: cancel_booking(actor, booking.pk,
                                   clock=lambda: NOW + timedelta(minutes=1)),
            lock_name="lock_actor", table="data_user", initial_ids={booking.pk},
        )
    assert first.result is not None and first.result == second.result
    assert first.refusal is None and second.refusal is None
    assert update.call_count == 1
    assert Booking.objects.count() == 1
    assert Booking.objects.values().get(pk=booking.pk) == dict(before, cancelled_at=NOW)
    print(f"double cancel: PIDs {first.pid}/{second.pid}, one UPDATE, timestamp={NOW}")


@pytest.mark.parametrize("cancel_first", [True, False],
                         ids=["AC-20-AC-25-cancel-before-create",
                              "AC-20-AC-25-create-before-cancel"])
def test_quota_cancellation_and_creation_order(cancel_first: bool) -> None:
    actor, _, station, second_station, booking = prepare()
    for hour in (9, 11):
        start = START.replace(hour=hour)
        Booking.objects.create(
            owner_id=actor.user_id, workstation=station, starts_at=start,
            ends_at=start + timedelta(hours=1),
        )
    initial = list(Booking.objects.order_by("pk").values())

    def cancel() -> object:
        return cancel_booking(actor, booking.pk, clock=lambda: NOW)

    def create() -> object:
        return create_booking(actor, second_station.pk,
                              START + timedelta(hours=1),
                              START + timedelta(hours=2), clock=lambda: NOW)

    outcomes = run_locked_operations(
        cancel if cancel_first else create,
        create if cancel_first else cancel,
        lock_name="lock_actor", table="data_user",
        initial_ids={row["id"] for row in initial},
    )
    cancellation = outcomes[0] if cancel_first else outcomes[1]
    creation = outcomes[1] if cancel_first else outcomes[0]
    assert cancellation.result is not None and cancellation.refusal is None
    if cancel_first:
        assert creation.result is not None and creation.refusal is None
    else:
        assert creation.result is None and type(creation.refusal) is QuotaExceeded
    assert Booking.objects.count() == (4 if cancel_first else 3)
    assert Booking.objects.filter(cancelled_at__isnull=True).count() == (
        3 if cancel_first else 2
    )
    initial[0]["cancelled_at"] = NOW
    assert list(Booking.objects.filter(pk__in=[row["id"] for row in initial])
                .order_by("pk").values()) == initial
    print(f"quota cancel_first={cancel_first}: PIDs {outcomes[0].pid}/{outcomes[1].pid}; "
          f"total={Booking.objects.count()}, active={Booking.objects.filter(cancelled_at=None).count()}")


@pytest.mark.parametrize("cancel_first", [True, False],
                         ids=["AC-17-AC-25-cancel-before-create",
                              "AC-17-AC-25-create-before-cancel"])
def test_slot_cancellation_and_creation_order(cancel_first: bool) -> None:
    actor, other, station, _, booking = prepare()

    def cancel() -> object:
        return cancel_booking(actor, booking.pk, clock=lambda: NOW)

    def create() -> object:
        return create_booking(other, station.pk, START,
                              START + timedelta(hours=1), clock=lambda: NOW)

    outcomes = run_locked_operations(
        cancel if cancel_first else create,
        create if cancel_first else cancel,
        lock_name="lock_workstation", table="data_workstation",
        initial_ids={booking.pk},
    )
    cancellation = outcomes[0] if cancel_first else outcomes[1]
    creation = outcomes[1] if cancel_first else outcomes[0]
    assert cancellation.result is not None and cancellation.refusal is None
    if cancel_first:
        assert creation.result is not None and creation.refusal is None
        row = Booking.objects.get(pk=creation.result.booking_id)
        assert row.owner_id == other.user_id
        assert row.starts_at == START
    else:
        assert creation.result is None and type(creation.refusal) is WorkstationConflict
    booking.refresh_from_db()
    assert booking.cancelled_at == NOW
    assert Booking.objects.count() == (2 if cancel_first else 1)
    assert Booking.objects.filter(cancelled_at=None).count() == (1 if cancel_first else 0)
    print(f"slot cancel_first={cancel_first}: PIDs {outcomes[0].pid}/{outcomes[1].pid}; "
          f"total={Booking.objects.count()}, active={Booking.objects.filter(cancelled_at=None).count()}")
