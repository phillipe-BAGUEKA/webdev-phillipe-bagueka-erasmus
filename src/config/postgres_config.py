"""Read only the explicitly provisioned PostgreSQL profile, never a .env file."""

import json
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from .base import BASE_DIR


def load_profile(kind: str, directory: Path | None = None) -> dict[str, str]:
    """Reject a missing or mismatched profile before Django can select a database."""
    if kind not in {"dev", "test"}:
        raise ImproperlyConfigured("Unknown PostgreSQL profile.")
    directory = directory if directory is not None else BASE_DIR / ".local"
    path = directory / f"postgres-1a-{kind}.json"
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise ImproperlyConfigured(
            "Run tools/setup_postgres.py locally first."
        ) from None
    expected_name = "lab_booking_1a" if kind == "dev" else "test_lab_booking_1a"
    expected_user = f"lab_booking_1a_{kind}"
    if (
        not isinstance(profile, dict)
        or set(profile) != {"name", "user", "password", "django_key"}
        or profile.get("name") != expected_name
        or profile.get("user") != expected_user
        or not all(isinstance(value, str) and value for value in profile.values())
    ):
        raise ImproperlyConfigured(
            "Invalid PostgreSQL profile; no connection attempted."
        )
    return profile


def database_settings(profile: dict[str, str]) -> dict:
    """Use a fixed local endpoint and disable ambient libpq credential sources."""
    return {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "127.0.0.1",
        "PORT": "5433",
        "NAME": profile["name"],
        "USER": profile["user"],
        "PASSWORD": profile["password"],
        "OPTIONS": {"connect_timeout": 5, "passfile": ""},
    }
