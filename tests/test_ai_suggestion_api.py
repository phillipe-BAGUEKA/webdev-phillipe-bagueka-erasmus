"""Protected API, real PostgreSQL services, synthetic clients and no provider."""

import json
from datetime import datetime, timezone
from typing import Any

import pytest
from django.db import connection
from django.test import Client

from src.data.models import Booking, Laboratory, User, Workstation
from tests.test_ai_suggestion import FakeClient

NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def forbid_real_transport(monkeypatch: Any) -> None:
    def refuse(*args: Any, **kwargs: Any) -> None:
        pytest.fail("Real provider adapter forbidden in API tests.")

    monkeypatch.setattr("src.integrations.gemini.GeminiClient.select_candidate", refuse)


def snapshot() -> tuple[Any, ...]:
    return tuple(list(model.objects.order_by("pk").values())
                 for model in (User, Laboratory, Workstation, Booking))


@pytest.fixture
def world(db: None, monkeypatch: Any) -> tuple[Any, ...]:
    assert connection.vendor == "postgresql"
    user = User.objects.create_user("ai-api@tests.example")
    lab = Laboratory.objects.create(name="AI API test lab")
    station = Workstation.objects.create(laboratory=lab, name="A")
    client = Client(enforce_csrf_checks=True)
    client.get("/login")
    client.force_login(user)
    # Replace the configuration factory, never inspect real environment keys.
    monkeypatch.setattr("src.routes.ai_suggestion.configured_client", lambda: FakeClient())
    monkeypatch.setattr("src.routes.ai_suggestion.business_clock", lambda: NOW)
    return user, lab, station, client


def post(world: tuple[Any, ...], payload: Any = None, **kwargs: Any) -> Any:
    _, lab, _, client = world
    return client.post(f"/api/labs/{lab.pk}/suggestion",
                       data=json.dumps({"date": "2030-01-07", "need": "A desk"}
                                       if payload is None else payload),
                       content_type="application/json",
                       HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value, **kwargs)


@pytest.mark.parametrize("label", ["AC-29-AC-31-AC-32-API"])
def test_success_uses_real_service_without_booking(world: tuple[Any, ...], label: str) -> None:
    _, _, station, _ = world
    before = snapshot()
    result = post(world)
    assert result.status_code == 200
    assert result.json()["status"] == "suggested"
    assert result.json()["candidate"]["workstation_id"] == station.pk
    assert result.json()["candidate"]["starts_at"] == "2030-01-07T06:00:00Z"
    assert not Booking.objects.exists()
    assert "no-store" in result.headers["Cache-Control"]
    assert snapshot() == before


@pytest.mark.parametrize("case,status", [("anonymous", 401), ("inactive", 401),
                                        ("staff", 403), ("csrf", 403)],
                         ids=lambda value: f"AC-29-API-{value}")
def test_permissions_and_csrf(world: tuple[Any, ...], case: str, status: int) -> None:
    user, lab, _, client = world
    if case == "anonymous":
        client.logout()
        client.get("/login")  # Real CSRF token, so the 401 is not a CSRF refusal.
    elif case == "inactive":
        user.is_active = False
        user.save()
    elif case == "staff":
        user.role = "personnel"
        user.save()
    if case == "csrf":
        result = client.post(f"/api/labs/{lab.pk}/suggestion", data="{}", content_type="application/json")
    else:
        result = post(world)
    assert result.status_code == status
    assert result.headers["Content-Type"] == "application/json"
    assert "error" in result.json()
    assert not Booking.objects.exists()


@pytest.mark.parametrize("body", [
    {"date": "2030-01-07", "need": "x" * 1001},
    {"date": "2030-01-07", "need": ""}, {"date": "bad", "need": "desk"},
    {"date": "2030-01-07", "need": "desk", "owner_id": 1},
    {"date": "2030-01-07", "need": 1},
], ids=[f"AC-29-API-invalid-{n}" for n in range(5)])
def test_invalid_input(world: tuple[Any, ...], body: Any) -> None:
    assert post(world, body).status_code == 422
    assert not Booking.objects.exists()


@pytest.mark.parametrize("label", ["AC-30-API-empty"])
def test_no_candidates_no_invocation(world: tuple[Any, ...], monkeypatch: Any, label: str) -> None:
    fake = FakeClient(action=lambda: pytest.fail("client must not be called"))
    monkeypatch.setattr("src.routes.ai_suggestion.configured_client", lambda: fake)
    result = post(world, {"date": "2030-01-06", "need": "desk"})
    assert result.status_code == 200
    assert result.json()["status"] == "no_candidates"
    assert result.json()["candidate"] is None and not fake.calls


