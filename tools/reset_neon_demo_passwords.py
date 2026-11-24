"""Reset only two public demo password hashes with masked local input."""

from getpass import getpass
import subprocess

from tools.prepare_neon_demo import IMAGE, ask_password, checked_url


WORKER = """
import os
import secrets
import sys

os.environ["DATABASE_URL"] = sys.stdin.buffer.readline().decode("utf-8").rstrip("\\r\\n")
student_password = sys.stdin.buffer.readline().decode("utf-8").rstrip("\\r\\n")
personnel_password = sys.stdin.buffer.readline().decode("utf-8").rstrip("\\r\\n")
os.environ["DJANGO_SECRET_KEY"] = secrets.token_urlsafe(60)
os.environ["DJANGO_SETTINGS_MODULE"] = "src.config.production"
os.environ["DJANGO_ALLOWED_HOSTS"] = "localhost"
os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://localhost"

conflict_type = ()
validation_error_type = ()
try:
    import django
    from django.core.exceptions import ValidationError
    from django.db import connection
    validation_error_type = ValidationError
    django.setup()
    from src.data.public_demo import DemoDataConflict, reset_public_demo_passwords
    conflict_type = DemoDataConflict

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_database(), current_setting('server_version_num'), "
            "current_setting('transaction_read_only')"
        )
        database, version, read_only = cursor.fetchone()
    if (
        database != "lab_booking"
        or int(version) // 10000 != 16
        or read_only != "off"
        or not connection.connection.pgconn.ssl_in_use
    ):
        raise RuntimeError("Unexpected database")

    reset_public_demo_passwords(student_password, personnel_password)
except Exception as error:
    if isinstance(error, conflict_type):
        print("DEMO_RESET:ACCOUNT_MISMATCH")
    elif isinstance(error, validation_error_type):
        print("DEMO_RESET:PASSWORD_RULE")
    else:
        print("DEMO_RESET:CHECK_OR_CONNECTION")
    sys.exit(1)
else:
    print("DEMO_RESET:OK")
finally:
    try:
        connection.close()
    except Exception:
        pass
"""


def main() -> int:
    """Apply the explicit two-account reset without secret arguments or logs."""
    try:
        database_url = checked_url(getpass("DATABASE_URL directe Neon (masquée) : "))
        student_password = ask_password("étudiant")
        personnel_password = ask_password("personnel")
        if student_password == personnel_password:
            raise ValueError("Utiliser deux mots de passe distincts.")
    except (ValueError, KeyboardInterrupt):
        print("DEMO_RESET:INPUT_REJECTED")
        return 2

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm", "-i", "--log-driver=none",
                "--entrypoint", "python", IMAGE, "-c", WORKER,
            ],
            input=f"{database_url}\n{student_password}\n{personnel_password}\n".encode("utf-8"),
            capture_output=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        print("DEMO_RESET:RESULT_UNCERTAIN")
        return 1

    output = result.stdout.decode("ascii", errors="replace").strip()
    if result.returncode == 0 and output == "DEMO_RESET:OK":
        print(output)
        return 0
    if output in {"DEMO_RESET:ACCOUNT_MISMATCH", "DEMO_RESET:PASSWORD_RULE"}:
        print(output)
    else:
        print("DEMO_RESET:RESULT_UNCERTAIN")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
