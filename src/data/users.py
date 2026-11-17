"""Adapter to Django authentication, without HTTP/session responsibilities."""

from django.contrib.auth import authenticate

from .models import User


def check_credentials(email: str, password: str) -> User | None:
    """Delegate password hashing and active-account checks to Django."""
    return authenticate(username=email, password=password)


def account_state(user_id: int) -> tuple[str, bool] | None:
    """Read current role/activity without locking or loading credentials."""
    return User.objects.filter(pk=user_id).values_list("role", "is_active").first()
