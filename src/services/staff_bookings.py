"""Personnel booking consultation independent of the transport."""

from dataclasses import dataclass
from datetime import datetime, timezone

from src.data import staff_bookings as data

from .access import Actor, require_staff_actor
from .booking_reads import booking_status, read_instant


@dataclass(frozen=True)
class StaffBooking:
    booking_id: int
    owner_id: int
    laboratory_name: str
    workstation_name: str
    starts_at: datetime
    ends_at: datetime
    status: str


def list_staff_bookings(
    actor: Actor | None, *, now: datetime | None = None,
) -> list[StaffBooking]:
    """Read all bookings, most recent start first, then descending booking ID."""
    require_staff_actor(actor)
    instant = read_instant(now)
    return [
        StaffBooking(
            booking_id=row["id"],
            owner_id=row["owner_id"],
            laboratory_name=row["workstation__laboratory__name"],
            workstation_name=row["workstation__name"],
            starts_at=row["starts_at"].astimezone(timezone.utc),
            ends_at=row["ends_at"].astimezone(timezone.utc),
            status=booking_status(
                row["starts_at"], row["ends_at"], row["cancelled_at"], instant,
            ),
        )
        for row in data.all_bookings()
    ]
