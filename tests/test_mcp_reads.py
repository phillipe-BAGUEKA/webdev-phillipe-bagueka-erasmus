"""Real stdio reads against committed PostgreSQL fixtures, never demo sessions."""

from contextlib import contextmanager
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
import hashlib
from importlib import import_module
import json
import os
from pathlib import Path
from queue import Queue
import subprocess
import sys
from threading import Thread
from typing import Any, Iterator
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.sessions.models import Session
from django.test import Client

from src.data.models import Booking, Laboratory, User, Workstation
from src.services.access import Actor
from src.services.booking_reads import list_available_slots, list_personal_bookings
from tests.concurrency_helpers import database_identity

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)
START = NOW + timedelta(hours=1)
pytestmark = pytest.mark.django_db(transaction=True)
World = tuple[User, User, Laboratory, Workstation, Client, str]
Request = Callable[[str, dict[str, Any]], dict[str, Any]]


@pytest.fixture
def world() -> World:
    database_identity()
    with patch("django.utils.timezone.now", return_value=NOW):
        owner = User.objects.create_user("mcp-owner@tests.example")
        other = User.objects.create_user("mcp-other@tests.example")
        lab = Laboratory.objects.create(name="MCP test laboratory")
        station = Workstation.objects.create(laboratory=lab, name="Test station")
        Booking.objects.create(owner=owner, workstation=station,
                               starts_at=START, ends_at=START + timedelta(hours=1))
        Booking.objects.create(owner=other, workstation=station,
                               starts_at=START + timedelta(hours=2),
                               ends_at=START + timedelta(hours=3))
        client = Client()
        client.force_login(owner)
    return owner, other, lab, station, client, client.cookies[settings.SESSION_COOKIE_NAME].value


@contextmanager
def server(token: str | None, *, now: datetime = NOW) -> Iterator[Request]:
    """Bound every reply; terminate and reap the child even after a failed test."""
    environment = os.environ.copy()
    environment.pop("LAB_BOOKING_MCP_SESSION", None)
    if token is not None:
        environment["LAB_BOOKING_MCP_SESSION"] = token
    environment["DJANGO_SETTINGS_MODULE"] = "tests.settings_postgres"
    bootstrap = (
        "import runpy,sys\nfrom datetime import datetime,timezone\n"
        "from unittest.mock import patch\n"
        "sys.path.insert(0,'mcp-server')\n"
        "sys.argv=['mcp-server/server.py','--project']\n"
        "with patch('django.utils.timezone.now',return_value="
        f"datetime.fromisoformat({now.isoformat()!r})):\n"
        "    runpy.run_path('mcp-server/server.py',run_name='__main__')\n"
    )
    process = subprocess.Popen(
        [sys.executable, "-c", bootstrap], cwd=ROOT, env=environment,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8",
    )
    replies: Queue[str] = Queue()

    def read_stdout() -> None:
        for line in process.stdout:
            replies.put(line)

    reader = Thread(target=read_stdout, daemon=True)
    reader.start()
    count = 0

    def request(method: str, params: dict[str, Any]) -> dict[str, Any]:
        nonlocal count
        count += 1
        process.stdin.write(json.dumps({
            "jsonrpc": "2.0", "id": count, "method": method, "params": params,
        }) + "\n")
        process.stdin.flush()
        raw = replies.get(timeout=15)
        leaked = token is not None and token in raw
        assert leaked is False
        response = json.loads(raw)
        assert response["id"] == count
        return response

    try:
        request("initialize", {"protocolVersion": "2025-11-25"})
        process.stdin.write(json.dumps({
            "jsonrpc": "2.0", "method": "notifications/initialized",
        }) + "\n")
        process.stdin.flush()
        yield request
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        reader.join(timeout=5)
        diagnostic = process.stderr.read()
        process.stdout.close()
        process.stderr.close()
        leaked = token is not None and token in diagnostic
        assert leaked is False
        assert diagnostic == ""
        assert process.returncode == 0


