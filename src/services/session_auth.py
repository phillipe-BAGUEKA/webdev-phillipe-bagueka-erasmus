"""Authenticate a fresh ordinary-user session for non-HTTP application adapters."""

from src.data.session_auth import session_identity
from .access import Actor, AuthenticationRequired, require_authenticated


def authenticate_session(session_key: str | None) -> Actor:
    """Reject missing/revoked/privileged sessions without caching their actor."""
    identity = session_identity(session_key)
    if identity is None or identity.is_staff or identity.is_superuser:
        raise AuthenticationRequired
    return require_authenticated(Actor(
        identity.user_id, identity.email, identity.role, identity.is_active,
    ))
