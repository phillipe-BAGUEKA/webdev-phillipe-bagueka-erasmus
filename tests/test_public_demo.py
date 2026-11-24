"""Public demo preparation is isolated, relaunchable and preserves accounts."""

from datetime import UTC, datetime, timedelta

import pytest
from django.core.exceptions import ValidationError

from src.data.models import Booking, Laboratory, User, Workstation
from src.data.public_demo import (
    DemoDataConflict,
    LABORATORY_NAME,
    PERSONNEL_EMAIL,
    STUDENT_EMAIL,
    WORKSTATION_NAMES,
    prepare_public_demo,
    reset_public_demo_passwords,
)
from src.services.auth import authenticate_user


@pytest.mark.django_db
def test_public_demo_creates_only_the_planned_non_admin_records() -> None:
    result = prepare_public_demo("test-student-password", "test-personnel-password")
    assert result == (2, 1, 2)

    student = User.objects.get(email=STUDENT_EMAIL)
    personnel = User.objects.get(email=PERSONNEL_EMAIL)
    assert student.role == User.Role.STUDENT
    assert personnel.role == User.Role.PERSONNEL
    for user in (student, personnel):
        assert user.is_active and not user.is_staff and not user.is_superuser
    assert student.check_password("test-student-password")
    assert personnel.check_password("test-personnel-password")
    assert authenticate_user(STUDENT_EMAIL, "test-student-password").pk == student.pk

    laboratory = Laboratory.objects.get(name=LABORATORY_NAME)
    assert list(Workstation.objects.filter(laboratory=laboratory).order_by("pk").values_list(
        "name", flat=True,
    )) == list(WORKSTATION_NAMES)


@pytest.mark.django_db
def test_public_demo_rerun_preserves_ids_passwords_and_roles() -> None:
    prepare_public_demo("test-student-password", "test-personnel-password")
    initial_users = {
        user.email: (user.pk, user.password, user.role)
        for user in User.objects.filter(email__in=(STUDENT_EMAIL, PERSONNEL_EMAIL))
    }
    laboratory = Laboratory.objects.get(name=LABORATORY_NAME)
    workstation_ids = list(Workstation.objects.filter(
        laboratory=laboratory,
    ).order_by("pk").values_list("pk", flat=True))

    assert prepare_public_demo("different-student", "different-personnel") == (0, 0, 0)
    assert initial_users == {
        user.email: (user.pk, user.password, user.role)
        for user in User.objects.filter(email__in=(STUDENT_EMAIL, PERSONNEL_EMAIL))
    }
    assert Laboratory.objects.get(name=LABORATORY_NAME).pk == laboratory.pk
    assert list(Workstation.objects.filter(
        laboratory=laboratory,
    ).order_by("pk").values_list("pk", flat=True)) == workstation_ids


@pytest.mark.django_db
def test_public_demo_rejects_incompatible_role_without_partial_creation() -> None:
    User.objects.create_user(
        email=PERSONNEL_EMAIL,
        password="existing-password",
        role=User.Role.STUDENT,
    )
    with pytest.raises(DemoDataConflict):
        prepare_public_demo("test-student-password", "test-personnel-password")

    assert not User.objects.filter(email=STUDENT_EMAIL).exists()
    assert User.objects.get(email=PERSONNEL_EMAIL).check_password("existing-password")
    assert not Laboratory.objects.filter(name=LABORATORY_NAME).exists()


@pytest.mark.django_db
def test_public_demo_refuses_to_reactivate_existing_workstation() -> None:
    laboratory = Laboratory.objects.create(name=LABORATORY_NAME)
    workstation = Workstation.objects.create(
        laboratory=laboratory,
        name=WORKSTATION_NAMES[0],
        is_operational=False,
    )
    with pytest.raises(DemoDataConflict):
        prepare_public_demo("test-student-password", "test-personnel-password")

    workstation.refresh_from_db()
    assert not workstation.is_operational
    assert not User.objects.filter(email=STUDENT_EMAIL).exists()


@pytest.mark.django_db
def test_public_demo_password_reset_preserves_accounts_catalogue_and_booking() -> None:
    prepare_public_demo("initial-student-password", "initial-personnel-password")
    student = User.objects.get(email=STUDENT_EMAIL)
    personnel = User.objects.get(email=PERSONNEL_EMAIL)
    laboratory = Laboratory.objects.get(name=LABORATORY_NAME)
    workstation = Workstation.objects.get(laboratory=laboratory, name=WORKSTATION_NAMES[0])
    starts_at = datetime(2030, 1, 7, 8, tzinfo=UTC)
    booking = Booking.objects.create(
        owner=student,
        workstation=workstation,
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
    )
    identities = (student.pk, personnel.pk, laboratory.pk, workstation.pk, booking.pk)
    old_auth_hash = student.get_session_auth_hash()

    reset_public_demo_passwords("replacement-student-password", "replacement-personnel-password")

    student.refresh_from_db()
    personnel.refresh_from_db()
    booking.refresh_from_db()
    assert identities == (
        student.pk, personnel.pk, laboratory.pk, workstation.pk, booking.pk,
    )
    assert (student.role, personnel.role) == (User.Role.STUDENT, User.Role.PERSONNEL)
    assert student.check_password("replacement-student-password")
    assert personnel.check_password("replacement-personnel-password")
    assert not student.check_password("initial-student-password")
    assert student.get_session_auth_hash() != old_auth_hash
    assert booking.owner_id == student.pk
    assert booking.workstation_id == workstation.pk
    assert booking.cancelled_at is None


@pytest.mark.django_db
def test_public_demo_password_reset_rolls_back_if_second_account_is_missing() -> None:
    student = User.objects.create_user(
        email=STUDENT_EMAIL,
        password="initial-student-password",
        role=User.Role.STUDENT,
    )
    original_hash = student.password

    with pytest.raises(DemoDataConflict):
        reset_public_demo_passwords("replacement-student-password", "replacement-personnel-password")

    student.refresh_from_db()
    assert student.password == original_hash


@pytest.mark.django_db
def test_public_demo_password_reset_validates_both_before_writing() -> None:
    prepare_public_demo("initial-student-password", "initial-personnel-password")
    student = User.objects.get(email=STUDENT_EMAIL)
    original_hash = student.password

    with pytest.raises(ValidationError):
        reset_public_demo_passwords("replacement-student-password", "short")

    student.refresh_from_db()
    assert student.password == original_hash


@pytest.mark.django_db
def test_public_demo_password_reset_rejects_incompatible_personnel() -> None:
    prepare_public_demo("initial-student-password", "initial-personnel-password")
    student = User.objects.get(email=STUDENT_EMAIL)
    personnel = User.objects.get(email=PERSONNEL_EMAIL)
    original_hashes = (student.password, personnel.password)
    personnel.is_staff = True
    personnel.save(update_fields=["is_staff"])

    with pytest.raises(DemoDataConflict):
        reset_public_demo_passwords("replacement-student-password", "replacement-personnel-password")

    student.refresh_from_db()
    personnel.refresh_from_db()
    assert (student.password, personnel.password) == original_hashes
    assert personnel.is_staff
