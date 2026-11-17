"""Opt-in Django bootstrap and per-call session adapter; no project tools yet."""

import os
from pathlib import Path
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.access import Actor


class SessionAuthenticationUnavailable(Exception):
    """Technical authentication failure without connection or driver details."""


def initialize_project() -> None:
    """Initialize only the explicitly selected PostgreSQL application profile."""
    root = str(Path(__file__).resolve().parents[1])
    if root not in sys.path:
        sys.path.insert(0, root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.config.postgres")

    import django
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    from django.db import connection

    django.setup()
    if (connection.vendor != "postgresql"
            or settings.SESSION_ENGINE != "django.contrib.sessions.backends.db"):
        raise ImproperlyConfigured("PostgreSQL and database sessions are required.")
    connection.ensure_connection()


def current_actor() -> "Actor":
    """Authenticate anew on every future project dispatch, never at handshake."""
    from django.db import DatabaseError
    from src.services.session_auth import authenticate_session

    try:
        return authenticate_session(os.environ.get("LAB_BOOKING_MCP_SESSION"))
    except DatabaseError:
        raise SessionAuthenticationUnavailable(
            "Session authentication unavailable.",
        ) from None
