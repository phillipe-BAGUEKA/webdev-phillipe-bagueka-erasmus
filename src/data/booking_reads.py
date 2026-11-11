"""Eager read-only ORM projections; no query escapes into the services."""

from datetime import datetime
from typing import Any

from .models import Booking, Laboratory, Workstation


def laboratory_exists(laboratory_id: int) -> bool:
    return Laboratory.objects.filter(pk=laboratory_id).exists()


def workstations(laboratory_id: int) -> list[dict[str, Any]]:
    return list(Workstation.objects.filter(laboratory_id=laboratory_id)
                .order_by("id").values("id", "name", "is_operational"))


def upcoming_count(owner_id: int, now: datetime) -> int:
    return Booking.objects.filter(
        owner_id=owner_id, cancelled_at__isnull=True, starts_at__gt=now,
    ).count()


def occupied_intervals(
    laboratory_id: int, start: datetime, end: datetime,
) -> list[tuple[int, datetime, datetime]]:
    return list(Booking.objects.filter(
        workstation__laboratory_id=laboratory_id, cancelled_at__isnull=True,
        starts_at__lt=end, ends_at__gt=start,
    ).values_list("workstation_id", "starts_at", "ends_at"))


def personal_intervals(
    owner_id: int, start: datetime, end: datetime,
) -> list[tuple[datetime, datetime]]:
    return list(Booking.objects.filter(
        owner_id=owner_id, cancelled_at__isnull=True,
        starts_at__lt=end, ends_at__gt=start,
    ).values_list("starts_at", "ends_at"))


def personal_bookings(owner_id: int) -> list[dict[str, Any]]:
    return list(Booking.objects.filter(owner_id=owner_id).order_by(
        "-starts_at", "-id"
    ).values(
        "id", "workstation_id", "workstation__name", "starts_at", "ends_at",
        "created_at", "cancelled_at", "workstation__is_operational",
        "workstation__laboratory_id", "workstation__laboratory__name",
    ))
