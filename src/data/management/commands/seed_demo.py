"""Prepare disposable demonstration accounts without publishing credentials."""

import getpass
import sys
import warnings
from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from src.data.demo import DEMO_EMAILS, require_demo_database, seed_demo_data
from src.data.models import User


def choose_password(user: User) -> None:
    """Prompt without echo; refuse getpass's insecure fallback to visible input."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        password = getpass.getpass(f"Password for {user.email}: ")
        confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise CommandError(
            "Passwords differ; account remains without a usable password."
        )
    try:
        validate_password(password, user=user)
    except ValidationError as error:
        raise CommandError(
            "Password rejected by Django validators; use changepassword to retry."
        ) from error
    user.set_password(password)
    user.save(update_fields=["password"])


class Command(BaseCommand):
    help = "Prepare the marked disposable demo; preserve existing accounts."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Create accounts with unusable passwords; set them locally later.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            require_demo_database()
        except ValueError as error:
            raise CommandError(str(error)) from error
        if not options["no_input"] and not sys.stdin.isatty():
            raise CommandError("Use a real terminal for masked input, or --no-input.")
        try:
            new_users, new_lab_count = seed_demo_data()
        except ValueError as error:
            raise CommandError(str(error)) from error

        self.stdout.write(f"Demo database: {settings.DEMO_DATABASE_PATH}")
        self.stdout.write(
            f"Created: {len(new_users)} accounts, {new_lab_count} laboratories."
        )
        if not options["no_input"]:
            try:
                for user in new_users:
                    choose_password(user)
            except (EOFError, KeyboardInterrupt, getpass.GetPassWarning) as error:
                raise CommandError(
                    "Masked input interrupted/unavailable. Use changepassword locally."
                ) from error
        for email in DEMO_EMAILS:
            user = User.objects.get(email__iexact=email)
            state = "password set" if user.has_usable_password() else "password not set"
            self.stdout.write(f"{email}: {state}; role={user.role}")
        self.stdout.write(
            "Existing passwords/roles preserved. For an unset password, run "
            "manage.py changepassword EMAIL in your own terminal."
        )
