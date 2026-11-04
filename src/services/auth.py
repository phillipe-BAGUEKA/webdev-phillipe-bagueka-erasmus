"""Local credential validation, independent of HTTP session creation."""

from src.data import users
from src.data.models import User


class InvalidCredentials(Exception):
    """Use the same refusal for unknown, inactive and incorrectly signed-in users."""


def authenticate_user(email: str, password: str) -> User:
    user = users.check_credentials(email, password)
    if user is None or not user.is_active:
        raise InvalidCredentials
    return user
