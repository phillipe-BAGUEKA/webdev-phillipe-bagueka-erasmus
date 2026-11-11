"""HTTP integration through real services, sessions, CSRF and PostgreSQL."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import patch

import pytest
from django.contrib.sessions.models import Session
from django.db import DatabaseError, connection
from django.test import Client

from src.data.models import Booking, Laboratory, User, Workstation
from tests.http_helpers import csrf_post

NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)
START = NOW + timedelta(hours=2)
World = tuple[User, User, Laboratory, Workstation, Workstation, Client]


@pytest.fixture
def world(db: None, monkeypatch: pytest.MonkeyPatch) -> World:
    assert connection.vendor == "postgresql"
    monkeypatch.setattr("django.utils.timezone.now", lambda: NOW)
    user = User.objects.create_user("http-owner@tests.example")
    other = User.objects.create_user("http-other@tests.example")
    lab = Laboratory.objects.create(name="HTTP isolated laboratory")
    first = Workstation.objects.create(laboratory=lab, name="A")
    second = Workstation.objects.create(laboratory=lab, name="B")
    return user, other, lab, first, second, signed_client(user)


def signed_client(user: User | None = None) -> Client:
    client = Client(enforce_csrf_checks=True)
    assert client.get("/login").status_code == 200
    if user is not None:
        client.force_login(user)
    return client


def payload(station: Workstation, start: datetime = START) -> dict[str, Any]:
    return {"workstation_id": station.pk, "starts_at": start.isoformat(),
            "ends_at": (start + timedelta(hours=1)).isoformat()}


def post(client: Client, url: str, body: Any) -> Any:
    return client.post(url, data=json.dumps(body), content_type="application/json",
                       HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
                       HTTP_ACCEPT="text/html")


def snapshot() -> tuple[list[dict[str, Any]], ...]:
    return tuple(list(model.objects.order_by("pk").values())
                 for model in (User, Laboratory, Workstation, Booking))


def stored(owner: User, station: Workstation, start: datetime = START,
           *, cancelled: bool = False) -> Booking:
    return Booking.objects.create(
        owner=owner, workstation=station, starts_at=start,
        ends_at=start + timedelta(hours=1), cancelled_at=NOW if cancelled else None,
    )


def assert_error(response: Any, status: int) -> None:
    assert response.status_code == status
    assert response.headers["Content-Type"] == "application/json"
    assert set(response.json()) == {"error"}
    assert isinstance(response.json()["error"], str)
    assert response.json()["error"]
    assert "Location" not in response.headers
    assert "no-store" in response.headers["Cache-Control"]


@pytest.mark.parametrize("criterion", ["AC-13-AC-14-AC-28"], ids=str)
def test_reads_real_rows_empty_and_private_history(world: World, criterion: str) -> None:
    user, other, lab, station, _, client = world
    before = snapshot()
    empty = client.get("/api/bookings")
    assert empty.status_code == 200 and empty.json() == {"bookings": []}
    slots = client.get(f"/api/labs/{lab.pk}/availability?date=2030-01-07")
    assert slots.status_code == 200
    assert len(slots.json()["slots"]) == 20
    assert set(slots.json()["slots"][0]) == {
        "workstation_id", "workstation_name", "starts_at", "ends_at",
    }
    assert slots.json()["slots"][0]["starts_at"] == "2030-01-07T06:00:00Z"
    assert snapshot() == before
    foreign = stored(other, station)
    mine = stored(user, station, START + timedelta(hours=1), cancelled=True)
    before = snapshot()
    history = client.get("/api/bookings")
    assert history.status_code == 200
    rows = history.json()["bookings"]
    assert [row["id"] for row in rows] == [mine.pk]
    assert rows[0]["status"] == "cancelled"
    assert rows[0]["cancelled_at"] == "2030-01-07T05:00:00Z"
    assert str(foreign.pk) not in [str(row["id"]) for row in rows]
    slots = client.get(f"/api/labs/{lab.pk}/availability?date=2030-01-07")
    assert len(slots.json()["slots"]) == 19
    assert other.email.encode() not in slots.content
    assert b"owner" not in slots.content and b"booking_id" not in slots.content
    assert snapshot() == before
    empty_lab = Laboratory.objects.create(name="Empty HTTP laboratory")
    assert client.get(f"/api/labs/{empty_lab.pk}/availability?date=2030-01-07").json() == {"slots": []}
    assert client.get(f"/api/labs/{lab.pk}/availability?date=2030-01-05").json() == {"slots": []}


@pytest.mark.parametrize("criterion", ["AC-15-AC-17-AC-25-AC-28"], ids=str)
def test_create_conflict_cancel_repeat_and_retained_row(world: World, criterion: str) -> None:
    user, other, _, station, _, client = world
    created = post(client, "/api/bookings", payload(station))
    assert created.status_code == 201
    row_json = created.json()["booking"]
    booking = Booking.objects.get(pk=row_json["id"])
    assert booking.owner_id == user.pk
    assert booking.starts_at == START
    assert row_json == {"id": booking.pk, "workstation_id": station.pk,
                        "starts_at": "2030-01-07T07:00:00Z",
                        "ends_at": "2030-01-07T08:00:00Z",
                        "created_at": "2030-01-07T05:00:00Z", "cancelled_at": None}
    foreign_client = signed_client(other)
    before = snapshot()
    assert_error(post(foreign_client, "/api/bookings", payload(station)), 409)
    assert snapshot() == before
    station.is_operational = False
    station.save()
    cancelled = post(client, f"/api/bookings/{booking.pk}/cancel", {})
    assert cancelled.status_code == 200
    before = snapshot()
    with patch("django.utils.timezone.now", return_value=START + timedelta(hours=2)):
        repeated = post(client, f"/api/bookings/{booking.pk}/cancel", {})
    assert repeated.status_code == 200 and repeated.json() == cancelled.json()
    assert snapshot() == before
    assert Booking.objects.count() == 1
    booking.refresh_from_db()
    assert booking.cancelled_at == NOW
    assert client.get("/api/bookings").json()["bookings"][0]["status"] == "cancelled"
    assert client.get("/api/bookings").json()["bookings"][0]["is_operational"] is False


@pytest.mark.parametrize("case,status", [("quota", 409), ("staff", 403), ("offline", 409),
                                         ("personal", 409), ("missing", 404)],
                         ids=["AC-20", "AC-15-personnel", "AC-11", "AC-18", "AC-15-missing"])
def test_creation_business_refusals(world: World, case: str, status: int) -> None:
    user, _, _, station, second, client = world
    body = payload(station)
    if case == "quota":
        for hour in (9, 11, 13):
            stored(user, second, START.replace(hour=hour))
    elif case == "staff":
        user.role = "personnel"
        user.save()
    elif case == "offline":
        station.is_operational = False
        station.save()
    elif case == "personal":
        stored(user, second)
    else:
        body["workstation_id"] = station.pk + 1000
    before = snapshot()
    assert_error(post(client, "/api/bookings", body), status)
    assert snapshot() == before


@pytest.mark.parametrize("case,status", [("other", 403), ("cancelled-other", 403),
                                         ("late", 409), ("missing", 404)],
                         ids=["AC-27", "AC-27-repeat", "AC-26", "AC-25-missing"])
def test_cancellation_refusals(world: World, case: str, status: int) -> None:
    user, other, _, station, _, client = world
    row = stored(other if "other" in case else user, station,
                 NOW if case == "late" else START, cancelled=case == "cancelled-other")
    target = row.pk + 1000 if case == "missing" else row.pk
    before = snapshot()
    assert_error(post(client, f"/api/bookings/{target}/cancel", {}), status)
    assert snapshot() == before


@pytest.mark.parametrize("state", ["absent", "invalid", "expired", "inactive", "logout-replay"],
                         ids=[f"AC-46-AC-49-{name}" for name in
                              ("absent", "invalid", "expired", "inactive", "logout-replay")])
def test_session_required_for_all_routes_including_csrf_valid_posts(world: World, state: str) -> None:
    user, _, lab, station, _, client = world
    row = stored(user, station)
    old_key = client.cookies["sessionid"].value
    if state == "absent":
        client.cookies.pop("sessionid")
    elif state == "invalid":
        client.cookies["sessionid"] = "not-a-real-session"
    elif state == "expired":
        Session.objects.filter(session_key=old_key).update(expire_date=NOW - timedelta(seconds=1))
    elif state == "inactive":
        user.is_active = False
        user.save()
    else:
        assert csrf_post(client, "/api/auth/logout").status_code == 200
        assert not Session.objects.filter(session_key=old_key).exists()
        client.cookies["sessionid"] = old_key
    before = snapshot()
    assert_error(client.get(f"/api/labs/{lab.pk}/availability?date=2030-01-07"), 401)
    assert_error(client.get("/api/bookings"), 401)
    assert_error(post(client, "/api/bookings", payload(station)), 401)
    assert_error(post(client, f"/api/bookings/{row.pk}/cancel", {}), 401)
    assert snapshot() == before


@pytest.mark.parametrize("signed", [False, True], ids=["AC-15-csrf-anonymous", "AC-15-csrf-session"])
def test_csrf_is_checked_separately_and_form_html_is_preserved(world: World, signed: bool) -> None:
    user, _, _, station, _, _ = world
    client = signed_client(user if signed else None)
    row = stored(user, station)
    before = snapshot()
    for url, body in (("/api/bookings", payload(station)), (f"/api/bookings/{row.pk}/cancel", {})):
        response = client.post(url, data=json.dumps(body), content_type="application/json",
                               HTTP_ACCEPT="text/html")
        assert_error(response, 403)
        assert "sécurité" in response.json()["error"]
    html = client.post("/api/auth/login", {}, HTTP_ACCEPT="text/html")
    assert html.status_code == 403 and html.headers["Content-Type"].startswith("text/html")
    assert snapshot() == before


@pytest.mark.parametrize("body", [None, [], {}, {"owner_id": 1},
                                 {"workstation_id": True, "starts_at": "x", "ends_at": "x"}],
                         ids=[f"AC-16-shape-{n}" for n in range(5)])
def test_invalid_json_shape(world: World, body: Any) -> None:
    before = snapshot()
    assert_error(post(world[-1], "/api/bookings", body), 422)
    assert snapshot() == before


@pytest.mark.parametrize("case", ["owner", "missing", "bad-start", "naive", "compact", "past",
                                "weekend", "duration", "zero-id", "bool-id"],
                         ids=[f"AC-15-AC-16-{case}" for case in
                              ("owner", "missing", "bad-start", "naive", "compact", "past",
                               "weekend", "duration", "zero-id", "bool-id")])
def test_invalid_payload_and_temporal_rules(world: World, case: str) -> None:
    _, other, _, station, _, client = world
    body = payload(station)
    if case == "owner":
        body["owner_id"] = other.pk
    elif case == "missing":
        del body["ends_at"]
    elif case == "bad-start":
        body["starts_at"] = "2030-99-99T08:00:00Z"
    elif case == "naive":
        body["starts_at"] = "2030-01-07T08:00:00"
    elif case == "compact":
        body["starts_at"] = "20300107T080000Z"
    elif case == "past":
        body = payload(station, START - timedelta(days=3))
    elif case == "weekend":
        body = payload(station, START.replace(day=5))
    elif case == "duration":
        body["ends_at"] = (START + timedelta(hours=2)).isoformat()
    else:
        body["workstation_id"] = 0 if case == "zero-id" else True
    before = snapshot()
    assert_error(post(client, "/api/bookings", body), 422)
    assert snapshot() == before


@pytest.mark.parametrize("raw,content_type,status", [("{", "application/json", 400),
    (b"\xff", "application/json", 400), ("", "application/json", 400),
    ("{}", "text/plain", 415), ("{}", "application/x-www-form-urlencoded", 415)],
    ids=[f"AC-16-content-{n}" for n in range(5)])
def test_malformed_json_and_unsupported_content_type(
    world: World, raw: Any, content_type: str, status: int,
) -> None:
    client = world[-1]
    before = snapshot()
    for url in ("/api/bookings", "/api/bookings/999999/cancel"):
        # Django's convenience post() omits Content-Type for empty data.
        # Supply the actual WSGI header to test malformed empty JSON itself.
        response = client.generic("POST", url, raw, content_type=content_type,
                               CONTENT_TYPE=content_type,
                               HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
        assert_error(response, status)
    assert snapshot() == before


@pytest.mark.parametrize("start,expected", [
    ("2030-01-07T08:00:00+02:00", "2030-01-07T06:00:00Z"),
    ("2030-07-08T08:00:00+03:00", "2030-07-08T05:00:00Z"),
], ids=["AC-14-winter-http", "AC-14-summer-http"])
def test_offset_input_is_returned_and_stored_as_utc(world: World, start: str, expected: str) -> None:
    station, client = world[3], world[-1]
    body = payload(station, datetime.fromisoformat(start))
    response = client.post(
        "/api/bookings", json.dumps(body), content_type="application/json; charset=utf-8",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
    )
    assert response.status_code == 201
    assert response.json()["booking"]["starts_at"] == expected
    assert Booking.objects.get().starts_at.utcoffset() == timedelta(0)


@pytest.mark.parametrize("criterion", ["AC-25-changed-routing-http"], ids=str)
def test_booking_changed_is_a_real_service_refusal_409(world: World, criterion: str) -> None:
    from src.data import booking_cancellation as data

    user, _, _, station, second, client = world
    row = stored(user, station)
    lookup = data.workstation_hint

    def change_after_lookup(booking_id: int) -> int:
        hint = lookup(booking_id)
        Booking.objects.filter(pk=booking_id).update(workstation=second)
        return hint

    before = snapshot()
    with patch.object(data, "workstation_hint", side_effect=change_after_lookup):
        assert_error(post(client, f"/api/bookings/{row.pk}/cancel", {}), 409)
    assert snapshot() == before


@pytest.mark.parametrize("query", ["", "date=no", "date=20300107", "date=2030-02-30",
    "date=2030-01-07&date=2030-01-08", "date=2030-01-07&owner_id=2"],
    ids=[f"AC-13-invalid-query-{n}" for n in range(6)])
def test_invalid_availability_query(world: World, query: str) -> None:
    _, _, lab, _, _, client = world
    before = snapshot()
    assert_error(client.get(f"/api/labs/{lab.pk}/availability?{query}"), 422)
    assert snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-13-AC-27"], ids=str)
def test_missing_lab_and_owner_spoofing_parameters(world: World, criterion: str) -> None:
    _, other, _, station, _, client = world
    row = stored(other, station)
    before = snapshot()
    assert_error(client.get("/api/labs/999999/availability?date=2030-01-07"), 404)
    assert_error(client.get(f"/api/bookings?owner_id={other.pk}"), 422)
    assert_error(post(client, f"/api/bookings/{row.pk}/cancel", {"owner_id": other.pk}), 422)
    assert_error(post(client, "/api/bookings?owner_id=2", payload(station)), 422)
    assert snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-13-AC-15-AC-25-methods"], ids=str)
def test_wrong_methods_return_json_and_allow(world: World, criterion: str) -> None:
    _, _, lab, _, _, client = world
    before = snapshot()
    for method, url, allow in (("post", f"/api/labs/{lab.pk}/availability", "GET"),
                               ("delete", "/api/bookings", "GET, POST"),
                               ("get", "/api/bookings/1/cancel", "POST")):
        response = getattr(client, method)(url, HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
        assert_error(response, 405)
        assert response.headers["Allow"] == allow
    assert snapshot() == before


@pytest.mark.parametrize("criterion", ["AC-15-infrastructure-error"], ids=str)
def test_unexpected_database_error_is_safe_500(world: World, criterion: str, caplog: Any) -> None:
    # Fault injection only, never a mocked domain decision or success path.
    from src.data import booking_reads as data

    client = world[-1]
    before = snapshot()
    with patch.object(data, "personal_bookings", side_effect=DatabaseError("SQL SELECT private_value")):
        response = client.get("/api/bookings")
    assert_error(response, 500)
    assert response.json() == {"error": "Erreur interne."}
    assert "private_value" not in caplog.text and "SELECT" not in caplog.text
    assert snapshot() == before
