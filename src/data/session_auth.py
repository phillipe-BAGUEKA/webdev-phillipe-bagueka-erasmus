"""Resolve Django authentication without creating, renewing or deleting sessions."""

import re
from dataclasses import dataclass

from django.contrib.auth import get_user
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ValidationError


class SessionMutationRefused(Exception):
    """A rotated or invalid session requires a new interactive login."""


class ReadOnlySessionStore(SessionStore):
    """Let Django validate its auth hash, but disallow its repair operations."""

    @property
    def key_salt(self) -> str:
        """Preserve the regular backend's signature despite the subclass name."""
        return SessionStore().key_salt

    def cycle_key(self) -> None:
        raise SessionMutationRefused

    def flush(self) -> None:
        raise SessionMutationRefused


@dataclass(frozen=True)
class SessionContext:
    """Only the session attribute required by Django get_user; no HTTP request."""

    session: ReadOnlySessionStore


@dataclass(frozen=True)
class SessionIdentity:
    user_id: int
    email: str
    role: str
    is_active: bool
    is_staff: bool
    is_superuser: bool


def session_identity(session_key: str | None) -> SessionIdentity | None:
    """Load a fresh database session and run Django's full user/hash validation."""
    if (not isinstance(session_key, str)
            or not re.fullmatch(r"[a-z0-9]{32}", session_key)):
        return None
    context = SessionContext(ReadOnlySessionStore(session_key=session_key))
    try:
        user = get_user(context)
    except (SessionMutationRefused, ValueError, TypeError, ValidationError):
        return None
    if not user.is_authenticated:
        return None
    return SessionIdentity(
        user.pk, user.email, user.role, user.is_active,
        user.is_staff, user.is_superuser,
    )
