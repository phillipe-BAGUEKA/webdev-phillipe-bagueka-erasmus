"""Check the public student account through Django without printing credentials."""

from getpass import getpass
from re import fullmatch
import subprocess

from tools.prepare_neon_demo import IMAGE, checked_url


WORKER = """
import os
import secrets
import sys

os.environ["DATABASE_URL"] = sys.stdin.buffer.readline().decode("utf-8").rstrip("\\r\\n")
password = sys.stdin.buffer.readline().decode("utf-8").rstrip("\\r\\n")
os.environ["DJANGO_SECRET_KEY"] = secrets.token_urlsafe(60)
os.environ["DJANGO_SETTINGS_MODULE"] = "src.config.production"
os.environ["DJANGO_ALLOWED_HOSTS"] = "localhost"
os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://localhost"
os.environ["PGOPTIONS"] = "-c default_transaction_read_only=on"

try:
    import django
    django.setup()
    from django.db import connection
    from src.data.models import Laboratory, User, Workstation
    from src.data.public_demo import LABORATORY_NAME, STUDENT_EMAIL
    from src.services.auth import InvalidCredentials, authenticate_user

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_database(), current_setting('server_version_num'), "
            "current_setting('transaction_read_only')"
        )
        database, version, read_only = cursor.fetchone()
    if (
        database != "lab_booking"
        or int(version) // 10000 != 16
        or read_only != "on"
        or not connection.connection.pgconn.ssl_in_use
    ):
        raise RuntimeError("Unexpected database")

    user = User.objects.filter(email__iexact=STUDENT_EMAIL).first()
    if user is None:
        result = "ACCOUNT_MISSING"
    elif not user.is_active:
        result = "ACCOUNT_INACTIVE"
    elif not user.check_password(password):
        result = "PASSWORD_MISMATCH"
    else:
        try:
            authenticated = authenticate_user(STUDENT_EMAIL, password)
        except InvalidCredentials:
            result = "AUTH_BACKEND_REJECTED"
        else:
            result = "LOGIN_VALID" if authenticated.pk == user.pk else "AUTH_BACKEND_REJECTED"

    laboratory = Laboratory.objects.filter(name=LABORATORY_NAME).first()
    workstation_count = (
        Workstation.objects.filter(laboratory=laboratory).count()
        if laboratory is not None else 0
    )
    print(f"DEMO_LOGIN:{result}:catalogue={int(laboratory is not None)}/{workstation_count}")
except Exception:
    print("DEMO_LOGIN:CHECK_FAILED")
    sys.exit(1)
"""


def main() -> int:
    """Check only the planned account using masked input and no database writes."""
    try:
        database_url = checked_url(getpass("DATABASE_URL directe Neon (masquée) : "))
        password = getpass("Mot de passe étudiant choisi pour le préparateur : ")
    except (ValueError, KeyboardInterrupt):
        print("DEMO_LOGIN:INPUT_REJECTED")
        return 2

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm", "-i", "--log-driver=none",
                "--entrypoint", "python", IMAGE, "-c", WORKER,
            ],
            input=f"{database_url}\n{password}\n".encode("utf-8"),
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        print("DEMO_LOGIN:CHECK_FAILED")
        return 1

    output = result.stdout.decode("ascii", errors="replace").strip()
    valid = {
        "LOGIN_VALID", "PASSWORD_MISMATCH", "ACCOUNT_MISSING",
        "ACCOUNT_INACTIVE", "AUTH_BACKEND_REJECTED",
    }
    if result.returncode == 0 and output.startswith("DEMO_LOGIN:"):
        parts = output.split(":")
        if (
            len(parts) == 3
            and parts[1] in valid
            and fullmatch(r"catalogue=\d+/\d+", parts[2])
        ):
            print(output)
            return 0
    print("DEMO_LOGIN:CHECK_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
