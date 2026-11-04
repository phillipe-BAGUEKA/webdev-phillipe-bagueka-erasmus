"""Prepare new, ignored local state without reading or replacing any secret."""

import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEMO_MARKER = "lab-booking-disposable-demo-v1\n"


def prepare_local_state(base_dir: Path) -> None:
    """Create a key only if absent; never adopt an unmarked existing database."""
    data_dir = base_dir / "data"
    marker_path = data_dir / "demo.marker"
    database_path = data_dir / "demo.sqlite3"
    if database_path.exists() and not marker_path.exists():
        raise RuntimeError("Existing unmarked database: refusing to adopt it.")
    data_dir.mkdir(parents=True, exist_ok=True)
    if not marker_path.exists():
        with marker_path.open("x", encoding="utf-8") as marker_file:
            marker_file.write(DEMO_MARKER)

    secret_dir = base_dir / ".local"
    secret_dir.mkdir(exist_ok=True)
    secret_path = secret_dir / "django-dev-key"
    if not secret_path.exists():
        with secret_path.open("x", encoding="utf-8") as secret_file:
            secret_file.write(secrets.token_urlsafe(64))
        secret_path.chmod(0o600)


def main() -> None:
    prepare_local_state(BASE_DIR)
    print("Local state prepared; existing files preserved; no secret displayed.")


if __name__ == "__main__":
    main()
