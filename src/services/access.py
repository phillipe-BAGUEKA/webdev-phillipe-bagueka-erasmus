"""Transport-independent authenticated-access policy."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    user_id: int
    email: str
    role: str
    is_active: bool


class AuthenticationRequired(Exception):
    """The operation requires an active, authenticated actor."""


class StaffAccessDenied(PermissionError):
    """An active account lacks the personnel business role."""


def require_authenticated(actor: Actor | None) -> Actor:
    if actor is None or not actor.is_active:
        raise AuthenticationRequired
    return actor


def require_staff_actor(actor: Actor | None) -> Actor:
    """Require an active actor with the personnel business role."""
    actor = require_authenticated(actor)
    if actor.role != "personnel":
        raise StaffAccessDenied
    return actor
