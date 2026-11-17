"""Rotate only the dedicated local test role, without printing credentials."""

import json
import os
from pathlib import Path
import secrets
import sys

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.config.postgres_config import load_profile

PROFILE = ROOT / ".local" / "postgres-1a-test.json"
RECEIPT = ROOT / ".local" / "postgres-test-password-rotation.json"


def connect(profile: dict[str, str]) -> psycopg.Connection:
    """Ignore ambient libpq credentials; never contact the development role."""
    return psycopg.connect(
        host="127.0.0.1", port=5433, dbname="test_lab_booking_1a",
        user="lab_booking_1a_test", password=profile["password"],
        passfile="", connect_timeout=5, autocommit=True,
    )


def write_profile(profile: dict[str, str]) -> None:
    """Update the existing file in place, preserving its Windows ACL and owner."""
    with PROFILE.open("r+", encoding="utf-8") as handle:
        json.dump(profile, handle)
        handle.truncate()
        handle.flush()
        os.fsync(handle.fileno())


def rotate() -> None:
    """Perform the explicitly authorized one-time rotation and verify both keys."""
    if RECEIPT.exists():
        raise RuntimeError("Rotation already recorded; refusing to repeat it.")
    previous = load_profile("test", PROFILE.parent)
    replacement = {**previous, "password": secrets.token_urlsafe(48)}
    with connect(previous) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_user, current_database(), inet_server_port(), "
                "current_setting('cluster_name'), current_setting('log_statement'), "
                "current_setting('log_min_error_statement'), "
                "current_setting('log_duration'), "
                "current_setting('log_min_duration_statement'), "
                "current_setting('log_min_duration_sample'), "
                "current_setting('log_transaction_sample_rate')"
            )
            expected = (
                "lab_booking_1a_test", "test_lab_booking_1a", 5433,
                "lab_booking_1a", "none", "panic", "off", "-1", "-1", "0",
            )
            if cursor.fetchone() != expected:
                raise RuntimeError("Unexpected instance or unsafe SQL logging.")
        verifier = connection.pgconn.encrypt_password(
            replacement["password"].encode(), previous["user"].encode(),
            b"scram-sha-256",
        ).decode()
        try:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                        sql.Identifier("lab_booking_1a_test"), sql.Literal(verifier),
                    ))
                write_profile(replacement)
        except BaseException:
            write_profile(previous)
            raise
    with connect(replacement) as verified:
        with verified.cursor() as cursor:
            cursor.execute("SELECT current_user, current_database()")
            if cursor.fetchone() != ("lab_booking_1a_test", "test_lab_booking_1a"):
                raise RuntimeError("Replacement verification failed.")
    try:
        with connect(previous):
            raise RuntimeError("Previous password still accepted.")
    except psycopg.OperationalError as error:
        # Inspect privately: a timeout is not proof of authentication refusal.
        if "password authentication failed" not in str(error):
            raise RuntimeError("Old-password verification inconclusive.") from None
    RECEIPT.write_text(json.dumps({
        "role": "lab_booking_1a_test", "port": 5433,
        "new_connection_verified": True, "old_password_rejected": True,
    }), encoding="utf-8")


def main() -> int:
    try:
        rotate()
    except Exception:
        print("Rotation stopped; inspect non-sensitive state before retrying.",
              file=sys.stderr)
        return 1
    print("Test-role rotation verified; previous password rejected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
