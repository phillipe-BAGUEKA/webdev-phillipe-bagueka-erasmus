"""Cancellation persistence; preliminary lookup never authorizes a write."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from django.db import transaction

from .models import Booking


@dataclass(frozen=True)
class LockedBooking:
    booking_id: int
    owner_id: int
    workstation_id: int
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    cancelled_at: datetime | None


@contextmanager
def cancellation_transaction() -> Iterator[None]:
    with transaction.atomic():
        yield


def workstation_hint(booking_id: int) -> int | None:
    """Read only the routing key; reload the full booking after all locks."""
    return Booking.objects.filter(pk=booking_id).values_list(
        "workstation_id", flat=True,
    ).first()


def lock_booking(booking_id: int) -> LockedBooking | None:
    row = Booking.objects.select_for_update().filter(pk=booking_id).first()
    if row is None:
        return None
    return LockedBooking(
        row.pk, row.owner_id, row.workstation_id, row.starts_at,
        row.ends_at, row.created_at, row.cancelled_at,
    )


def mark_cancelled(booking_id: int, cancelled_at: datetime) -> None:
    """Called only after ownership/state validation while holding the row lock."""
    Booking.objects.filter(pk=booking_id).update(cancelled_at=cancelled_at)
