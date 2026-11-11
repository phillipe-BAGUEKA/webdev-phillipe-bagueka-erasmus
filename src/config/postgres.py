"""Opt-in local PostgreSQL development; SQLite settings remain untouched."""

from .base import *  # noqa: F403
from .postgres_config import database_settings, load_profile

_profile = load_profile("dev")
SECRET_KEY = _profile["django_key"]
DATABASES = {"default": database_settings(_profile)}
DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
# Explicitly prevent the SQLite-only demonstration commands from being redirected.
DEMO_DATABASE_PATH = "/not-a-postgresql-demo.sqlite3"
DEMO_MARKER_PATH = "/not-a-postgresql-demo.marker"