@pytest.mark.parametrize("failure,status", [("missing", 503), ("quota", 503),
                                           ("error", 503), ("timeout", 504), ("invalid", 502)],
                         ids=lambda value: f"AC-33-AC-35-AC-36-API-{value}")
def test_safe_failure(world: tuple[Any, ...], monkeypatch: Any, failure: str, status: int,
                      caplog: Any) -> None:
    from src.services.ai_suggestion import ClientQuotaExceeded

    def fail() -> None:
        raise {"quota": ClientQuotaExceeded, "error": RuntimeError,
               "timeout": TimeoutError}[failure]("synthetic-sensitive-data")

    fake = None if failure == "missing" else FakeClient(
        output={} if failure == "invalid" else {"candidate_id": "c1"},
        action=fail if failure in {"quota", "error", "timeout"} else None,
    )
    monkeypatch.setattr("src.routes.ai_suggestion.configured_client", lambda: fake)
    before = snapshot()
    result = post(world)
    assert result.status_code == status
    assert result.json()["status"] == "unavailable"
    assert result.json()["candidate"] is None
    assert "synthetic-sensitive" not in result.content.decode() + caplog.text
    assert not Booking.objects.exists()
    assert snapshot() == before
    if fake is not None:
        assert len(fake.calls) == 1
    _, lab, _, client = world
    manual = client.get(f"/api/labs/{lab.pk}/availability?date=2030-01-07")
    assert manual.status_code == 200 and manual.json()["slots"]


@pytest.mark.parametrize("label", ["AC-33-API-stale"])
def test_stale_candidate_is_not_success(world: tuple[Any, ...], monkeypatch: Any, label: str) -> None:
    _, _, station, _ = world

    def offline() -> None:
        station.is_operational = False
        station.save()

    monkeypatch.setattr("src.routes.ai_suggestion.configured_client", lambda: FakeClient(action=offline))
    result = post(world)
    assert result.status_code == 409
    assert result.json()["code"] == "candidate_unavailable"
    assert not Booking.objects.exists()


@pytest.mark.parametrize("case,status", [("get", 405), ("type", 415), ("json", 400),
                                        ("size", 422), ("date", 422), ("missing", 404)],
                         ids=lambda value: f"AC-29-API-contract-{value}")
def test_http_contract(world: tuple[Any, ...], case: str, status: int) -> None:
    _, lab, _, client = world
    path = f"/api/labs/{lab.pk}/suggestion"
    if case == "get":
        result = client.get(path)
    elif case == "missing":
        lab.pk += 100000
        result = post(world)
    elif case == "date":
        result = post(world, {"date": "2030-02-30", "need": "desk"})
    else:
        body = "not-json" if case == "json" else "x" * 16385 if case == "size" else "{}"
        result = client.post(path, data=body,
                             content_type="text/plain" if case == "type" else "application/json",
                             HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
    assert result.status_code == status
    assert "error" in result.json()
    assert not Booking.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("label", ["AC-36-API-no-transaction"])
def test_wait_is_outside_request_transaction(world: tuple[Any, ...], monkeypatch: Any,
                                            label: str) -> None:
    def inspect() -> None:
        assert connection.get_autocommit()
        assert not connection.in_atomic_block

    monkeypatch.setitem(connection.settings_dict, "ATOMIC_REQUESTS", True)
    monkeypatch.setattr("src.routes.ai_suggestion.configured_client",
                        lambda: FakeClient(action=inspect))
    before = snapshot()
    assert post(world).status_code == 200
    assert snapshot() == before


@pytest.mark.parametrize("label", ["AC-35-API-absent-key-zero-process"])
def test_real_configuration_with_missing_key_does_not_spawn(
    world: tuple[Any, ...], monkeypatch: Any, label: str,
) -> None:
    from src.integrations.gemini import configured_client

    def forbidden(*args: Any, **kwargs: Any) -> None:
        pytest.fail("No worker should be started without a key.")

    monkeypatch.setattr("src.integrations.gemini.subprocess.Popen", forbidden)
    monkeypatch.setattr("src.routes.ai_suggestion.configured_client", lambda: configured_client({
        "LAB_BOOKING_AI_ENABLED": "1",
    }))
    result = post(world)
    assert result.status_code == 503 and result.json()["code"] == "not_configured"
