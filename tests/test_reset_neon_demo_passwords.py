"""The two-account reset is explicit and never exposes its masked inputs."""

import ast
from subprocess import CompletedProcess

from tools import reset_neon_demo_passwords


TEST_URL = (
    "postgresql://demo:synthetic-secret@db.neon.tech/lab_booking"
    "?sslmode=verify-full&sslrootcert=system&channel_binding=require"
)


def test_reset_worker_uses_only_the_named_data_function() -> None:
    ast.parse(reset_neon_demo_passwords.WORKER)
    assert "reset_public_demo_passwords(student_password, personnel_password)" in (
        reset_neon_demo_passwords.WORKER
    )


def test_reset_passes_secrets_only_on_stdin(monkeypatch, capsys) -> None:
    calls = []

    def fake_run(arguments, **kwargs):
        calls.append((arguments, kwargs))
        return CompletedProcess(arguments, 0, b"DEMO_RESET:OK\n", b"")

    monkeypatch.setattr(reset_neon_demo_passwords, "getpass", lambda _prompt: TEST_URL)
    monkeypatch.setattr(
        reset_neon_demo_passwords,
        "ask_password",
        lambda label: "student-synthetic" if label == "étudiant" else "personnel-synthetic",
    )
    monkeypatch.setattr(reset_neon_demo_passwords.subprocess, "run", fake_run)

    assert reset_neon_demo_passwords.main() == 0
    assert capsys.readouterr().out.strip() == "DEMO_RESET:OK"
    arguments, kwargs = calls[0]
    assert arguments[:3] == ["docker", "run", "--rm"]
    assert "--log-driver=none" in arguments
    assert kwargs["input"].splitlines() == [
        TEST_URL.encode("utf-8"), b"student-synthetic", b"personnel-synthetic",
    ]
    assert b"\r\n" not in kwargs["input"]
    assert kwargs.get("text") is None
    for secret in (TEST_URL, "student-synthetic", "personnel-synthetic"):
        assert secret not in " ".join(arguments)


def test_reset_does_not_echo_child_error(monkeypatch, capsys) -> None:
    def fake_run(arguments, **_kwargs):
        return CompletedProcess(arguments, 1, b"", b"synthetic-secret trace")

    monkeypatch.setattr(reset_neon_demo_passwords, "getpass", lambda _prompt: TEST_URL)
    monkeypatch.setattr(
        reset_neon_demo_passwords,
        "ask_password",
        lambda label: "student-synthetic" if label == "étudiant" else "personnel-synthetic",
    )
    monkeypatch.setattr(reset_neon_demo_passwords.subprocess, "run", fake_run)

    assert reset_neon_demo_passwords.main() == 1
    assert capsys.readouterr().out.strip() == "DEMO_RESET:RESULT_UNCERTAIN"
