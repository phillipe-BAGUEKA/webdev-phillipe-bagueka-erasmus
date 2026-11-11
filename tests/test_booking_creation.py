"""Direct creation tests on isolated PostgreSQL, with a controlled clock."""

from datetime import datetime, timedelta, timezone
from importlib import import_module
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.db import IntegrityError, connection

from src.data.models import Booking, Laboratory, User, Workstation
from src.services.access import Actor, AuthenticationRequired

NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)
START = NOW + timedelta(hours=2)
World = tuple[User, User, Actor, Workstation, Workstation]


@pytest.fixture
def world(db: None) -> World:
    assert connection.vendor == "postgresql"
    user = User.objects.create_user("creator@tests.example")
    other = User.objects.create_user("other-creator@tests.example")
    lab = Laboratory.objects.create(name="Creation tests")
    station = Workstation.objects.create(laboratory=lab, name="A")
    second = Workstation.objects.create(laboratory=lab, name="B")
    return user, other, Actor(user.pk, user.email, user.role, True), station, second


def service() -> ModuleType:
    return import_module("src.services.booking_creation")


def snapshot() -> tuple[list[dict[str, Any]], ...]:
    """Compare all business rows, including fields unrelated to the refusal."""
    return tuple(list(model.objects.order_by("pk").values())
                 for model in (User, Laboratory, Workstation, Booking))


def create(world: World, **changes: Any) -> Any:
    _, _, actor, station, _ = world
    inputs = dict(actor=actor, workstation_id=station.pk, starts_at=START,
                  ends_at=START + timedelta(hours=1), clock=lambda: NOW)
    inputs.update(changes)
    return service().create_booking(**inputs)


def existing(user: User, station: Workstation, start: datetime,
             *, cancelled: bool = False) -> Booking:
    return Booking.objects.create(
        owner=user, workstation=station, starts_at=start,
        ends_at=start + timedelta(hours=1), cancelled_at=NOW if cancelled else None,
    )


@pytest.mark.parametrize("case", ["anonymous", "inactive", "staff", "missing", "offline"],
                         ids=["AC-15-anonymous", "AC-15-inactive", "AC-15-personnel",
                              "AC-15-unknown-post", "AC-11-offline"])
def test_access_and_post_refusals_are_unchanged(world: World, case: str) -> None:
    user, _, actor, station, _ = world
    changes = {}
    expected = service().StudentRequired
    if case == "anonymous":
        changes["actor"] = None
        expected = AuthenticationRequired
    elif case == "inactive":
        user.is_active = False
        user.save()
        expected = AuthenticationRequired
    elif case == "staff":
        user.role = "personnel"
        user.save()
    elif case == "missing":
        changes["workstation_id"] = station.pk + 1000
        expected = service().WorkstationNotFound
    else:
        station.is_operational = False
        station.save()
        expected = service().WorkstationUnavailable
    before = snapshot()
    with pytest.raises(expected):
        create(world, **changes)
    assert snapshot() == before


@pytest.mark.parametrize("start,end", [
    (START.replace(tzinfo=None), START + timedelta(hours=1)),
    (START, START.replace(tzinfo=None)),
    ("2030-01-07", START),
    (START, None),
    (START, START),
    (START, START - timedelta(hours=1)),
    (START, START + timedelta(minutes=30)),
    (START, START + timedelta(hours=2)),
    (START + timedelta(minutes=1), START + timedelta(hours=1, minutes=1)),
    (START + timedelta(seconds=1), START + timedelta(hours=1, seconds=1)),
    (START + timedelta(microseconds=1), START + timedelta(hours=1, microseconds=1)),
    (START.replace(hour=5), START.replace(hour=6)),
    (START.replace(hour=16), START.replace(hour=17)),
    (START.replace(day=5), START.replace(day=5, hour=8)),
    (START.replace(day=6), START.replace(day=6, hour=8)),
], ids=[f"AC-13-AC-16-invalid-{n}" for n in range(15)])
def test_invalid_slots_leave_rows_unchanged(world: World, start: Any, end: Any) -> None:
    before = snapshot()
    with pytest.raises(service().InvalidBookingInput):
        create(world, starts_at=start, ends_at=end)
    assert snapshot() == before


@pytest.mark.parametrize("now", [START, START + timedelta(seconds=1)],
                         ids=["AC-16-exact-start", "AC-16-past"])
def test_start_is_strictly_future(world: World, now: datetime) -> None:
    before = snapshot()
    with pytest.raises(service().SlotNotFuture):
        create(world, clock=lambda: now)
    assert snapshot() == before


@pytest.mark.parametrize("personal,other_lab", [(False, False), (True, False), (True, True)],
                         ids=["AC-17-station", "AC-18-personal", "AC-18-other-lab"])
