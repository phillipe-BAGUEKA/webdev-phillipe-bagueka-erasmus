"""Owner-only cancellation on isolated PostgreSQL, with controlled clocks."""

from datetime import date, datetime, timedelta, timezone
from importlib import import_module
from types import ModuleType
from typing import Any
from unittest.mock import patch

import pytest
from django.db import connection

from src.data.models import Booking, Laboratory, User, Workstation
from src.services.access import Actor, AuthenticationRequired
from src.services.booking_creation import QuotaExceeded, create_booking
from src.services.booking_reads import (
    list_available_slots,
    list_personal_bookings,
)

NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)
START = NOW + timedelta(hours=2)
World = tuple[User, User, Actor, Workstation, Booking]


@pytest.fixture
def world(db: None) -> World:
    assert connection.vendor == "postgresql"
    owner = User.objects.create_user("cancel-owner@tests.example")
    other = User.objects.create_user("cancel-other@tests.example")
    lab = Laboratory.objects.create(name="Cancellation isolated tests")
    station = Workstation.objects.create(laboratory=lab, name="A")
    booking = Booking.objects.create(
        owner=owner, workstation=station, starts_at=START,
        ends_at=START + timedelta(hours=1),
    )
    return owner, other, Actor(owner.pk, owner.email, owner.role, True), station, booking


def service() -> ModuleType:
    return import_module("src.services.booking_cancellation")


def snapshot() -> tuple[list[dict[str, Any]], ...]:
    return tuple(list(model.objects.order_by("pk").values())
                 for model in (User, Laboratory, Workstation, Booking))


def cancel(world: World, **changes: Any) -> Any:
    _, _, actor, _, booking = world
    arguments = dict(actor=actor, booking_id=booking.pk, clock=lambda: NOW)
    arguments.update(changes)
    return service().cancel_booking(**arguments)


@pytest.mark.parametrize("case", ["anonymous", "inactive", "other", "cancelled-other", "missing"],
                         ids=["AC-25-anonymous", "AC-25-inactive", "AC-27-other",
                              "AC-27-already-cancelled", "AC-25-missing"])
def test_refusals_leave_all_business_rows_unchanged(world: World, case: str) -> None:
    owner, other, _, _, booking = world
    changes = {}
    error = AuthenticationRequired
    if case == "anonymous":
        changes["actor"] = None
    elif case == "inactive":
        owner.is_active = False
        owner.save()
    elif case in ("other", "cancelled-other"):
        changes["actor"] = Actor(other.pk, other.email, other.role, True)
        if case == "cancelled-other":
            booking.cancelled_at = NOW
            booking.save()
        error = service().NotBookingOwner
    else:
        changes["booking_id"] = booking.pk + 1000
        error = service().BookingNotFound
    before = snapshot()
    with pytest.raises(error):
        cancel(world, **changes)
    assert snapshot() == before


@pytest.mark.parametrize("offset", [0, 1], ids=["AC-26-exact-start", "AC-26-after-start"])
def test_first_cancellation_at_or_after_start_is_refused(world: World, offset: int) -> None:
    before = snapshot()
    with pytest.raises(service().CancellationTooLate):
        cancel(world, clock=lambda: START + timedelta(seconds=offset))
    assert snapshot() == before


@pytest.mark.parametrize("offline", [False, True],
                         ids=["AC-25-AC-28-online", "AC-25-AC-28-offline"])
def test_valid_cancellation_keeps_row_and_history(world: World, offline: bool) -> None:
    owner, _, actor, station, booking = world
    station.is_operational = not offline
    station.save()
    initial = Booking.objects.values().get(pk=booking.pk)
    instant = START - timedelta(microseconds=1)
    result = cancel(world, clock=lambda: instant)
    assert Booking.objects.count() == 1
    expected = dict(initial, cancelled_at=instant)
    assert Booking.objects.values().get(pk=booking.pk) == expected
    assert (result.booking_id, result.owner_id, result.cancelled_at) == (
        booking.pk, owner.pk, instant,
    )
    history = list_personal_bookings(actor, now=START + timedelta(hours=2))
    assert len(history) == 1
    assert history[0].status == "cancelled"
    assert history[0].cancelled_at == instant
    assert history[0].is_operational == (not offline)
    slots = list_available_slots(
        actor, station.laboratory_id, date(2030, 1, 7), now=instant,
    )
    assert any(slot.starts_at == START for slot in slots) == (not offline)


@pytest.mark.parametrize("criterion", ["AC-25-AC-28-idempotent"], ids=str)
def test_repeat_after_start_preserves_timestamp_and_does_not_read_clock(
    world: World, criterion: str,
) -> None:
    first = cancel(world)
    before = snapshot()
    with patch("src.services.booking_cancellation.django_timezone.now") as clock:
        repeated = cancel(world, clock=None)
    clock.assert_not_called()
    assert repeated == first
    assert snapshot() == before
    repeated = cancel(world, clock=lambda: START + timedelta(days=10))
    assert repeated == first
    assert snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-20-AC-21-AC-25-release"], ids=str)
def test_cancellation_releases_quota_and_slot_through_existing_services(
    world: World, criterion: str,
) -> None:
    owner, other, actor, station, booking = world
    for hours in (2, 4):
        start = START + timedelta(hours=hours)
        Booking.objects.create(owner=owner, workstation=station,
                               starts_at=start, ends_at=start + timedelta(hours=1))
    other_actor = Actor(other.pk, other.email, other.role, True)
    day = date(2030, 1, 7)
    assert list_available_slots(actor, station.laboratory_id, day, now=NOW) == []
    assert not any(slot.starts_at == START for slot in list_available_slots(
        other_actor, station.laboratory_id, day, now=NOW,
    ))
    with pytest.raises(QuotaExceeded):
        create_booking(actor, station.pk, START + timedelta(hours=1),
                       START + timedelta(hours=2), clock=lambda: NOW)
    cancel(world)
    for caller in (actor, other_actor):
        assert any(slot.starts_at == START for slot in list_available_slots(
            caller, station.laboratory_id, day, now=NOW,
        ))
    replacement = create_booking(actor, station.pk, START,
                                 START + timedelta(hours=1), clock=lambda: NOW)
    assert replacement.booking_id != booking.pk
    assert Booking.objects.filter(cancelled_at__isnull=True).count() == 3
    assert Booking.objects.count() == 4


