"""Explicit PostgreSQL regressions using only a precreated dedicated test database."""

from tests.settings import *  # noqa: F403
from src.config.postgres_config import database_settings, load_profile

DATABASES = {"default": database_settings(load_profile("test"))}
DATABASES["default"]["TEST"] = {"NAME": "test_lab_booking_1a"}
