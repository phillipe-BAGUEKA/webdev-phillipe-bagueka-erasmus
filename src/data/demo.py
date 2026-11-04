"""Idempotent demonstration data, separate from schema migrations."""

from pathlib import Path

from django.conf import settings
from django.db import connection, transaction

from .models import Laboratory, User

DEMO_MARKER = "lab-booking-disposable-demo-v1\n"
DEMO_EMAILS = ("student1@demo.example", "student2@demo.example")
DEMO_LABS = {
    1: "DEMO - Laboratory Alpha",
    2: "DEMO - Laboratory Beta",
    3: "DEMO - Laboratory Gamma",
}


def require_demo_database() -> None:
    """Refuse seeding unless the configured SQLite database is explicitly marked."""
    expected_path = Path(settings.DEMO_DATABASE_PATH).resolve()
    actual_path = Path(connection.settings_dict["NAME"]).resolve()
    if (
        connection.vendor != "sqlite"
        or actual_path != expected_path
        or not actual_path.is_file()
    ):
        raise ValueError("Refusing to seed a database other than the prepared demo.")
    marker_path = Path(settings.DEMO_MARKER_PATH)
    if (
        not marker_path.is_file()
        or marker_path.read_text(encoding="utf-8") != DEMO_MARKER
    ):
        raise ValueError("Missing or invalid disposable demonstration marker.")


@transaction.atomic
def seed_demo_data() -> tuple[list[User], int]:
    """Preserve matching rows and refuse conflicting rows atomically."""
    for lab_id, name in DEMO_LABS.items():
        existing_lab = Laboratory.objects.filter(pk=lab_id).first()
        if existing_lab is not None and existing_lab.name != name:
            raise ValueError(f"Laboratory {lab_id} differs; no data changed.")
    for email in DEMO_EMAILS:
        existing_user = User.objects.filter(email__iexact=email).first()
        if existing_user is not None and (
            existing_user.role != User.Role.STUDENT
            or existing_user.is_staff
            or existing_user.is_superuser
            or not existing_user.is_active
        ):
            raise ValueError(f"Account {email} differs; no data changed.")

    new_lab_count = 0
    for lab_id, name in DEMO_LABS.items():
        _, created = Laboratory.objects.get_or_create(
            pk=lab_id, defaults={"name": name}
        )
        new_lab_count += int(created)

    new_users = []
    for email in DEMO_EMAILS:
        if not User.objects.filter(email__iexact=email).exists():
            # None produces Django's unusable password, never a shared default.
            new_users.append(User.objects.create_user(email=email))
    return new_users, new_lab_count
