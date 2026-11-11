"""Transactional persistence and locks for the booking creation service."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from django.db import IntegrityError, transaction

from .models import Booking, User, Workstation

KNOWN_CONSTRAINTS = {
    "booking_positive_interval": "23514",
    "booking_one_hour": "23514",
    "booking_workstation_no_overlap": "23P01",
    "booking_owner_no_overlap": "23P01",
}


class ConstraintViolation(Exception):
    """A named, recognized constraint failed after the atomic block rolled back."""


@dataclass(frozen=True)
class LockedUser:
    user_id: int
    role: str
    is_active: bool


@dataclass(frozen=True)
class LockedWorkstation:
    workstation_id: int
    is_operational: bool


@contextmanager
def creation_transaction() -> Iterator[None]:
    """Roll back before exposing a recognized database refusal to the service."""
    try:
        with transaction.atomic():
            yield
    except IntegrityError as error:
        cause = error.__cause__
        diagnostic = getattr(cause, "diag", None)
        name = getattr(diagnostic, "constraint_name", None)
        if name in KNOWN_CONSTRAINTS and getattr(cause, "sqlstate", None) == KNOWN_CONSTRAINTS[name]:
            raise ConstraintViolation(name) from error
        raise


def lock_actor(user_id: int) -> LockedUser | None:
    """Lock and reload the authoritative user before taking a workstation lock."""
    user = User.objects.select_for_update().filter(pk=user_id).first()
    if user is None:
        return None
    return LockedUser(user.pk, user.role, user.is_active)


def lock_workstation(workstation_id: int) -> LockedWorkstation | None:
    station = Workstation.objects.select_for_update().filter(pk=workstation_id).first()
    if station is None:
        return None
    return LockedWorkstation(station.pk, station.is_operational)


def workstation_conflicts(workstation_id: int, start: datetime, end: datetime) -> bool:
    return Booking.objects.filter(
        workstation_id=workstation_id, cancelled_at__isnull=True,
        starts_at__lt=end, ends_at__gt=start,
    ).exists()


def insert_booking(
    owner_id: int, workstation_id: int, start: datetime, end: datetime,
    created_at: datetime,
) -> int:
    return Booking.objects.create(
        owner_id=owner_id, workstation_id=workstation_id,
        starts_at=start, ends_at=end, created_at=created_at,
    ).pk
