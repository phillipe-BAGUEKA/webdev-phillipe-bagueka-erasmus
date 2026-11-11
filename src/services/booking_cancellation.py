"""Owner-only, idempotent cancellation independent of HTTP and MCP."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from django.utils import timezone as django_timezone

from src.data import booking_cancellation as data
from src.data import booking_creation as locks
from .access import Actor, AuthenticationRequired, require_authenticated
from .booking_creation import BookingError, InvalidBookingInput


class BookingNotFound(BookingError):
    """The requested booking no longer exists."""


class NotBookingOwner(BookingError):
    """The actor does not own this booking, including cancelled bookings."""


class CancellationTooLate(BookingError):
    """The first cancellation must occur strictly before the slot begins."""


class BookingChanged(BookingError):
    """The routing key changed before locking; abort without taking locks anew."""


@dataclass(frozen=True)
class CancellationResult:
    booking_id: int
    owner_id: int
    workstation_id: int
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    cancelled_at: datetime


def _result(
    row: data.LockedBooking, cancelled_at: datetime,
) -> CancellationResult:
    return CancellationResult(
        row.booking_id, row.owner_id, row.workstation_id,
        row.starts_at.astimezone(timezone.utc),
        row.ends_at.astimezone(timezone.utc),
        row.created_at.astimezone(timezone.utc),
        cancelled_at.astimezone(timezone.utc),
    )


def cancel_booking(
    actor: Actor | None, booking_id: int,
    *, clock: Callable[[], datetime] | None = None,
) -> CancellationResult:
    """Authenticate and lock user -> station -> booking before any decision.

    Actor comes from a trusted authenticated adapter. A repeated cancellation
    returns the stored state without reading the clock or writing anything.
    """
    actor = require_authenticated(actor)
    if type(booking_id) is not int or booking_id <= 0:
        raise InvalidBookingInput("A positive booking ID is required.")
    with data.cancellation_transaction():
        current_actor = locks.lock_actor(actor.user_id)
        if current_actor is None or not current_actor.is_active:
            raise AuthenticationRequired
        station_id = data.workstation_hint(booking_id)
        if station_id is None:
            raise BookingNotFound("Booking not found.")
        locks.lock_workstation(station_id)
        row = data.lock_booking(booking_id)
        if row is None:
            raise BookingNotFound("Booking no longer exists.")
        if row.owner_id != current_actor.user_id:
            raise NotBookingOwner("Only the owner may cancel this booking.")
        if row.workstation_id != station_id:
            raise BookingChanged("Booking changed; submit a fresh request.")
        if row.cancelled_at is not None:
            return _result(row, row.cancelled_at)
        instant = django_timezone.now() if clock is None else clock()
        if not isinstance(instant, datetime) or instant.utcoffset() is None:
            raise InvalidBookingInput("An aware current instant is required.")
        instant = instant.astimezone(timezone.utc)
        if instant >= row.starts_at:
            raise CancellationTooLate("The slot has already begun.")
        data.mark_cancelled(booking_id, instant)
        return _result(row, instant)