def test_existing_conflicts(world: World, personal: bool, other_lab: bool) -> None:
    user, other, _, station, second = world
    if other_lab:
        second.laboratory = Laboratory.objects.create(name="Other laboratory")
        second.save()
    existing(user if personal else other, second if personal else station, START)
    before = snapshot()
    error = service().PersonalConflict if personal else service().WorkstationConflict
    with pytest.raises(error):
        create(world)
    assert snapshot() == before


@pytest.mark.parametrize("offline", [False, True], ids=["AC-20-online", "AC-20-offline"])
def test_fourth_future_booking_is_refused(world: World, offline: bool) -> None:
    user, _, _, _, second = world
    for hour in (3, 4, 5):
        existing(user, second, START + timedelta(hours=hour))
    second.is_operational = not offline
    second.save()
    before = snapshot()
    with pytest.raises(service().QuotaExceeded):
        create(world)
    assert snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-15-AC-21"], ids=str)
def test_valid_creation_owner_and_quota_exclusions(world: World, criterion: str) -> None:
    user, _, _, station, second = world
    for offset in (-2, -1, 0, 3, 4):
        existing(user, second, NOW + timedelta(hours=offset))
    existing(user, station, START, cancelled=True)
    count = Booking.objects.count()
    result = create(world)
    assert Booking.objects.count() == count + 1
    row = Booking.objects.get(pk=result.booking_id)
    assert (row.owner_id, row.workstation_id, row.starts_at, row.ends_at) == (
        user.pk, station.pk, START, START + timedelta(hours=1))
    assert row.created_at == NOW
    assert result.owner_id == user.pk
    assert Booking.objects.filter(owner=user, cancelled_at=None, starts_at__gt=NOW).count() == 3


@pytest.mark.parametrize("offset", [-1, 1], ids=["AC-19-before", "AC-19-after"])
def test_consecutive_slots_allowed(world: World, offset: int) -> None:
    user, _, _, station, _ = world
    existing(user, station, START + timedelta(hours=offset))
    create(world)
    assert Booking.objects.count() == 2


@pytest.mark.parametrize("value", [0, -1, True, "1", None],
                         ids=[f"AC-15-invalid-id-{n}" for n in range(5)])
def test_invalid_station_id(world: World, value: Any) -> None:
    before = snapshot()
    with pytest.raises(service().InvalidBookingInput):
        create(world, workstation_id=value)
    assert snapshot() == before


@pytest.mark.parametrize("case", ["missing", "inactive-actor"],
                         ids=["AC-15-deleted-user", "AC-15-inactive-actor"])
def test_missing_user_and_inactive_actor(world: World, case: str) -> None:
    user, _, actor, _, _ = world
    if case == "missing":
        user.delete()
    else:
        actor = Actor(actor.user_id, actor.email, actor.role, False)
    before = snapshot()
    with pytest.raises(AuthenticationRequired):
        create(world, actor=actor)
    assert snapshot() == before


@pytest.mark.parametrize("value", [datetime(2030, 1, 7), "invalid"],
                         ids=["AC-16-naive-clock", "AC-16-invalid-clock"])
def test_invalid_clock(world: World, value: Any) -> None:
    before = snapshot()
    with pytest.raises(service().InvalidBookingInput):
        create(world, clock=lambda: value)
    assert snapshot() == before


@pytest.mark.parametrize("month,day,hour", [(1, 7, 8), (1, 7, 17), (7, 8, 8), (7, 8, 17)],
                         ids=["AC-13-AC-14-winter-first", "AC-13-winter-last",
                              "AC-14-summer-first", "AC-13-summer-last"])
def test_sofia_boundaries_and_utc(world: World, month: int, day: int, hour: int) -> None:
    start = datetime(2030, month, day, hour, tzinfo=ZoneInfo("Europe/Sofia"))
    result = create(world, starts_at=start, ends_at=start + timedelta(hours=1))
    assert result.starts_at == start
    assert result.starts_at.tzinfo == timezone.utc
    assert result.ends_at - result.starts_at == timedelta(hours=1)


@pytest.mark.parametrize("personal", [False, True], ids=["AC-17-partial", "AC-18-partial"])
def test_partial_overlap(world: World, personal: bool) -> None:
    user, other, _, station, second = world
    existing(user if personal else other, second if personal else station,
             START + timedelta(minutes=30))
    before = snapshot()
    error = service().PersonalConflict if personal else service().WorkstationConflict
    with pytest.raises(error):
        create(world)
    assert snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-17-cancelled"], ids=str)
def test_cancelled_foreign_booking_does_not_block(world: World, criterion: str) -> None:
    _, other, _, station, _ = world
    existing(other, station, START, cancelled=True)
    create(world)
    assert Booking.objects.count() == 2


