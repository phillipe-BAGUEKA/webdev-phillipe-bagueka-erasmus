import secrets

import pytest
from django.test import Client

from src.data.models import User


@pytest.fixture
def generated_password() -> str:
    """An ephemeral test credential, unrelated to local demonstration accounts."""
    return secrets.token_urlsafe(24)


@pytest.fixture
def active_student(db: None, generated_password: str) -> User:
    return User.objects.create_user("student@tests.example", generated_password)


@pytest.fixture
def csrf_client() -> Client:
    """Keep Django's actual CSRF middleware checks enabled in HTTP tests."""
    client = Client(enforce_csrf_checks=True)
    client.get("/login")
    return client
