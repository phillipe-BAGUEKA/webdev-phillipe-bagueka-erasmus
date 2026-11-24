"""Public demo preparation is isolated, relaunchable and preserves accounts."""

import pytest

from src.data.models import Laboratory, User, Workstation
from src.data.public_demo import (
    DemoDataConflict,
    LABORATORY_NAME,
    PERSONNEL_EMAIL,
    STUDENT_EMAIL,
    WORKSTATION_NAMES,
    prepare_public_demo,
)


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