@pytest.mark.parametrize("criterion", ["AC-15-AC-16-clock-after-locks"], ids=str)
def test_lock_order_and_fresh_clock(world: World, criterion: str) -> None:
    from src.data import booking_creation as data

    events = []
    lock_user, lock_station = data.lock_actor, data.lock_workstation

    def actor_lock(user_id: int) -> Any:
        assert connection.in_atomic_block
        events.append("user")
        return lock_user(user_id)

    def station_lock(station_id: int) -> Any:
        events.append("workstation")
        return lock_station(station_id)

    def clock() -> datetime:
        events.append("clock")
        return START

    before = snapshot()
    with patch.object(data, "lock_actor", side_effect=actor_lock), patch.object(
        data, "lock_workstation", side_effect=station_lock,
    ), pytest.raises(service().SlotNotFuture):
        create(world, clock=clock)
    assert events == ["user", "workstation", "clock"]
    assert snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-15-default-clock"], ids=str)
def test_default_clock_and_authoritative_role(world: World, criterion: str) -> None:
    _, _, actor, _, _ = world
    stale_actor = Actor(actor.user_id, actor.email, "personnel", True)
    with patch("src.services.booking_creation.django_timezone.now", return_value=NOW) as clock:
        result = create(world, actor=stale_actor, clock=None)
    clock.assert_called_once_with()
    assert result.owner_id == actor.user_id


@pytest.mark.parametrize("constraint,error", [
    ("booking_positive_interval", "InvalidBookingInput"),
    ("booking_one_hour", "InvalidBookingInput"),
    ("booking_workstation_no_overlap", "WorkstationConflict"),
    ("booking_owner_no_overlap", "PersonalConflict"),
], ids=["AC-16-db-positive", "AC-16-db-hour", "AC-17-db-conflict", "AC-18-db-conflict"])
def test_database_defence_rolls_back_before_translation(
    world: World, constraint: str, error: str,
) -> None:
    from src.data import booking_creation as data

    user, other, _, station, second = world
    insert = data.insert_booking

    def force_constraint(owner: int, post: int, start: datetime,
                         end: datetime, created: datetime) -> int:
        if constraint == "booking_positive_interval":
            # With both checks active, PostgreSQL reports booking_one_hour
            # first for a zero-length interval. Exercise the other named
            # diagnostic separately, without dropping either constraint.
            cause = Exception("Synthetic PostgreSQL diagnostic")
            cause.diag = SimpleNamespace(constraint_name=constraint)
            cause.sqlstate = "23514"
            raise IntegrityError("Synthetic check violation") from cause
        elif constraint == "booking_one_hour":
            end = start + timedelta(hours=2)
        elif constraint == "booking_workstation_no_overlap":
            existing(other, station, START)
        else:
            existing(user, second, START)
        return insert(owner, post, start, end, created)

    before = snapshot()
    with patch.object(data, "insert_booking", side_effect=force_constraint):
        with pytest.raises(getattr(service(), error)) as failure:
            create(world)
    assert str(failure.value.__cause__) == constraint
    # A query here also proves that rollback cleared PostgreSQL's aborted state.
    assert snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-15-unrelated-db-error"], ids=str)
def test_unrelated_database_error_propagates_and_rolls_back(world: World, criterion: str) -> None:
    from src.data import booking_creation as data

    user, _, _, _, _ = world
    insert = data.insert_booking

    def unrelated_failure(*args: Any) -> int:
        insert(*args)
        User.objects.create(email=user.email)
        raise AssertionError("The unique email constraint must reject this insert.")

    before = snapshot()
    with patch.object(data, "insert_booking", side_effect=unrelated_failure):
        with pytest.raises(IntegrityError):
            create(world)
    assert snapshot() == before


@pytest.mark.parametrize("diagnostic", [None, "wrong-state"],
                         ids=["AC-15-unknown-diagnostic", "AC-15-wrong-sqlstate"])
def test_unrecognized_integrity_diagnostic_is_not_a_booking_conflict(
    world: World, diagnostic: str | None,
) -> None:
    from src.data import booking_creation as data

    def failure(*args: Any) -> int:
        if diagnostic is None:
            raise IntegrityError("No PostgreSQL diagnostic")
        cause = Exception("Synthetic diagnostic")
        cause.diag = SimpleNamespace(constraint_name="booking_owner_no_overlap")
        cause.sqlstate = "23505"
        raise IntegrityError("Unexpected SQLSTATE") from cause

    before = snapshot()
    with patch.object(data, "insert_booking", side_effect=failure):
        with pytest.raises(IntegrityError):
            create(world)
    assert snapshot() == before
