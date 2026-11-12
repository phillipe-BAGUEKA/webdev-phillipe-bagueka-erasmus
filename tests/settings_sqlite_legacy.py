"""Run the unchanged TP2 SQLite guard against its original isolated schema only."""

from tests.settings import *  # noqa: F403

# Do not translate PostgreSQL booking constraints to SQLite or touch demo.sqlite3.
MIGRATION_MODULES = {"data": "tests.sqlite_migrations"}
