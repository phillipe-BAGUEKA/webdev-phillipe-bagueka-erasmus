"""Prepare public demo rows through the Docker image with masked local input."""

from getpass import getpass
import subprocess
from urllib.parse import parse_qs, unquote, urlsplit


IMAGE = "lab-booking:render-fix"
WORKER = """
import os
import secrets
import sys

database_url = sys.stdin.buffer.readline().decode("utf-8").rstrip("\\r\\n")
student_password = sys.stdin.buffer.readline().decode("utf-8").rstrip("\\r\\n")
personnel_password = sys.stdin.buffer.readline().decode("utf-8").rstrip("\\r\\n")
os.environ["DATABASE_URL"] = database_url
os.environ["DJANGO_SECRET_KEY"] = secrets.token_urlsafe(60)
os.environ["DJANGO_ALLOWED_HOSTS"] = "localhost"
os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://localhost"

demo_conflict_type = ()
validation_error_type = ()
connection = None
try:
    import django
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    from django.db import connection
    validation_error_type = ValidationError

    django.setup()
    from src.data.public_demo import DemoDataConflict, prepare_public_demo
    demo_conflict_type = DemoDataConflict

    validate_password(student_password)
    validate_password(personnel_password)
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
        raise RuntimeError("Unexpected database properties")

    users, laboratories, workstations = prepare_public_demo(
        student_password, personnel_password,
    )
except Exception as error:
    if isinstance(error, validation_error_type):
        print("DEMO_ERROR:PASSWORD_RULE")
    elif isinstance(error, demo_conflict_type):
        print("DEMO_ERROR:EXISTING_DATA")
    else:
        print("DEMO_ERROR:CHECK_OR_CONNECTION")
    sys.exit(1)
else:
    print(f"DEMO_OK:{users}:{laboratories}:{workstations}")
finally:
    try:
        connection.close()
    except Exception:
        pass
"""


def checked_url(raw_url: str) -> str:
    """Accept only this project's direct Neon database with verified TLS."""
    value = raw_url.strip()
    try:
        parsed = urlsplit(value)
        parameters = parse_qs(parsed.query, strict_parsing=True)
        if (
            parsed.scheme not in {"postgres", "postgresql"}
            or not parsed.hostname
            or not parsed.hostname.endswith(".neon.tech")
            or "-pooler." in parsed.hostname
            or unquote(parsed.path) != "/lab_booking"
            or not parsed.username
            or not parsed.password
            or parsed.fragment
            or parsed.port not in (None, 5432)
            or parameters != {
                "sslmode": ["verify-full"],
                "sslrootcert": ["system"],
                "channel_binding": ["require"],
            }
        ):
            raise ValueError
    except ValueError:
        raise ValueError("URL directe Neon non conforme.") from None
    return value


def ask_password(label: str) -> str:
    """Read and confirm a new password without echoing it."""
    first = getpass(f"Nouveau mot de passe {label} : ")
    second = getpass(f"Confirmer le mot de passe {label} : ")
    if first != second or not first:
        raise ValueError("Saisie du mot de passe non confirmée.")
    return first


def main() -> int:
    """Run the one-time idempotent preparation with no secret in arguments."""
    image = subprocess.run(
        ["docker", "image", "inspect", IMAGE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if image.returncode:
        print("Image locale absente ; construire lab-booking:render-fix d'abord.")
        return 2

    try:
        url = checked_url(getpass("DATABASE_URL directe Neon (masquée) : "))
        student_password = ask_password("étudiant")
        personnel_password = ask_password("personnel")
        if student_password == personnel_password:
            raise ValueError("Utiliser deux mots de passe distincts.")
    except (ValueError, KeyboardInterrupt) as error:
        print(str(error) if isinstance(error, ValueError) else "Saisie interrompue.")
        return 2

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm", "-i", "--log-driver=none",
                "--entrypoint", "python", IMAGE, "-c", WORKER,
            ],
            input=f"{url}\n{student_password}\n{personnel_password}\n".encode("utf-8"),
            capture_output=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        print("Préparation interrompue ; vérifier les lignes en base avant de réessayer.")
        return 1

    output = result.stdout.decode("ascii", errors="replace").strip()
    if result.returncode == 0 and output.startswith("DEMO_OK:"):
        parts = output.split(":")
        if len(parts) == 4 and all(part.isdigit() for part in parts[1:]):
            print(
                "Préparation réussie : "
                f"{parts[1]} comptes, {parts[2]} laboratoire, "
                f"{parts[3]} postes créés."
            )
            if parts[1] == "0":
                print(
                    "Comptes existants inchangés ; les mots de passe saisis "
                    "ne les remplacent pas."
                )
            return 0
    if output in {"DEMO_ERROR:PASSWORD_RULE", "DEMO_ERROR:EXISTING_DATA"}:
        print(
            f"Préparation refusée ({output.removeprefix('DEMO_ERROR:')}) ; "
            "aucune mutation partielle."
        )
    else:
        print("Préparation non confirmée ; vérifier les lignes en base avant de réessayer.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
