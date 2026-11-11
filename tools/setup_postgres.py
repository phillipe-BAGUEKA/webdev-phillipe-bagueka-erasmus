"""Interactive one-time provisioning: never reuse an existing role, DB or secret."""

import getpass
import csv
import json
import os
import secrets
import subprocess
import sys
import warnings
from pathlib import Path

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]
LOCAL_ROOT = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local/share")))
EXPECTED_DATA = LOCAL_ROOT / "LabBooking" / "PostgreSQL16"
TARGETS = (
    ("dev", "lab_booking_1a", "lab_booking_1a_dev"),
    ("test", "test_lab_booking_1a", "lab_booking_1a_test"),
)


def restrict_profile_permissions(path: Path) -> None:
    """Restrict a newly created, still empty profile before writing credentials."""
    if sys.platform == "win32":
        identity = subprocess.check_output(
            ["whoami", "/user", "/fo", "csv", "/nh"],
            text=True, errors="replace",
        )
        sid = next(csv.reader(identity.splitlines()))[1]
        rights = "(OI)(CI)F" if path.is_dir() else "(F)"
        subprocess.run(
            ["icacls", str(path), "/inheritance:r", "/grant:r", f"*{sid}:{rights}"],
            check=True, capture_output=True,
        )
    else:
        path.chmod(0o600)


def provision(connection: psycopg.Connection | None = None) -> None:
    """Provision fresh objects, using only an authenticated dedicated instance."""
    if connection is None and not sys.stdin.isatty():
        raise RuntimeError("Run in an interactive terminal; masked input is required.")
    directory = ROOT / ".local"
    paths = [directory / f"postgres-1a-{kind}.json" for kind, _, _ in TARGETS]
    if any(path.exists() for path in paths):
        raise RuntimeError("A profile already exists; nothing overwritten or read.")
    if connection is None:
        prompt = "Dedicated PostgreSQL provisioning role [lab_booking_bootstrap]: "
        admin = input(prompt).strip() or "lab_booking_bootstrap"
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = getpass.getpass("Administrative password (not saved): ")
        connection = psycopg.connect(
            host="127.0.0.1", port=5433, dbname="postgres", user=admin,
            password=password, passfile="", connect_timeout=5, autocommit=True,
        )
        password = ""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_setting('port'), current_setting('cluster_name'), "
            "current_setting('data_directory')"
        )
        port, cluster, directory_name = cursor.fetchone()
        if (
            (port, cluster) != ("5433", "lab_booking_1a")
            or Path(directory_name).resolve() != EXPECTED_DATA.resolve()
        ):
            raise RuntimeError("Refusing an instance without the dedicated identity.")
    with connection:
        with connection.cursor() as cursor:
            for _, database, role in TARGETS:
                cursor.execute(
                    "SELECT 1 FROM pg_roles WHERE rolname = %s", (role,)
                )
                if cursor.fetchone():
                    raise RuntimeError(
                        "A target role already exists; no object changed."
                    )
                cursor.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s", (database,)
                )
                if cursor.fetchone():
                    raise RuntimeError(
                        "A target database already exists; no object changed."
                    )
            directory.mkdir(exist_ok=True)
            for kind, database, role in TARGETS:
                profile = {
                    "name": database, "user": role,
                    "password": secrets.token_urlsafe(48),
                    "django_key": secrets.token_urlsafe(64),
                }
                # Save new credentials before DDL: a later failure cannot lose them.
                # Exclusive creation refuses concurrent provisioning and any overwrite.
                profile_path = directory / f"postgres-1a-{kind}.json"
                with profile_path.open("x", encoding="utf-8") as handle:
                    restrict_profile_permissions(profile_path)
                    json.dump(profile, handle)
                cursor.execute(sql.SQL(
                    "CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                    "NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD {}"
                ).format(sql.Identifier(role), sql.Literal(profile["password"])))
                cursor.execute(sql.SQL(
                    "CREATE DATABASE {} OWNER {} TEMPLATE template0"
                ).format(sql.Identifier(database), sql.Identifier(role)))
                cursor.execute(sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(
                    sql.Identifier(database),
                ))
                print(f"Created dedicated database {database}, owner {role}.")
    print("Provisioning complete; no migrations or business data created.")


def main() -> int:
    try:
        provision()
    except (
        psycopg.Error, OSError, RuntimeError, EOFError, getpass.GetPassWarning,
        subprocess.SubprocessError,
    ):
        # Server errors can contain SQL/password literals. Never print the exception.
        print(
            "Provisioning incomplete. No secrets displayed. "
            "Do not delete or overwrite "
            "profiles: retain any partial state for targeted inspection.", file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
