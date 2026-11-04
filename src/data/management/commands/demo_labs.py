"""Manual AC-48 procedure restricted to the disposable demonstration database."""

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from src.data import demo_labs


class Command(BaseCommand):
    help = "Inspect, back up, withdraw or restore one fictitious demo laboratory."

    def add_arguments(self, parser: ArgumentParser) -> None:
        commands = parser.add_subparsers(dest="action", required=True)
        commands.add_parser("list")
        backup = commands.add_parser("backup")
        backup.add_argument("--id", type=int, required=True)
        backup.add_argument("--snapshot", type=Path, required=True)
        for name in ("withdraw", "restore"):
            command = commands.add_parser(name)
            command.add_argument("--snapshot", type=Path, required=True)

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            action = options["action"]
            if action == "list":
                rows = demo_labs.inspect_laboratories()
                self.stdout.write(f"Disposable demo: {settings.DEMO_DATABASE_PATH}")
                for lab in rows:
                    self.stdout.write(f"{lab['id']}: {lab['name']}")
            elif action == "backup":
                demo_labs.backup_laboratory(options["id"], options["snapshot"])
                self.stdout.write("Snapshot saved. No database change.")
            elif action == "withdraw":
                demo_labs.withdraw_laboratory(options["snapshot"])
                self.stdout.write("One demo laboratory withdrawn; snapshot preserved.")
            else:
                created = demo_labs.restore_laboratory(options["snapshot"])
                message = "Laboratory restored." if created else "Already restored."
                self.stdout.write(message)
        except (ValueError, OSError) as error:
            raise CommandError(str(error)) from error
