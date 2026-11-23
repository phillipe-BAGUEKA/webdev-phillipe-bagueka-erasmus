"""Minimal database readiness query; no application records are read."""

from django.db import DatabaseError, connection


def database_ready() -> bool:
    """Return a generic result without disclosing database diagnostics."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone() == (1,)
    except DatabaseError:
        return False
