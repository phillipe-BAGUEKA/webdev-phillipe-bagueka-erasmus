"""Direct PostgreSQL read contracts, with fixed clocks and isolated rows."""

from datetime import date, datetime, timedelta, timezone
from importlib import import_module
from types import ModuleType

import pytest
from django.db import connection

from src.data.models import Booking, Laboratory, User, Workstation
from src.services.access import Actor, AuthenticationRequired

World = tuple[Laboratory, Workstation, Workstation, User, User, Actor]


@pytest.fixture
def world(db: None) -> World:
    assert connection.vendor == "postgresql"
    lab = Laboratory.objects.create(name="Read tests")
    station = Workstation.objects.create(laboratory=lab, name="A")
    other_station = Workstation.objects.create(laboratory=lab, name="B")
    user = User.objects.create_user("reader@tests.example")
    other = User.objects.create_user("other-reader@tests.example")
    actor = Actor(user.pk, user.email, user.role, True)
    return lab, station, other_station, user, other, actor


def service() -> ModuleType:
    # Import in the test so the initial red run reports the missing service.
    return import_module("src.services.booking_reads")


def book(
    user: User, station: Workstation, hour: int, day: int = 7,
    *, cancelled_at: datetime | None = None,
) -> Booking:
    start = datetime(2030, 1, day, hour, tzinfo=timezone.utc)
    return Booking.objects.create(
        owner=user, workstation=station, starts_at=start,
        ends_at=start + timedelta(hours=1), cancelled_at=cancelled_at,
    )


NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)


@pytest.mark.parametrize("day,first", [
    (date(2030, 1, 7), 6), (date(2030, 7, 8), 5),
], ids=["AC-13-AC-14-winter", "AC-13-AC-14-summer"])
def test_slots_use_sofia_hours_and_utc(world: World, day: date, first: int) -> None:
    lab, _, _, _, _, actor = world
    slots = service().list_available_slots(actor, lab.pk, day, now=NOW)
    assert len(slots) == 20
    assert min(s.starts_at.hour for s in slots) == first
    assert max(s.ends_at.hour for s in slots) == first + 10
    assert all(s.starts_at.utcoffset() == timedelta(0) for s in slots)
    assert all(s.ends_at - s.starts_at == timedelta(hours=1) for s in slots)


@pytest.mark.parametrize("day", [date(2030, 1, 5), date(2030, 1, 6)], ids=["AC-13-sat", "AC-13-sun"])
def test_weekend_has_no_slots(world: World, day: date) -> None:
    lab, _, _, _, _, actor = world
    assert service().list_available_slots(actor, lab.pk, day, now=NOW) == []


@pytest.mark.parametrize("hour,count", [(6, 18), (16, 0)], ids=["AC-13-at-start", "AC-13-after-last"])
def test_start_must_be_strictly_future(world: World, hour: int, count: int) -> None:
    lab, _, _, _, _, actor = world
    now = NOW.replace(hour=hour)
    slots = service().list_available_slots(actor, lab.pk, date(2030, 1, 7), now=now)
    assert len(slots) == count
    assert all(slot.starts_at > now for slot in slots)


@pytest.mark.parametrize("criterion", ["AC-11-AC-17-AC-19-AC-25-read"], ids=str)
def test_station_state_occupancy_cancellation_and_adjacency(world: World, criterion: str) -> None:
    lab, station, second, user, other, actor = world
    second.is_operational = False
    second.save()
    occupied = book(other, station, 7)
    slots = service().list_available_slots(actor, lab.pk, date(2030, 1, 7), now=NOW)
    assert all(s.workstation_id == station.pk for s in slots)
    assert {s.starts_at.hour for s in slots} == {6, 8, 9, 10, 11, 12, 13, 14, 15}
    occupied.cancelled_at = NOW
    occupied.save()
    assert len(service().list_available_slots(actor, lab.pk, date(2030, 1, 7), now=NOW)) == 10


@pytest.mark.parametrize("criterion", ["AC-18-read"], ids=str)
def test_personal_conflict_applies_across_laboratories(world: World, criterion: str) -> None:
    lab, _, _, user, _, actor = world
    elsewhere = Laboratory.objects.create(name="Elsewhere")
    post = Workstation.objects.create(laboratory=elsewhere, name="Elsewhere")
    book(user, post, 7)
    slots = service().list_available_slots(actor, lab.pk, date(2030, 1, 7), now=NOW)
    assert len(slots) == 18
    assert all(s.starts_at.hour != 7 for s in slots)


