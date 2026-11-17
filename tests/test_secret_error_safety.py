"""Synthetic credential failures must not appear in CLI or pytest diagnostics."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from unittest.mock import MagicMock, Mock

import psycopg
import pytest

from tools import rotate_postgres_test_password as rotation


def test_pytest_default_traceback_hides_synthetic_connection_arguments(
    tmp_path: Path,
) -> None:
    test_file = tmp_path / "test_fake_connection.py"
    test_file.write_text(
        "import os\nimport psycopg\n"
        "def test_connection():\n"
        "    psycopg.connect(host='127.0.0.1',\n"
        "        port=int(os.environ['SYNTHETIC_PORT']),\n"
        "        user='synthetic_only', dbname='synthetic_only',\n"
        "        password=os.environ['SYNTHETIC_CREDENTIAL'],\n"
        "        connect_timeout=1, passfile='')\n", encoding="utf-8",
    )
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment["DJANGO_SETTINGS_MODULE"] = "tests.settings"
    environment["SYNTHETIC_CREDENTIAL"] = "fake-value-must-never-be-displayed"
    # Reserve a port without listening: never contact any active database.
    with socket.socket() as unused_endpoint:
        unused_endpoint.bind(("127.0.0.1", 0))
        environment["SYNTHETIC_PORT"] = str(unused_endpoint.getsockname()[1])
        command = [sys.executable, "-m", "pytest", "-c",
                   str(rotation.ROOT / "pytest.ini"), str(test_file), "-q"]
        for extra, expected_leak in (([], False), (["--tb=long"], True)):
            result = subprocess.run(
                [*command, *extra], env=environment, cwd=rotation.ROOT,
                text=True, capture_output=True, timeout=20,
            )
            assert result.returncode == 1
            assert "OperationalError" in result.stdout or "ConnectionTimeout" in result.stdout
            leaked = environment["SYNTHETIC_CREDENTIAL"] in result.stdout + result.stderr
            assert leaked is expected_leak


def test_rotation_cli_never_prints_driver_exception(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    sentinel = "synthetic-password-not-for-output"
    monkeypatch.setattr(rotation, "rotate", Mock(side_effect=psycopg.OperationalError(sentinel)))
    assert rotation.main() == 1
    captured = capsys.readouterr()
    assert sentinel not in captured.out + captured.err


def test_rotation_updates_only_test_profile_and_verifies_old_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile = {"name": "test_lab_booking_1a", "user": "lab_booking_1a_test",
               "password": "old-synthetic", "django_key": "unchanged-synthetic"}
    path = tmp_path / "test.json"
    path.write_text(json.dumps(profile))
    monkeypatch.setattr(rotation, "PROFILE", path)
    monkeypatch.setattr(rotation, "RECEIPT", tmp_path / "receipt.json")
    monkeypatch.setattr(rotation, "load_profile", Mock(return_value=profile))
    first, verified = MagicMock(), MagicMock()
    first.__enter__.return_value = first
    verified.__enter__.return_value = verified
    first.cursor.return_value.__enter__.return_value.fetchone.return_value = (
        "lab_booking_1a_test", "test_lab_booking_1a", 5433, "lab_booking_1a",
        "none", "panic", "off", "-1", "-1", "0",
    )
    first.pgconn.encrypt_password.return_value = b"synthetic-scram-verifier"
    verified.cursor.return_value.__enter__.return_value.fetchone.return_value = (
        "lab_booking_1a_test", "test_lab_booking_1a",
    )
    connector = Mock(side_effect=[first, verified, psycopg.OperationalError(
        "password authentication failed",
    )])
    monkeypatch.setattr(rotation, "connect", connector)
    assert rotation.main() == 0
    updated = json.loads(path.read_text())
    assert updated["password"] != profile["password"]
    assert {k: v for k, v in updated.items() if k != "password"} == {
        k: v for k, v in profile.items() if k != "password"
    }
    output = capsys.readouterr()
    assert updated["password"] not in output.out + output.err
    assert json.loads(rotation.RECEIPT.read_text())["old_password_rejected"]
    with pytest.raises(RuntimeError, match="already recorded"):
        rotation.rotate()


def test_rotation_connector_uses_fixed_dedicated_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connector = Mock()
    monkeypatch.setattr(rotation.psycopg, "connect", connector)
    rotation.connect({"password": "synthetic-only"})
    assert connector.call_args.kwargs == {
        "host": "127.0.0.1", "port": 5433, "dbname": "test_lab_booking_1a",
        "user": "lab_booking_1a_test", "password": "synthetic-only",
        "passfile": "", "connect_timeout": 5, "autocommit": True,
    }