def payload(response: dict[str, Any], error: str | None = None) -> dict[str, Any]:
    result = response["result"]
    decoded = json.loads(result["content"][0]["text"])
    assert decoded == result["structuredContent"]
    assert result["isError"] == (error is not None)
    if error:
        assert decoded["error"]["code"] == error
        assert decoded["error"]["message"]
    return decoded


def snapshot() -> str:
    """Compare mutations without risking session values in assertion output."""
    rows = [list(Booking.objects.order_by("pk").values()),
            list(Session.objects.order_by("session_key").values())]
    return hashlib.sha256(json.dumps(rows, default=str).encode()).hexdigest()


@pytest.mark.parametrize("_criterion", ["AC-37-AC-39"], ids=str)
def test_AC_37_AC_39_read_catalog_and_personal_history(
    world: World, _criterion: str,
) -> None:
    owner, _, lab, station, client, token = world
    before = snapshot()
    with server(token) as request:
        tools = request("tools/list", {})["result"]["tools"]
        assert [tool["name"] for tool in tools] == [
            "find_lecture", "search_lectures", "list_free_slots", "my_bookings",
            "book_slot", "cancel_booking",
        ]
        for tool in tools[2:]:
            assert len(tool["description"]) >= 20
            assert tool["inputSchema"]["additionalProperties"] is False
        assert tools[2]["inputSchema"]["required"] == ["laboratory_id", "date"]
        assert tools[2]["inputSchema"]["properties"] == {
            "laboratory_id": {"type": "integer", "minimum": 1},
            "date": {"type": "string", "format": "date"},
        }
        assert tools[3]["inputSchema"]["properties"] == {}
        history = payload(request("tools/call", {"name": "my_bookings"}))
        assert len(history["bookings"]) == 1
        assert history["bookings"][0]["id"] == Booking.objects.get(owner=owner).pk
        slots = payload(request("tools/call", {
            "name": "list_free_slots", "arguments": {"laboratory_id": lab.pk, "date": "2030-01-07"},
        }))
        assert slots["slots"]
        assert all(row["workstation_id"] == station.pk for row in slots["slots"])
        assert all(set(row) == {"workstation_id", "workstation_name", "starts_at", "ends_at"}
                   for row in slots["slots"])
        with patch("django.utils.timezone.now", return_value=NOW):
            assert history == client.get("/api/bookings").json()
            assert slots == client.get(f"/api/labs/{lab.pk}/availability?date=2030-01-07").json()
        actor = Actor(owner.pk, owner.email, owner.role, True)
        direct_history = list_personal_bookings(actor, now=NOW)
        assert [row["id"] for row in history["bookings"]] == [
            row.booking_id for row in direct_history
        ]
        direct_slots = list_available_slots(actor, lab.pk, START.date(), now=NOW)
        assert [(row["workstation_id"], datetime.fromisoformat(row["starts_at"]))
                for row in slots["slots"]] == [
            (row.workstation_id, row.starts_at) for row in direct_slots
        ]
    assert snapshot() == before


@pytest.mark.parametrize("token", [None, "z" * 32], ids=["AC-38-absent", "AC-38-invalid"])
def test_AC_38_both_read_tools_refuse_without_session(
    world: World, token: str | None,
) -> None:
    before = snapshot()
    with server(token) as request:
        for name, arguments in (("my_bookings", {}), ("list_free_slots", {
            "laboratory_id": world[2].pk, "date": "2030-01-07",
        })):
            result = payload(request("tools/call", {"name": name, "arguments": arguments}),
                             "AuthenticationRequired")
            assert set(result) == {"error"}
    assert snapshot() == before


@pytest.mark.parametrize("_criterion", ["AC-38"], ids=str)
def test_AC_38_session_revoked_between_calls_in_same_process(
    world: World, _criterion: str,
) -> None:
    *_, client, token = world
    with server(token) as request:
        payload(request("tools/call", {"name": "my_bookings"}))
        client.logout()
        before = snapshot()
        payload(request("tools/call", {"name": "my_bookings"}), "AuthenticationRequired")
        payload(request("tools/call", {"name": "list_free_slots", "arguments": {
            "laboratory_id": world[2].pk, "date": "2030-01-07",
        }}), "AuthenticationRequired")
        assert snapshot() == before


