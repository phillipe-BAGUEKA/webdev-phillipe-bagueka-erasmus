"""Fixed, separate PostgreSQL database for an empty-chain migration proof."""

from .postgres import *  # noqa: F403

DATABASES = {"default": {**DATABASES["default"], "NAME": "lab_booking_1b_verify"}}
