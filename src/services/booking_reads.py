"""Non-binding availability and personal history, independent of transport."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from django.utils import timezone as django_timezone

from src.data import booking_reads as data
from .access import Actor, require_authenticated

SOFIA = ZoneInfo("Europe/Sofia")


class InvalidReadInput(ValueError):
    """A calendar date and an aware clock value are required."""


class LaboratoryNotFound(LookupError):
    """The requested laboratory does not exist."""


@dataclass(frozen=True)
class AvailableSlot:
    workstation_id: int
    workstation_name: str
    starts_at: datetime
    ends_at: datetime


@dataclass(frozen=True)
class PersonalBooking:
    booking_id: int
    workstation_id: int
    workstation_name: str
    laboratory_id: int
    laboratory_name: str
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    cancelled_at: datetime | None
    is_operational: bool
    status: str


def _clock(now: datetime | None) -> datetime:
    instant = django_timezone.now() if now is None else now
    if not isinstance(instant, datetime) or instant.utcoffset() is None:
        raise InvalidReadInput("An aware current instant is required.")
    return instant.astimezone(timezone.utc)


def list_available_slots(
    actor: Actor | None, laboratory_id: int, day: date,
    *, now: datetime | None = None,
) -> list[AvailableSlot]:
    """Return UTC slot candidates, ordered by start then workstation ID.

    This read is not a reservation or a transactionally guaranteed offer.
    """
    actor = require_authenticated(actor)
    instant = _clock(now)
    if type(day) is not date or type(laboratory_id) is not int or laboratory_id <= 0:
        raise InvalidReadInput("A calendar date and positive laboratory ID are required.")
    if not data.laboratory_exists(laboratory_id):
        raise LaboratoryNotFound("Laboratory not found.")
    if actor.role != "student" or day.weekday() >= 5:
        return []
    if data.upcoming_count(actor.user_id, instant) >= 3:
        return []
    start = datetime.combine(day, time(8), SOFIA).astimezone(timezone.utc)
    end = datetime.combine(day, time(18), SOFIA).astimezone(timezone.utc)
    occupied = data.occupied_intervals(laboratory_id, start, end)
    personal = data.personal_intervals(actor.user_id, start, end)
    stations = data.workstations(laboratory_id)
    slots = []
    for hour in range(10):
        begins = start + timedelta(hours=hour)
        finishes = begins + timedelta(hours=1)
        if begins <= instant:
            continue
        if any(begins < other_end and other_start < finishes
               for other_start, other_end in personal):
            continue
        for station in stations:
            if not station["is_operational"]:
                continue
            if any(post == station["id"] and begins < other_end and other_start < finishes
                   for post, other_start, other_end in occupied):
                continue
            slots.append(AvailableSlot(station["id"], station["name"], begins, finishes))
    return slots


def list_personal_bookings(
    actor: Actor | None, *, now: datetime | None = None,
) -> list[PersonalBooking]:
    """Return only the actor's history, descending by start then booking ID."""
    actor = require_authenticated(actor)
    instant = _clock(now)
    result = []
    for row in data.personal_bookings(actor.user_id):
        if row["cancelled_at"] is not None:
            status = "cancelled"
        elif row["starts_at"] > instant:
            status = "future"
        elif row["ends_at"] > instant:
            status = "in_progress"
        else:
            status = "past"
        result.append(PersonalBooking(
            booking_id=row["id"], workstation_id=row["workstation_id"],
            workstation_name=row["workstation__name"],
            laboratory_id=row["workstation__laboratory_id"],
            laboratory_name=row["workstation__laboratory__name"],
            starts_at=row["starts_at"].astimezone(timezone.utc),
            ends_at=row["ends_at"].astimezone(timezone.utc),
            created_at=row["created_at"].astimezone(timezone.utc),
            cancelled_at=row["cancelled_at"],
            is_operational=row["workstation__is_operational"], status=status,
        ))
    return result
