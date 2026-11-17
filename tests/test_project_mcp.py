"""Opt-in stdio bootstrap and session adapter, preserving the default TP1 mode."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
from types import ModuleType
from unittest.mock import patch

import pytest
from django.conf import settings
from django.db import OperationalError, connection
from django.test import Client

from src.data.models import User
from src.services.access import AuthenticationRequired

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp-server" / "server.py"


def runtime() -> ModuleType:
    """Load the hyphenated server directory without adding a Python package."""
    spec = importlib.util.spec_from_file_location(
        "mcp_project_runtime", SERVER.with_name("project_runtime.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exchange(
    *arguments: str, profile: str, stdlib_only: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a real stdio exchange without inheriting any real session token."""
    environment = os.environ.copy()
    environment.pop("LAB_BOOKING_MCP_SESSION", None)
    environment["DJANGO_SETTINGS_MODULE"] = profile
    lines = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-11-25"}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "find_lecture", "arguments": {"number": 5}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "my_bookings", "arguments": {}}},
    ]
    command = [sys.executable]
    if stdlib_only:
        command.append("-S")
    return subprocess.run(
        [*command, str(SERVER), *arguments], cwd=ROOT, env=environment,
        input="\n".join(json.dumps(line) for line in lines) + "\n",
        text=True, encoding="utf-8", capture_output=True, timeout=20,
    )


def assert_catalog(
    result: subprocess.CompletedProcess, project: bool = False,
) -> None:
    assert result.returncode == 0
    assert result.stderr == ""
    replies = [json.loads(line) for line in result.stdout.splitlines()]
    assert [row["id"] for row in replies] == [1, 2, 3, 4]
    assert replies[0]["result"]["protocolVersion"] == "2025-11-25"
    names = ["find_lecture", "search_lectures"]
    if project:
        names += ["list_free_slots", "my_bookings", "book_slot", "cancel_booking"]
    assert [tool["name"] for tool in replies[1]["result"]["tools"]] == names
    assert "Lecture 5:" in replies[2]["result"]["content"][0]["text"]
    if project:
        assert replies[3]["result"]["isError"] is True
        assert replies[3]["result"]["structuredContent"]["error"]["code"] == (
            "AuthenticationRequired"
        )
    else:
        assert replies[3]["error"]["code"] == -32602


def test_AC_37_partial_default_stdio_needs_no_django_or_database() -> None:
    assert_catalog(exchange(profile="unavailable.settings", stdlib_only=True))


@pytest.mark.django_db(transaction=True)
def test_AC_37_partial_project_stdio_starts_without_a_session() -> None:
    assert connection.vendor == "postgresql"
    assert connection.settings_dict["NAME"] == "test_lab_booking_1a"
    assert_catalog(exchange("--project", profile="tests.settings_postgres"), project=True)


@pytest.mark.parametrize("profile", ["tests.settings", "missing.settings"])
def test_project_startup_refuses_bad_configuration_without_trace(profile: str) -> None:
    result = exchange("--project", profile=profile)
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip() == (
        "Project initialization failed; check local configuration."
    )


def test_unknown_cli_argument_is_not_echoed() -> None:
    result = exchange("--not-supported", profile="missing.settings")
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip() == "Usage: server.py [--project]"


@pytest.mark.django_db
def test_AC_38_runtime_revalidates_in_same_process(
    active_student: User, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = runtime()
    monkeypatch.delenv("LAB_BOOKING_MCP_SESSION", raising=False)
    with pytest.raises(AuthenticationRequired):
        module.current_actor()
    client = Client()
    client.force_login(active_student)
    key = client.cookies[settings.SESSION_COOKIE_NAME].value
    monkeypatch.setenv("LAB_BOOKING_MCP_SESSION", key)
    assert module.current_actor().user_id == active_student.pk
    client.logout()
    with pytest.raises(AuthenticationRequired):
        module.current_actor()
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""


def test_AC_38_runtime_database_failure_is_sanitized() -> None:
    module = runtime()
    sentinel = "synthetic-driver-detail-must-not-escape"
    with patch(
        "src.services.session_auth.authenticate_session",
        side_effect=OperationalError(sentinel),
    ):
        with pytest.raises(module.SessionAuthenticationUnavailable) as caught:
            module.current_actor()
    assert str(caught.value) == "Session authentication unavailable."
    rendered = "".join(traceback.format_exception(caught.value))
    assert sentinel not in rendered
    assert caught.value.__suppress_context__
