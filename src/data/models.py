"""Persistent identities, laboratory catalogue and PostgreSQL booking schema."""

from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeBoundary
from django.utils import timezone

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


class Workstation(models.Model):
    laboratory = models.ForeignKey(Laboratory, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    is_operational = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["laboratory", "name"], name="workstation_name_in_lab"
            ),
        ]


class Booking(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    workstation = models.ForeignKey(Workstation, on_delete=models.PROTECT)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ends_at__gt=models.F("starts_at")),
                name="booking_positive_interval",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    ends_at=models.F("starts_at") + timedelta(hours=1)
                ),
                name="booking_one_hour",
            ),
            ExclusionConstraint(
                name="booking_workstation_no_overlap",
                expressions=[
                    ("workstation", "="),
                    (models.Func(
                        "starts_at", "ends_at", RangeBoundary(),
                        function="TSTZRANGE", output_field=DateTimeRangeField(),
                    ), "&&"),
                ],
                condition=models.Q(cancelled_at__isnull=True),
            ),
            ExclusionConstraint(
                name="booking_owner_no_overlap",
                expressions=[
                    ("owner", "="),
                    (models.Func(
                        "starts_at", "ends_at", RangeBoundary(),
                        function="TSTZRANGE", output_field=DateTimeRangeField(),
                    ), "&&"),
                ],
                condition=models.Q(cancelled_at__isnull=True),
            ),
        ]
