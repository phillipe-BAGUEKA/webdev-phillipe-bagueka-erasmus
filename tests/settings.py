"""Test-only settings. No environment file or local development key is loaded."""

from src.config.base import *  # noqa: F403 - share non-secret Django settings.

SECRET_KEY = "test-only-public-value-never-use-outside-isolated-tests"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
ALLOWED_HOSTS = ["testserver"]
DEMO_DATABASE_PATH = "/not-the-demo-database.sqlite3"
DEMO_MARKER_PATH = "/not-the-demo-marker"
