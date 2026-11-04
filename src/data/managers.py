"""Email-based user creation using Django's password implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email

if TYPE_CHECKING:
    from .models import User


class UserManager(BaseUserManager):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email: str) -> str:
        """Use one lowercase identifier for local email sign-in."""
        return super().normalize_email(email).strip().lower()

    def get_by_natural_key(self, username: str) -> User:
        return self.get(email__iexact=self.normalize_email(username))

    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> User:
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        validate_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("A superuser requires is_staff and is_superuser.")
        # Framework administration does not assign the personnel business role.
        return self.create_user(email, password, **extra_fields)
