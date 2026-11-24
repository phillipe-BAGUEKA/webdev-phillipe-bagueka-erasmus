"""The read-only account diagnosis does not disclose masked inputs."""

import ast
from subprocess import CompletedProcess

from tools import check_neon_demo_login
from tools.prepare_neon_demo import IMAGE


TEST_URL = (
    "postgresql://demo:synthetic-secret@db.neon.tech/lab_booking"
    "?sslmode=verify-full&sslrootcert=system&channel_binding=require"
)


def test_check_worker_is_valid_python() -> None:
    ast.parse(check_neon_demo_login.WORKER)
    assert "authenticate_user(STUDENT_EMAIL, password)" in check_neon_demo_login.WORKER


def test_check_passes_credentials_only_on_stdin(monkeypatch, capsys) -> None:
    answers = iter((TEST_URL, "student-synthetic-password"))
    calls = []

    def fake_run(arguments, **kwargs):
        calls.append((arguments, kwargs))
        return CompletedProcess(arguments, 0, b"DEMO_LOGIN:LOGIN_VALID:catalogue=1/2\n", b"")

    monkeypatch.setattr(check_neon_demo_login, "getpass", lambda _prompt: next(answers))
    monkeypatch.setattr(check_neon_demo_login.subprocess, "run", fake_run)

    assert check_neon_demo_login.main() == 0
    assert capsys.readouterr().out.strip() == "DEMO_LOGIN:LOGIN_VALID:catalogue=1/2"
    arguments, kwargs = calls[0]
    assert arguments[:3] == ["docker", "run", "--rm"]
    assert "--log-driver=none" in arguments
    assert IMAGE in arguments
    assert kwargs["input"].splitlines() == [
        TEST_URL.encode("utf-8"), b"student-synthetic-password",
    ]
    assert b"\r\n" not in kwargs["input"]
    assert kwargs.get("text") is None
    assert TEST_URL not in " ".join(arguments)
    assert "student-synthetic-password" not in " ".join(arguments)


def test_check_masks_child_errors_and_unexpected_output(monkeypatch, capsys) -> None:
    answers = iter((TEST_URL, "student-synthetic-password"))

    def fake_run(arguments, **_kwargs):
        return CompletedProcess(arguments, 1, b"unexpected synthetic-secret", b"secret trace")

    monkeypatch.setattr(check_neon_demo_login, "getpass", lambda _prompt: next(answers))
    monkeypatch.setattr(check_neon_demo_login.subprocess, "run", fake_run)

    assert check_neon_demo_login.main() == 1
    assert capsys.readouterr().out.strip() == "DEMO_LOGIN:CHECK_FAILED"
