"""Foundation evidence for AC-47/48, not completed HTTP acceptance tests."""

import pytest
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor

from src.data.models import Laboratory, User


@pytest.mark.django_db
@pytest.mark.parametrize("criterion", ["AC-47-foundation"], ids=str)
def test_email_identity_and_django_password(
    criterion: str, generated_password: str
) -> None:
    user = User.objects.create_user(" Student@DEMO.example ", generated_password)
    user.refresh_from_db()
    assert get_user_model() is User
    assert user.email == "student@demo.example"
    assert User.USERNAME_FIELD == "email"
    assert "username" not in {field.name for field in User._meta.fields}
    assert user.role == User.Role.STUDENT
    assert not user.is_staff and not user.is_superuser
    assert user.password != generated_password
    assert identify_hasher(user.password).algorithm == "pbkdf2_sha256"
    assert user.check_password(generated_password)
    assert not user.check_password(generated_password + "wrong")
    assert authenticate(
        username="STUDENT@demo.example", password=generated_password
    ) == user
    assert authenticate(
        username=user.email, password=generated_password + "wrong"
    ) is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "email",
    ["student@demo.example", "STUDENT@DEMO.EXAMPLE"],
    ids=["AC-47-exact", "AC-47-case"],
)
def test_email_uniqueness_in_manager_and_database(email: str) -> None:
    User.objects.create_user("student@demo.example")
    with pytest.raises(ValidationError):
        User.objects.create_user(email)
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.bulk_create([User(email=email)])
    assert User.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "email", ["", "not-an-email"], ids=["AC-47-empty", "AC-47-invalid"]
)
def test_reject_invalid_email(email: str) -> None:
    with pytest.raises((ValueError, ValidationError)):
        User.objects.create_user(email)
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_unset_password_cannot_authenticate() -> None:
    user = User.objects.create_user("unset@demo.example")
    assert not user.has_usable_password()
    assert not user.check_password("")


@pytest.mark.django_db
def test_business_role_is_separate_from_framework_admin() -> None:
    user = User.objects.create_superuser("admin@demo.example")
    assert user.is_superuser and user.is_staff
    assert user.role == User.Role.STUDENT
    with pytest.raises(ValueError):
        User.objects.create_superuser("invalid@demo.example", is_staff=False)
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.filter(pk=user.pk).update(role="unknown")


@pytest.mark.django_db
@pytest.mark.parametrize("criterion", ["AC-48-foundation"], ids=str)
def test_initial_migrations_create_only_expected_models(criterion: str) -> None:
    executor = MigrationExecutor(connection)
    assert ("data", "0001_initial") in executor.loader.applied_migrations
    assert ("sessions", "0001_initial") in executor.loader.applied_migrations
    tables = set(connection.introspection.table_names())
    assert {"data_user", "data_laboratory", "django_session"} <= tables
    assert "auth_user" not in tables
    assert not any("booking" in name or "workstation" in name for name in tables)
    laboratory = Laboratory.objects.create(name="DEMO - Test laboratory")
    assert Laboratory.objects.get(pk=laboratory.pk).name == laboratory.name
    call_command("makemigrations", "data", check=True, dry_run=True, verbosity=0)
