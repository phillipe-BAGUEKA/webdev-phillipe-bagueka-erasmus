"""Read-only booking projection for the personnel consultation."""

from typing import Any

from .models import Booking


def all_bookings() -> list[dict[str, Any]]:
    """Fetch the fields needed for the staff view in one query."""
    return list(Booking.objects.order_by("-starts_at", "-id").values(
        "id",
        "owner_id",
        "workstation__laboratory__name",
        "workstation__name",
        "starts_at",
        "ends_at",
        "cancelled_at",
    ))