@pytest.mark.parametrize("name,arguments,error", [
    ("my_bookings", {"owner_id": 2}, "InvalidToolInput"),
    ("my_bookings", {"user_id": 2}, "InvalidToolInput"),
    ("my_bookings", [], "InvalidToolInput"),
    ("list_free_slots", {}, "InvalidToolInput"),
    ("list_free_slots", {"laboratory_id": True, "date": "2030-01-07"}, "InvalidToolInput"),
    ("list_free_slots", {"laboratory_id": 1, "date": "2030-02-30"}, "InvalidToolInput"),
    ("list_free_slots", {"laboratory_id": 1, "date": 42}, "InvalidToolInput"),
    ("list_free_slots", {"laboratory_id": 999999, "date": "2030-01-07"}, "LaboratoryNotFound"),
], ids=lambda value: str(value) if isinstance(value, str) else None)
def test_AC_38_AC_39_invalid_arguments_and_domain_refusals(
    world: World, name: str, arguments: object, error: str,
) -> None:
    before = snapshot()
    with server(world[-1]) as request:
        payload(request("tools/call", {"name": name, "arguments": arguments}), error)
    assert snapshot() == before


def test_AC_39_empty_results_are_successful_and_do_not_mutate(world: World) -> None:
    Booking.objects.all().delete()
    before = snapshot()
    with server(world[-1]) as request:
        assert payload(request("tools/call", {"name": "my_bookings"})) == {"bookings": []}
        assert payload(request("tools/call", {"name": "list_free_slots", "arguments": {
            "laboratory_id": world[2].pk, "date": "2030-01-12",
        }})) == {"slots": []}
    assert snapshot() == before


def test_AC_28_AC_39_cancelled_history_keeps_current_station_state(world: World) -> None:
    owner, _, _, station, _, token = world
    Booking.objects.filter(owner=owner).update(cancelled_at=NOW - timedelta(minutes=1))
    Workstation.objects.filter(pk=station.pk).update(is_operational=False)
    before = snapshot()
    with server(token) as request:
        rows = payload(request("tools/call", {"name": "my_bookings"}))["bookings"]
        assert len(rows) == 1
        assert rows[0]["status"] == "cancelled"
        assert rows[0]["cancelled_at"] == "2030-01-07T04:59:00Z"
        assert rows[0]["is_operational"] is False
    assert snapshot() == before


@pytest.mark.parametrize("failure,code", [
    (ValueError, "InternalError"),
    (import_module("src.services.booking_reads").InvalidReadInput, "InvalidReadInput"),
])
def test_AC_39_service_errors_are_sanitized(
    world: World, monkeypatch: pytest.MonkeyPatch,
    failure: type[Exception], code: str,
) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "mcp-server"))
    tools = import_module("project_tools")
    monkeypatch.setenv("LAB_BOOKING_MCP_SESSION", world[-1])
    sentinel = "synthetic-driver-secret-must-not-escape"
    with patch("django.utils.timezone.now", return_value=NOW):
        with patch.object(tools.booking_reads, "list_personal_bookings",
                          side_effect=failure(sentinel)):
            result = tools.call_tool({"name": "my_bookings", "arguments": {}})
    assert result["structuredContent"]["error"]["code"] == code
    assert sentinel not in json.dumps(result)


def test_AC_39_unknown_adapter_name_cannot_trigger_a_read(
    world: World, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "mcp-server"))
    tools = import_module("project_tools")
    monkeypatch.setenv("LAB_BOOKING_MCP_SESSION", world[-1])
    with patch("django.utils.timezone.now", return_value=NOW):
        with patch.object(tools.booking_reads, "list_available_slots") as read:
            result = tools.call_tool({"name": "unknown_read", "arguments": {
                "laboratory_id": world[2].pk, "date": "2030-01-07",
            }})
    assert result["structuredContent"]["error"]["code"] == "InvalidToolInput"
    read.assert_not_called()
