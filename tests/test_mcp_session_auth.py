"""Real Django sessions on the isolated PostgreSQL database; AC-38 groundwork."""

from datetime import timedelta
from importlib import import_module
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY
from django.contrib.sessions.models import Session
from django.db import OperationalError, connection
from django.test import Client, override_settings
from django.utils import timezone

from src.data.models import User
from src.services.access import Actor, AuthenticationRequired

pytestmark = pytest.mark.django_db


def authenticate(key: str | None) -> Actor:
    """Import lazily so the first refusal proves the missing implementation."""
    return import_module("src.services.session_auth").authenticate_session(key)


@pytest.fixture
def signed_session(active_student: User, generated_password: str) -> tuple[Client, str]:
    assert connection.vendor == "postgresql"
    assert connection.settings_dict["NAME"] == "test_lab_booking_1a"
    client = Client()
    assert client.login(email=active_student.email, password=generated_password)
    return client, client.cookies[settings.SESSION_COOKIE_NAME].value


@pytest.mark.parametrize("key", [None, "", "not-a-session", "a" * 32],
                         ids=["AC-38-absent", "AC-38-empty", "AC-38-malformed",
                              "AC-38-unknown"])
def test_refuse_missing_or_unknown_session(key: str | None) -> None:
    before = list(Session.objects.values())
    with pytest.raises(AuthenticationRequired):
        authenticate(key)
    assert list(Session.objects.values()) == before


def test_AC_38_real_session_returns_current_ordinary_actor(
    signed_session: tuple[Client, str], active_student: User,
) -> None:
    _, key = signed_session
    before = list(Session.objects.values())
    actor = authenticate(key)
    assert (actor.user_id, actor.email, actor.role, actor.is_active) == (
        active_student.pk, active_student.email, "student", True,
    )
    active_student.role = "personnel"
    active_student.save(update_fields=["role"])
    assert authenticate(key).role == "personnel"
    assert list(Session.objects.values()) == before


@pytest.mark.parametrize("reason", [
    "expired", "deleted", "inactive", "password", "user-deleted", "staff",
    "superuser", "corrupted", "missing-user", "invalid-user", "missing-backend",
    "unknown-backend", "missing-hash", "invalid-hash",
], ids=lambda reason: "AC-38-" + reason)
def test_refuse_invalidated_session_without_writing(
    signed_session: tuple[Client, str], active_student: User, reason: str,
) -> None:
    client, key = signed_session
    if reason == "expired":
        Session.objects.filter(session_key=key).update(
            expire_date=timezone.now() - timedelta(seconds=1),
        )
    elif reason == "deleted":
        Session.objects.filter(session_key=key).delete()
    elif reason == "user-deleted":
        active_student.delete()
    elif reason in {"inactive", "staff", "superuser"}:
        field = {
            "inactive": "is_active", "staff": "is_staff", "superuser": "is_superuser",
        }[reason]
        setattr(active_student, field, reason != "inactive")
        active_student.save(update_fields=[field])
    elif reason == "password":
        active_student.set_password("test-only-new-password")
        active_student.save(update_fields=["password"])
    elif reason == "corrupted":
        Session.objects.filter(session_key=key).update(session_data="invalid-signed-data")
    else:
        session = client.session
        field = {
            "missing-user": SESSION_KEY, "invalid-user": SESSION_KEY,
            "missing-backend": BACKEND_SESSION_KEY,
            "unknown-backend": BACKEND_SESSION_KEY,
            "missing-hash": HASH_SESSION_KEY, "invalid-hash": HASH_SESSION_KEY,
        }[reason]
        if reason.startswith("missing"):
            del session[field]
        else:
            session[field] = "invalid-value"
        session.save()
    before = list(Session.objects.values())
    with pytest.raises(AuthenticationRequired):
        authenticate(key)
    assert list(Session.objects.values()) == before


def test_AC_38_logout_revokes_between_calls_in_same_process(
    signed_session: tuple[Client, str],
) -> None:
    client, key = signed_session
    assert authenticate(key).is_active
    client.logout()
    with pytest.raises(AuthenticationRequired):
        authenticate(key)
    assert not Session.objects.filter(session_key=key).exists()


def test_AC_38_secret_rotation_does_not_cycle_browser_session(
    signed_session: tuple[Client, str],
) -> None:
    _, key = signed_session
    before = list(Session.objects.values())
    with override_settings(
        SECRET_KEY="new-test-only-key", SECRET_KEY_FALLBACKS=[settings.SECRET_KEY],
    ):
        with pytest.raises(AuthenticationRequired):
            authenticate(key)
    assert list(Session.objects.values()) == before


def test_AC_38_database_failure_is_not_an_authenticated_actor(
    signed_session: tuple[Client, str],
) -> None:
    _, key = signed_session
    with patch(
        "src.data.session_auth.ReadOnlySessionStore.load", side_effect=OperationalError,
    ):
        with pytest.raises(OperationalError):
            authenticate(key)