@pytest.mark.parametrize("value", [0, -1, True, "1", None],
                         ids=[f"AC-25-invalid-id-{n}" for n in range(5)])
def test_invalid_booking_id(world: World, value: Any) -> None:
    before = snapshot()
    with pytest.raises(service().InvalidBookingInput):
        cancel(world, booking_id=value)
    assert snapshot() == before


@pytest.mark.parametrize("value", [datetime(2030, 1, 7), "invalid"],
                         ids=["AC-25-naive-clock", "AC-25-invalid-clock"])
def test_invalid_clock(world: World, value: Any) -> None:
    before = snapshot()
    with pytest.raises(service().InvalidBookingInput):
        cancel(world, clock=lambda: value)
    assert snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-25-default-clock-owner-role"], ids=str)
def test_default_clock_and_owner_whose_role_changed(world: World, criterion: str) -> None:
    owner, _, _, _, _ = world
    owner.role = "personnel"
    owner.save()
    with patch("src.services.booking_cancellation.django_timezone.now", return_value=NOW):
        assert cancel(world, clock=None).cancelled_at == NOW


@pytest.mark.parametrize("case", ["actor-inactive", "missing-user", "inactive-repeat"],
                         ids=["AC-25-inactive-actor", "AC-25-deleted-user",
                              "AC-25-inactive-repeat"])
def test_authentication_precedes_idempotence(world: World, case: str) -> None:
    from src.data import booking_creation as locks

    owner, _, actor, _, _ = world
    changes = {}
    if case == "inactive-repeat":
        cancel(world)
        owner.is_active = False
        owner.save()
    elif case == "actor-inactive":
        changes["actor"] = Actor(actor.user_id, actor.email, actor.role, False)
    before = snapshot()
    if case == "missing-user":
        # A missing account cannot coexist with its PROTECT booking in real
        # data; emulate this stale trusted adapter response without dropping FK.
        with patch.object(locks, "lock_actor", return_value=None):
            with pytest.raises(AuthenticationRequired):
                cancel(world)
    else:
        with pytest.raises(AuthenticationRequired):
            cancel(world, **changes)
    assert snapshot() == before


@pytest.mark.parametrize("change", ["deleted", "owner", "station"],
                         ids=["AC-25-stale-hint-deleted", "AC-27-stale-owner",
                              "AC-25-stale-station"])
def test_preliminary_lookup_is_not_authoritative(world: World, change: str) -> None:
    from src.data import booking_cancellation as data

    _, other, _, station, booking = world
    second = Workstation.objects.create(laboratory=station.laboratory, name="B")
    lookup = data.workstation_hint

    def changed_hint(booking_id: int) -> int:
        hint = lookup(booking_id)
        if change == "deleted":
            Booking.objects.filter(pk=booking_id).delete()
        elif change == "owner":
            Booking.objects.filter(pk=booking_id).update(owner=other)
        else:
            Booking.objects.filter(pk=booking_id).update(workstation=second)
        return hint

    error = {"deleted": service().BookingNotFound,
             "owner": service().NotBookingOwner,
             "station": service().BookingChanged}[change]
    before = snapshot()
    with patch.object(data, "workstation_hint", side_effect=changed_hint):
        with pytest.raises(error):
            cancel(world)
    # The injected change is in the same transaction and must roll back too.
    assert snapshot() == before
    assert Booking.objects.get(pk=booking.pk).cancelled_at is None


@pytest.mark.parametrize("criterion", ["AC-26-clock-after-all-locks"], ids=str)
def test_clock_is_read_after_all_three_locks(world: World, criterion: str) -> None:
    from src.data import booking_cancellation as data
    from src.data import booking_creation as locks

    events = []
    user_lock = locks.lock_actor
    post_lock = locks.lock_workstation
    booking_lock = data.lock_booking

    def lock_user(identifier: int) -> Any:
        events.append("user")
        return user_lock(identifier)

    def lock_station(identifier: int) -> Any:
        events.append("station")
        return post_lock(identifier)

    def lock_booking(identifier: int) -> Any:
        events.append("booking")
        return booking_lock(identifier)

    def clock() -> datetime:
        events.append("clock")
        return START

    before = snapshot()
    with patch.object(locks, "lock_actor", side_effect=lock_user), patch.object(
        locks, "lock_workstation", side_effect=lock_station,
    ), patch.object(data, "lock_booking", side_effect=lock_booking):
        with pytest.raises(service().CancellationTooLate):
            cancel(world, clock=clock)
    assert events == ["user", "station", "booking", "clock"]
    assert snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-25-write-failure-rollback"], ids=str)
def test_unrelated_write_error_rolls_back(world: World, criterion: str) -> None:
    from src.data import booking_cancellation as data

    update = data.mark_cancelled

    def failure(booking_id: int, instant: datetime) -> None:
        update(booking_id, instant)
        raise RuntimeError("Simulated infrastructure failure")

    before = snapshot()
    with patch.object(data, "mark_cancelled", side_effect=failure):
        with pytest.raises(RuntimeError):
            cancel(world)
    assert snapshot() == before
