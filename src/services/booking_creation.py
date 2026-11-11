"""Student booking creation, independent of HTTP and MCP."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from django.utils import timezone as django_timezone

from src.data import booking_creation as data
from src.data import booking_reads as reads
from .access import Actor, AuthenticationRequired, require_authenticated


class BookingError(Exception):
    """Base for explicit creation refusals; no transport status is assigned here."""


class StudentRequired(BookingError):
    """Only a student may create a booking."""


class WorkstationNotFound(BookingError):
    """The requested workstation does not exist."""


class WorkstationUnavailable(BookingError):
    """The workstation is out of service."""


class InvalidBookingInput(BookingError):
    """The ID, clock or requested interval is not valid."""


class SlotNotFuture(BookingError):
    """The slot has already begun."""


class WorkstationConflict(BookingError):
    """An uncancelled booking overlaps on this workstation."""


class PersonalConflict(BookingError):
    """The student already has an overlapping uncancelled booking."""


class QuotaExceeded(BookingError):
    """The student already holds three future uncancelled bookings."""


@dataclass(frozen=True)
class CreatedBooking:
    booking_id: int
    owner_id: int
    workstation_id: int
    starts_at: datetime
    ends_at: datetime
    created_at: datetime


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise InvalidBookingInput("An aware datetime is required.")
    return value.astimezone(timezone.utc)


def _canonical_slot(start: datetime, end: datetime) -> None:
    local = start.astimezone(ZoneInfo("Europe/Sofia"))
    if (end - start != timedelta(hours=1) or local.weekday() >= 5
            or not 8 <= local.hour < 18
            or (local.minute, local.second, local.microsecond) != (0, 0, 0)):
        raise InvalidBookingInput("Choose a weekday one-hour slot from 08:00 to 18:00 Europe/Sofia.")


def create_booking(
    actor: Actor | None, workstation_id: int, starts_at: datetime, ends_at: datetime,
    *, clock: Callable[[], datetime] | None = None,
) -> CreatedBooking:
    """Create atomically after user -> workstation locks and fresh validation.

    Actor must come from a trusted authenticated adapter, never client JSON.
    The injected clock is invoked only after lock acquisition, not before waits.
    """
    actor = require_authenticated(actor)
    if type(workstation_id) is not int or workstation_id <= 0:
        raise InvalidBookingInput("A positive workstation ID is required.")
    try:
        with data.creation_transaction():
            current_actor = data.lock_actor(actor.user_id)
            if current_actor is None or not current_actor.is_active:
                raise AuthenticationRequired
            station = data.lock_workstation(workstation_id)
            instant = _utc(django_timezone.now() if clock is None else clock())
            if current_actor.role != "student":
                raise StudentRequired("Only students may create bookings.")
            if station is None:
                raise WorkstationNotFound("Workstation not found.")
            if not station.is_operational:
                raise WorkstationUnavailable("The workstation is out of service.")
            start, end = _utc(starts_at), _utc(ends_at)
            _canonical_slot(start, end)
            if start <= instant:
                raise SlotNotFuture("The slot must start strictly in the future.")
            if data.workstation_conflicts(workstation_id, start, end):
                raise WorkstationConflict("This workstation is already booked for that slot.")
            if reads.personal_intervals(current_actor.user_id, start, end):
                raise PersonalConflict("You already have a booking during that slot.")
            if reads.upcoming_count(current_actor.user_id, instant) >= 3:
                raise QuotaExceeded("You already have three future bookings.")
            booking_id = data.insert_booking(
                current_actor.user_id, workstation_id, start, end, instant,
            )
            return CreatedBooking(
                booking_id, current_actor.user_id, workstation_id, start, end, instant,
            )
    except data.ConstraintViolation as error:
        refusal = {
            "booking_positive_interval": InvalidBookingInput,
            "booking_one_hour": InvalidBookingInput,
            "booking_workstation_no_overlap": WorkstationConflict,
            "booking_owner_no_overlap": PersonalConflict,
        }[str(error)]
        raise refusal("The database rejected the requested booking.") from error