@pytest.mark.parametrize("criterion", ["AC-20-AC-21-read"], ids=str)
def test_quota_counts_future_offline_post_but_not_cancelled_or_current(world: World, criterion: str) -> None:
    lab, station, second, user, _, actor = world
    second.is_operational = False
    second.save()
    book(user, second, 8, day=8)
    book(user, second, 9, day=8)
    book(user, second, 5)  # at start: does not consume future quota
    book(user, second, 3)  # past
    book(user, second, 10, day=8, cancelled_at=NOW)
    assert len(service().list_available_slots(actor, lab.pk, date(2030, 1, 7), now=NOW)) == 10
    third = book(user, second, 11, day=8)
    assert service().list_available_slots(actor, lab.pk, date(2030, 1, 7), now=NOW) == []
    third.cancelled_at = NOW
    third.save()
    assert len(service().list_available_slots(actor, lab.pk, date(2030, 1, 7), now=NOW)) == 10


@pytest.mark.parametrize("criterion", ["AC-28-read"], ids=str)
def test_personal_history_has_all_states_order_and_no_foreign_rows(world: World, criterion: str) -> None:
    _, station, second, user, other, actor = world
    past = book(user, station, 3)
    current = book(user, station, 5)
    future = book(user, station, 8)
    cancelled = book(user, station, 8, cancelled_at=NOW)
    book(other, second, 9)
    station.is_operational = False
    station.save()
    rows = service().list_personal_bookings(actor, now=NOW)
    assert [r.booking_id for r in rows] == [cancelled.pk, future.pk, current.pk, past.pk]
    assert [r.status for r in rows] == ["cancelled", "future", "in_progress", "past"]
    assert all(not r.is_operational for r in rows)


@pytest.mark.parametrize("actor", [None, Actor(1, "inactive@tests.example", "student", False)])
def test_unauthenticated_reads_are_refused(actor: Actor | None) -> None:
    with pytest.raises(AuthenticationRequired):
        service().list_available_slots(actor, 1, date(2030, 1, 7), now=NOW)
    with pytest.raises(AuthenticationRequired):
        service().list_personal_bookings(actor, now=NOW)


def test_consultations_never_mutate_rows(world: World) -> None:
    lab, station, _, user, _, actor = world
    book(user, station, 8)
    models = (Laboratory, Workstation, User, Booking)
    before = [list(model.objects.order_by("pk").values()) for model in models]
    service().list_available_slots(actor, lab.pk, date(2030, 1, 7), now=NOW)
    service().list_personal_bookings(actor, now=NOW)
    assert [list(model.objects.order_by("pk").values()) for model in models] == before


def test_empty_history_empty_lab_staff_and_missing_lab(world: World) -> None:
    lab, _, _, _, _, actor = world
    assert service().list_personal_bookings(actor, now=NOW) == []
    empty = Laboratory.objects.create(name="Empty")
    assert service().list_available_slots(actor, empty.pk, date(2030, 1, 7), now=NOW) == []
    staff = Actor(actor.user_id, actor.email, "personnel", True)
    assert service().list_available_slots(staff, lab.pk, date(2030, 1, 7), now=NOW) == []
    with pytest.raises(service().LaboratoryNotFound):
        service().list_available_slots(actor, 999999, date(2030, 1, 7), now=NOW)


@pytest.mark.parametrize("instant", [datetime(2030, 1, 7), "invalid"])
def test_clock_must_be_an_aware_datetime(world: World, instant: object) -> None:
    lab, _, _, _, _, actor = world
    with pytest.raises(service().InvalidReadInput):
        service().list_available_slots(actor, lab.pk, date(2030, 1, 7), now=instant)
    with pytest.raises(service().InvalidReadInput):
        service().list_personal_bookings(actor, now=instant)


@pytest.mark.parametrize("lab_id,day", [(0, date(2030, 1, 7)), (True, date(2030, 1, 7)), (1, "2030-01-07"), (1, NOW)])
def test_invalid_read_inputs_are_domain_errors(world: World, lab_id, day) -> None:
    *_, actor = world
    with pytest.raises(service().InvalidReadInput):
        service().list_available_slots(actor, lab_id, day, now=NOW)


def test_default_clock_is_controllable_and_history_cannot_choose_an_owner(
    world: World, monkeypatch: pytest.MonkeyPatch,
) -> None:
    lab, station, second, user, other, actor = world
    own = book(user, station, 8)
    # Foreign history remains detectable without occupying today's availability.
    book(other, second, 9, day=8)
    monkeypatch.setattr(service().django_timezone, "now", lambda: NOW)
    assert len(service().list_available_slots(actor, lab.pk, date(2030, 1, 7))) == 18
    assert [row.booking_id for row in service().list_personal_bookings(actor)] == [own.pk]
    with pytest.raises(TypeError):
        service().list_personal_bookings(actor, owner_id=other.pk, now=NOW)
