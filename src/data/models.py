"""Initial models: email identity and laboratory catalogue only."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        PERSONNEL = "personnel", "Personnel"

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.STUDENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="user_email_case_insensitive"),
            models.CheckConstraint(
                condition=models.Q(role__in=["student", "personnel"]),
                name="user_valid_business_role",
            ),
        ]


class Laboratory(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.name
