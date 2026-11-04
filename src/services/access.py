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


def require_authenticated(actor: Actor | None) -> Actor:
    if actor is None or not actor.is_active:
        raise AuthenticationRequired
    return actor
