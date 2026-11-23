"""Application readiness decision shared independently of HTTP."""

from src.data.health import database_ready


def is_ready() -> bool:
    """Report whether the application can reach its database."""
    return database_ready()
