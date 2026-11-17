"""Mutation tools through real stdio and CSRF-protected HTTP on isolated PG."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from importlib import import_module
from typing import Any
from unittest.mock import patch

import pytest
from django.conf import settings
from django.test import Client

from src.data.models import Booking, Laboratory, User, Workstation
from tests.concurrency_helpers import database_identity
from tests.test_mcp_reads import NOW, ROOT, START, payload, server, snapshot

pytestmark = pytest.mark.django_db(transaction=True)


@dataclass
class World:
    owner: User
    other: User
    first: Workstation
    second: Workstation
    client: Client
    token: str


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch) -> World:
    database_identity()
    monkeypatch.setattr("django.utils.timezone.now", lambda: NOW)
    owner = User.objects.create_user("mcp-mutation-owner@tests.example")
    other = User.objects.create_user("mcp-mutation-other@tests.example")
    lab = Laboratory.objects.create(name="MCP mutation test laboratory")
    first = Workstation.objects.create(laboratory=lab, name="A")
    second = Workstation.objects.create(laboratory=lab, name="B")
    client = Client(enforce_csrf_checks=True)
    client.get("/login")
    client.force_login(owner)
    token = client.cookies[settings.SESSION_COOKIE_NAME].value
    return World(owner, other, first, second, client, token)


def body(station: Workstation, start: datetime = START) -> dict[str, Any]:
    return {
        "workstation_id": station.pk, "starts_at": start.isoformat(),
        "ends_at": (start + timedelta(hours=1)).isoformat(),
    }


def stored(user: User, station: Workstation, start: datetime = START) -> Booking:
    return Booking.objects.create(
        owner=user, workstation=station, starts_at=start,
        ends_at=start + timedelta(hours=1),
    )


def state() -> list[dict[str, Any]]:
    """Ignore generated IDs only when comparing independently replayed creations."""
    return list(Booking.objects.order_by("pk").values(
        "owner_id", "workstation_id", "starts_at", "ends_at", "created_at",
        "cancelled_at",
    ))


def http_post(client: Client, path: str, arguments: dict[str, Any],
              now: datetime = NOW) -> Any:
    with patch("django.utils.timezone.now", return_value=now):
        return client.post(
            path, json.dumps(arguments), content_type="application/json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )


def restore(rows: list[dict[str, Any]]) -> None:
    """Replay the same baseline only on the already verified test database."""
    Booking.objects.all().delete()
    Booking.objects.bulk_create([Booking(**row) for row in rows])


@pytest.mark.parametrize("_criterion", ["AC-37"], ids=str)
def test_AC_37_six_tools_and_mutation_schemas(world: World, _criterion: str) -> None:
    with server(None) as request:
        tools = request("tools/list", {})["result"]["tools"]
    assert [tool["name"] for tool in tools] == [
        "find_lecture", "search_lectures", "list_free_slots", "my_bookings",
        "book_slot", "cancel_booking",
    ]
    for tool in tools[2:]:
        assert len(tool["description"]) >= 20
        assert tool["inputSchema"]["additionalProperties"] is False
    create, cancel = tools[-2:]
    assert create["inputSchema"]["required"] == [
        "workstation_id", "starts_at", "ends_at",
    ]
    assert create["inputSchema"]["properties"] == {
        "workstation_id": {"type": "integer", "minimum": 1},
        "starts_at": {"type": "string", "format": "date-time"},
        "ends_at": {"type": "string", "format": "date-time"},
    }
    assert cancel["inputSchema"]["required"] == ["booking_id"]
    assert cancel["inputSchema"]["properties"] == {
        "booking_id": {"type": "integer", "minimum": 1},
    }
    assert create["annotations"]["idempotentHint"] is False
    assert cancel["annotations"]["idempotentHint"] is True
    assert create["annotations"]["readOnlyHint"] is False
    assert cancel["annotations"]["readOnlyHint"] is False
    assert create["annotations"]["destructiveHint"] is False
    assert cancel["annotations"]["destructiveHint"] is True


@pytest.mark.parametrize("case,error,status", [
    ("valid", None, 201),
    ("workstation", "WorkstationConflict", 409),
    ("personal", "PersonalConflict", 409),
    ("quota", "QuotaExceeded", 409),
    ("role", "StudentRequired", 403),
    ("inactive", "AuthenticationRequired", 401),
    ("offline", "WorkstationUnavailable", 409),
    ("missing", "WorkstationNotFound", 404),
    ("duration", "InvalidBookingInput", 422),
    ("weekend", "InvalidBookingInput", 422),
    ("outside-hours", "InvalidBookingInput", 422),
    ("not-future", "SlotNotFuture", 422),
    ("past", "SlotNotFuture", 422),
    ("half-hour", "InvalidBookingInput", 422),
], ids=[
    "AC-15-AC-39-valid", "AC-17-AC-39-workstation", "AC-18-AC-39-personal",
    "AC-20-AC-39-quota", "AC-39-role", "AC-38-AC-39-inactive",
    "AC-11-AC-39-offline", "AC-39-missing", "AC-16-AC-39-duration",
    "AC-16-AC-39-weekend", "AC-16-AC-39-outside-hours",
    "AC-16-AC-39-now", "AC-16-AC-39-past", "AC-16-AC-39-half-hour",
])
def test_AC_11_AC_15_AC_17_AC_18_AC_20_AC_39_creation_parity(
    world: World, case: str, error: str | None, status: int,
) -> None:
    arguments = body(world.first)
    instant = NOW
    if case == "workstation":
        stored(world.other, world.first)
    elif case == "personal":
        stored(world.owner, world.second)
    elif case == "quota":
        for offset in (2, 3, 4):
            stored(world.owner, world.second, START + timedelta(hours=offset))
    elif case == "role":
        world.owner.role = "personnel"
        world.owner.save(update_fields=["role"])
    elif case == "inactive":
        world.owner.is_active = False
        world.owner.save(update_fields=["is_active"])
    elif case == "offline":
        Workstation.objects.filter(pk=world.first.pk).update(is_operational=False)
    elif case == "missing":
        arguments["workstation_id"] = 999999
    elif case == "duration":
        arguments["ends_at"] = (START + timedelta(hours=2)).isoformat()
    elif case == "weekend":
        arguments = body(world.first, START + timedelta(days=5))
    elif case == "outside-hours":
        arguments = body(world.first, START - timedelta(hours=1))
    elif case == "not-future":
        instant = START
    elif case == "past":
        instant = START + timedelta(minutes=1)
    elif case == "half-hour":
        arguments = body(world.first, START + timedelta(minutes=30))
    baseline = list(Booking.objects.order_by("pk").values())
    before = snapshot()
    with server(world.token, now=instant) as request:
        result = payload(request("tools/call", {
            "name": "book_slot", "arguments": arguments,
        }), error)
    mcp_state = state()
    if error is None:
        assert len(mcp_state) == len(baseline) + 1
        row = Booking.objects.get(pk=result["booking"]["id"])
        assert row.owner_id == world.owner.pk
        assert row.workstation_id == world.first.pk
        assert row.starts_at == START
        assert row.cancelled_at is None
    else:
        assert snapshot() == before
    restore(baseline)
    response = http_post(world.client, "/api/bookings", arguments, instant)
    assert response.status_code == status
    assert state() == mcp_state
    if error is None:
        http_booking = response.json()["booking"]
        assert {k: v for k, v in http_booking.items() if k != "id"} == {
            k: v for k, v in result["booking"].items() if k != "id"
        }
    else:
        assert list(Booking.objects.order_by("pk").values()) == baseline
        if status == 403:
            assert response.json()["error"] == "Seuls les étudiants peuvent réserver."


@pytest.mark.parametrize("case,error,status", [
    ("valid", None, 200), ("offline", None, 200),
    ("foreign", "NotBookingOwner", 403),
    ("foreign-cancelled", "NotBookingOwner", 403),
    ("equal", "CancellationTooLate", 409),
    ("after", "CancellationTooLate", 409),
    ("repeat-after-start", None, 200),
    ("missing", "BookingNotFound", 404),
], ids=[
    "AC-25-AC-28-AC-39-owner", "AC-25-AC-28-AC-39-offline",
    "AC-27-AC-39-other", "AC-27-AC-39-other-cancelled",
    "AC-26-AC-39-equal", "AC-26-AC-39-after",
    "AC-28-AC-39-repeat", "AC-39-missing",
])
def test_AC_25_AC_26_AC_27_AC_28_AC_39_cancellation_parity(
    world: World, case: str, error: str | None, status: int,
) -> None:
    owner = world.other if case.startswith("foreign") else world.owner
    row = stored(owner, world.first)
    if case in {"foreign-cancelled", "repeat-after-start"}:
        Booking.objects.filter(pk=row.pk).update(
            created_at=NOW - timedelta(minutes=2),
            cancelled_at=NOW - timedelta(minutes=1),
        )
        row.refresh_from_db()
    if case == "offline":
        Workstation.objects.filter(pk=world.first.pk).update(is_operational=False)
    instant = START if case == "equal" else NOW
    if case in {"after", "repeat-after-start"}:
        instant = START + timedelta(minutes=1)
    booking_id = 999999 if case == "missing" else row.pk
    baseline = list(Booking.objects.order_by("pk").values())
    expected_timestamp = row.cancelled_at or instant
    before = snapshot()
    with server(world.token, now=instant) as request:
        result = payload(request("tools/call", {
            "name": "cancel_booking", "arguments": {"booking_id": booking_id},
        }), error)
        if error is None:
            row.refresh_from_db()
            first_timestamp = row.cancelled_at
            assert first_timestamp == expected_timestamp
            expected_row = {**baseline[0], "cancelled_at": expected_timestamp}
            assert Booking.objects.values().get(pk=row.pk) == expected_row
            after_first = snapshot()
            repeated = payload(request("tools/call", {
                "name": "cancel_booking", "arguments": {"booking_id": row.pk},
            }))
            assert repeated == result
            assert snapshot() == after_first
            row.refresh_from_db()
            assert row.cancelled_at == first_timestamp
            assert result["booking"]["id"] == row.pk
            history = payload(request("tools/call", {"name": "my_bookings"}))
            assert [item["id"] for item in history["bookings"]] == [row.pk]
            assert history["bookings"][0]["status"] == "cancelled"
            assert snapshot() == after_first
        else:
            assert snapshot() == before
    mcp_state = state()
    assert Booking.objects.count() == 1
    restore(baseline)
    response = http_post(world.client, f"/api/bookings/{booking_id}/cancel", {}, instant)
    assert response.status_code == status
    assert state() == mcp_state
    if error is None:
        assert response.json() == result
    else:
        assert list(Booking.objects.order_by("pk").values()) == baseline
        if status == 403:
            assert response.json()["error"] == "Tu ne peux annuler que tes propres réservations."


@pytest.mark.parametrize("token", [None, "x" * 32], ids=["AC-38-absent", "AC-38-invalid"])
def test_AC_38_mutations_refuse_without_session(world: World, token: str | None) -> None:
    row = stored(world.owner, world.first)
    before = snapshot()
    with server(token) as request:
        for name, arguments in (("book_slot", body(world.second)), (
            "cancel_booking", {"booking_id": row.pk},
        )):
            result = payload(request("tools/call", {
                "name": name, "arguments": arguments,
            }), "AuthenticationRequired")
            assert set(result) == {"error"}
    assert snapshot() == before


@pytest.mark.parametrize("_criterion", ["AC-38"], ids=str)
def test_AC_38_revocation_blocks_both_mutations_in_same_process(
    world: World, _criterion: str,
) -> None:
    with server(world.token) as request:
        result = payload(request("tools/call", {
            "name": "book_slot", "arguments": body(world.first),
        }))
        world.client.logout()
        before = snapshot()
        for name, arguments in (("book_slot", body(world.second)), (
            "cancel_booking", {"booking_id": result["booking"]["id"]},
        )):
            payload(request("tools/call", {"name": name, "arguments": arguments}),
                    "AuthenticationRequired")
    assert snapshot() == before


@pytest.mark.parametrize("name,extra", [
    ("book_slot", "owner_id"), ("book_slot", "user_id"),
    ("cancel_booking", "owner_id"), ("cancel_booking", "user_id"),
], ids=["AC-38-AC-39-book-owner", "AC-38-AC-39-book-user",
        "AC-38-AC-39-cancel-owner", "AC-38-AC-39-cancel-user"])
def test_AC_38_AC_39_client_identity_is_refused(
    world: World, name: str, extra: str,
) -> None:
    row = stored(world.owner, world.first)
    arguments = body(world.second) if name == "book_slot" else {"booking_id": row.pk}
    arguments[extra] = world.other.pk
    before = snapshot()
    with server(world.token) as request:
        payload(request("tools/call", {"name": name, "arguments": arguments}),
                "InvalidToolInput")
    assert snapshot() == before


@pytest.mark.parametrize("arguments", [
    {}, {"workstation_id": True, "starts_at": "2030-01-07T06:00:00Z", "ends_at": "2030-01-07T07:00:00Z"},
    {"workstation_id": 1, "starts_at": "2030-01-07T06:00:00", "ends_at": "2030-01-07T07:00:00Z"},
    {"workstation_id": 1, "starts_at": "bad", "ends_at": "2030-01-07T07:00:00Z"},
    {"workstation_id": 1, "starts_at": 42, "ends_at": "2030-01-07T07:00:00Z"},
    {"workstation_id": 1, "starts_at": "2030-02-30T06:00:00Z", "ends_at": "2030-02-30T07:00:00Z"},
], ids=["AC-16-AC-39-empty", "AC-16-AC-39-bool", "AC-16-AC-39-naive",
        "AC-16-AC-39-malformed", "AC-16-AC-39-type", "AC-16-AC-39-calendar"])
def test_AC_39_creation_shape_refusals(world: World, arguments: dict[str, Any]) -> None:
    before = snapshot()
    with server(world.token) as request:
        payload(request("tools/call", {"name": "book_slot", "arguments": arguments}),
                "InvalidToolInput")
    assert snapshot() == before


@pytest.mark.parametrize("arguments", [{}, {"booking_id": False}, {"booking_id": 0}],
                         ids=["AC-39-empty", "AC-39-bool", "AC-39-zero"])
def test_AC_39_cancel_shape_refusals(world: World, arguments: dict[str, Any]) -> None:
    before = snapshot()
    with server(world.token) as request:
        payload(request("tools/call", {"name": "cancel_booking", "arguments": arguments}),
                "InvalidToolInput")
    assert snapshot() == before


@pytest.mark.parametrize("_criterion", ["AC-39"], ids=str)
def test_AC_39_adapter_repetition_performs_only_one_state_write(
    world: World, monkeypatch: pytest.MonkeyPatch, _criterion: str,
) -> None:
    from src.data import booking_cancellation as data

    monkeypatch.syspath_prepend(str(ROOT / "mcp-server"))
    tools = import_module("project_tools")
    monkeypatch.setenv("LAB_BOOKING_MCP_SESSION", world.token)
    row = stored(world.owner, world.first)
    parameters = {"name": "cancel_booking", "arguments": {"booking_id": row.pk}}
    with patch.object(data, "mark_cancelled", wraps=data.mark_cancelled) as write:
        first = tools.call_tool(parameters)
        second = tools.call_tool(parameters)
    assert first["isError"] is False
    assert first == second
    assert write.call_count == 1


@pytest.mark.parametrize("known", [True, False], ids=["AC-39-known", "AC-39-unknown"])
def test_AC_39_mutation_error_details_are_not_disclosed(
    world: World, monkeypatch: pytest.MonkeyPatch, known: bool,
) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "mcp-server"))
    tools = import_module("project_tools")
    monkeypatch.setenv("LAB_BOOKING_MCP_SESSION", world.token)
    error_type = (
        tools.booking_cancellation.BookingChanged if known
        else tools.booking_creation.BookingError
    )
    sentinel = "synthetic-private-driver-detail"
    before = snapshot()
    with patch.object(tools.booking_cancellation, "cancel_booking",
                      side_effect=error_type(sentinel)):
        result = tools.call_tool({"name": "cancel_booking", "arguments": {"booking_id": 1}})
    assert result["isError"] is True
    assert result["structuredContent"]["error"]["code"] == (
        "BookingChanged" if known else "InternalError"
    )
    assert sentinel not in json.dumps(result)
    assert snapshot() == before
