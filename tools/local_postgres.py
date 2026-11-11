"""Manage only the user-owned Lab booking cluster; never the Windows service."""

import argparse
import getpass
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import warnings

import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.setup_postgres import EXPECTED_DATA, provision, restrict_profile_permissions

BIN = Path(r"C:\Program Files\PostgreSQL\16\bin")
DATA = EXPECTED_DATA
PROFILE = ROOT / ".local" / "postgres-1a-bootstrap.json"
PORT = 5433


def run_pg(program: str, *arguments: str) -> None:
    """Suppress subprocess output; arguments never contain a password."""
    subprocess.run(
        [str(BIN / program), *arguments], check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def write_private(path: Path, value: dict) -> None:
    """Create an empty private file before writing newly authorized secrets."""
    with path.open("x", encoding="utf-8") as handle:
        restrict_profile_permissions(path)
        json.dump(value, handle)


def start() -> None:
    """Start this cluster only, without registering any Windows service."""
    run_pg(
        "pg_ctl.exe", "-D", str(DATA), "-l", str(DATA / "server.log"),
        "-o", "-h 127.0.0.1 -p 5433 -c cluster_name=lab_booking_1a "
        "-c log_statement=none -c log_min_error_statement=panic",
        "-w", "start",
    )


def connect() -> psycopg.Connection:
    """Use exclusively the new bootstrap profile for the isolated cluster."""
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    connection = psycopg.connect(
        host="127.0.0.1", port=PORT, dbname="postgres",
        user=profile["user"], password=profile["password"], passfile="",
        connect_timeout=5, autocommit=True,
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_setting('data_directory'), "
                       "current_setting('cluster_name'), current_setting('port')")
        directory, name, port = cursor.fetchone()
    if Path(directory).resolve() != DATA.resolve() or (name, port) != ("lab_booking_1a", "5433"):
        connection.close()
        raise RuntimeError("Unexpected PostgreSQL identity.")
    return connection


def initialize() -> None:
    """Initialize once using a temporary private initdb password file."""
    if DATA.exists() or PROFILE.exists():
        raise RuntimeError("Refusing an existing data directory or bootstrap profile.")
    if any((ROOT / ".local" / f"postgres-1a-{kind}.json").exists()
           for kind in ("dev", "test")):
        raise RuntimeError("Refusing existing application profiles.")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", PORT))
    if not sys.stdin.isatty():
        raise RuntimeError("Initialization requires a terminal with masked input.")
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        password = getpass.getpass("New dedicated bootstrap password (hidden): ")
    if not password or "\n" in password or "\r" in password:
        raise RuntimeError("Invalid initialization input.")
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.mkdir()
    restrict_profile_permissions(DATA)
    PROFILE.parent.mkdir(exist_ok=True)
    write_private(PROFILE, {"user": "lab_booking_bootstrap", "password": password})
    descriptor, temporary_name = tempfile.mkstemp(
        prefix="lab-booking-initdb-", dir=PROFILE.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            restrict_profile_permissions(temporary)
            handle.write(password + "\n")
        run_pg(
            "initdb.exe", "-D", str(DATA), "--encoding=UTF8", "--locale=C",
            "--username=lab_booking_bootstrap", "--auth-local=scram-sha-256",
            "--auth-host=scram-sha-256", "--pwfile=" + str(temporary),
        )
    finally:
        # Only this operation's exact temporary file is authorized for deletion.
        temporary.unlink(missing_ok=True)
    password = ""
    start()
    with connect() as connection:
        provision(connection)
    print("Dedicated cluster initialized and provisioned on 127.0.0.1:5433.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=("init", "provision", "start", "stop", "status", "verify")
    )
    action = parser.parse_args().action
    try:
        if action == "init":
            initialize()
        elif action == "provision":
            with connect() as connection:
                provision(connection)
        elif action == "start":
            start()
        elif action == "stop":
            with connect():
                pass
            run_pg("pg_ctl.exe", "-D", str(DATA), "-m", "fast", "-w", "stop")
        else:
            with connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    print(cursor.fetchone()[0])
            print("Verified dedicated Lab booking instance: 127.0.0.1:5433.")
    except Exception as error:
        print(f"Operation stopped ({type(error).__name__}); no secrets displayed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
