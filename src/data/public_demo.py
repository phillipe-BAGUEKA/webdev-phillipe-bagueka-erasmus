"""Idempotent public demonstration records, separate from local SQLite seeds."""

from django.db import transaction

from .models import Laboratory, User, Workstation


STUDENT_EMAIL = "student-public@demo.example"
PERSONNEL_EMAIL = "personnel-public@demo.example"
LABORATORY_NAME = "DEMO PUBLIC - Laboratory"
WORKSTATION_NAMES = ("DEMO PUBLIC - Poste A", "DEMO PUBLIC - Poste B")


class DemoDataConflict(Exception):
    """A record with a demonstration identifier has incompatible existing data."""


def prepare_public_demo(
    student_password: str,
    personnel_password: str,
) -> tuple[int, int, int]:
    """Add missing demo rows without changing any existing password or role."""
    created_users = 0
    created_laboratories = 0
    created_workstations = 0

    with transaction.atomic():
        for email, role, password in (
            (STUDENT_EMAIL, User.Role.STUDENT, student_password),
            (PERSONNEL_EMAIL, User.Role.PERSONNEL, personnel_password),
        ):
            user = User.objects.filter(email__iexact=email).first()
            if user is None:
                User.objects.create_user(
                    email=email,
                    password=password,
                    role=role,
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                )
                created_users += 1
            elif (
                user.role != role
                or not user.is_active
                or user.is_staff
                or user.is_superuser
            ):
                raise DemoDataConflict("Incompatible demonstration account.")

        laboratories = list(Laboratory.objects.filter(name=LABORATORY_NAME)[:2])
        if len(laboratories) > 1:
            raise DemoDataConflict("Duplicate demonstration laboratory.")
        if laboratories:
            laboratory = laboratories[0]
        else:
            laboratory = Laboratory.objects.create(name=LABORATORY_NAME)
            created_laboratories += 1

        for name in WORKSTATION_NAMES:
            workstation, created = Workstation.objects.get_or_create(
                laboratory=laboratory,
                name=name,
                defaults={"is_operational": True},
            )
            if not workstation.is_operational:
                raise DemoDataConflict("Demonstration workstation is out of service.")
            created_workstations += int(created)

    return created_users, created_laboratories, created_workstations
