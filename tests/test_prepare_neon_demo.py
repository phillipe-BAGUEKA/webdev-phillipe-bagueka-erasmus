"""The public demo launcher keeps connection credentials out of argv and output."""

import ast
import subprocess
from subprocess import CompletedProcess
import sys

import pytest

from tools import prepare_neon_demo
from tools import check_neon_demo_login, reset_neon_demo_passwords


TEST_URL = (
    "postgresql://demo:synthetic-secret@db.neon.tech/lab_booking"
    "?sslmode=verify-full&sslrootcert=system&channel_binding=require"
)


def test_direct_url_requires_expected_database_and_verified_tls() -> None:
    assert prepare_neon_demo.checked_url(TEST_URL) == TEST_URL
    for invalid in (
        TEST_URL.replace("verify-full", "require"),
        TEST_URL.replace("/lab_booking?", "/other?"),
        TEST_URL.replace("db.neon.tech", "db-pooler.neon.tech"),
        TEST_URL.replace("db.neon.tech", "localhost"),
    ):
        with pytest.raises(ValueError, match="non conforme"):
            prepare_neon_demo.checked_url(invalid)


def test_worker_is_valid_python() -> None:
    ast.parse(prepare_neon_demo.WORKER)


def test_binary_transport_and_workers_handle_windows_crlf() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"],
        input=b"synthetic-line\n",
        capture_output=True,
        check=True,
    )
    assert result.stdout == b"synthetic-line\n"
    for worker in (
        prepare_neon_demo.WORKER,
        check_neon_demo_login.WORKER,
        reset_neon_demo_passwords.WORKER,
    ):
        assert 'rstrip("\\r\\n")' in worker


def test_launcher_passes_secrets_only_on_stdin(monkeypatch, capsys) -> None:
    answers = iter((
        TEST_URL, "student-secret", "student-secret",
        "personnel-secret", "personnel-secret",
    ))
    calls = []

    def fake_run(arguments, **kwargs):
        calls.append((arguments, kwargs))
        if arguments[:3] == ["docker", "image", "inspect"]:
            return CompletedProcess(arguments, 0)
        return CompletedProcess(arguments, 0, b"DEMO_OK:2:1:2\n", b"")

    monkeypatch.setattr(prepare_neon_demo, "getpass", lambda _prompt: next(answers))
    monkeypatch.setattr(prepare_neon_demo.subprocess, "run", fake_run)

    assert prepare_neon_demo.main() == 0
    assert "Préparation réussie" in capsys.readouterr().out
    command, kwargs = calls[1]
    assert command[:3] == ["docker", "run", "--rm"]
    assert "--log-driver=none" in command
    assert kwargs["input"].splitlines() == [
        TEST_URL.encode("utf-8"), b"student-secret", b"personnel-secret",
    ]
    assert b"\r\n" not in kwargs["input"]
    assert kwargs.get("text") is None
    arguments_text = " ".join(command)
    for secret in (TEST_URL, "student-secret", "personnel-secret"):
        assert secret not in arguments_text


def test_launcher_hides_child_errors(monkeypatch, capsys) -> None:
    answers = iter((
        TEST_URL, "student-secret", "student-secret",
        "personnel-secret", "personnel-secret",
    ))

    def fake_run(arguments, **_kwargs):
        if arguments[:3] == ["docker", "image", "inspect"]:
            return CompletedProcess(arguments, 0)
        return CompletedProcess(arguments, 1, b"", b"synthetic-secret trace")

    monkeypatch.setattr(prepare_neon_demo, "getpass", lambda _prompt: next(answers))
    monkeypatch.setattr(prepare_neon_demo.subprocess, "run", fake_run)

    assert prepare_neon_demo.main() == 1
    assert "synthetic-secret" not in capsys.readouterr().out
