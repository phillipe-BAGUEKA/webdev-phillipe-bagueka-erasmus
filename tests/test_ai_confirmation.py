"""AC-34: fake suggestion then actual creation service through session/CSRF HTTP."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from django.db import connection
from django.test import Client

from src.data.models import Booking, Laboratory, User, Workstation
from tests.test_ai_suggestion import FakeClient

NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "change", ["none", "occupied", "offline", "quota", "personal"],
    ids=lambda value: f"AC-34-suggestion-confirm-{value}",
)
def test_confirmation_rechecks_current_rules(
    db: None, monkeypatch: Any, change: str,
) -> None:
    assert connection.vendor == "postgresql"
    monkeypatch.setattr("django.utils.timezone.now", lambda: NOW)
    monkeypatch.setattr(
        "src.routes.ai_suggestion.business_clock", lambda: NOW,
    )
    fake = FakeClient()
    monkeypatch.setattr("src.routes.ai_suggestion.configured_client", lambda: fake)
    user = User.objects.create_user("ai-confirm@tests.example")
    other = User.objects.create_user("ai-competitor@tests.example")
    lab = Laboratory.objects.create(name="AI confirmation tests")
    station = Workstation.objects.create(laboratory=lab, name="A")
    second = Workstation.objects.create(laboratory=lab, name="B")
    client = Client(enforce_csrf_checks=True)
    client.get("/login")
    client.force_login(user)

    def post(path: str, payload: dict[str, Any]) -> Any:
        return client.post(
            path, data=json.dumps(payload), content_type="application/json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )

    suggestion = post(
        f"/api/labs/{lab.pk}/suggestion",
        {"date": "2030-01-07", "need": "desk"},
    )
    assert suggestion.status_code == 200
    assert Booking.objects.count() == 0
    candidate = suggestion.json()["candidate"]
    start = datetime.fromisoformat(candidate["starts_at"])
    if change == "offline":
        station.is_operational = False
        station.save()
    if change in {"occupied", "personal", "quota"}:
        owner = other if change == "occupied" else user
        target = second if change == "personal" else station
        times = (
            [start + timedelta(hours=n) for n in (2, 3, 4)]
            if change == "quota" else [start]
        )
        for begins in times:
            Booking.objects.create(
                owner=owner, workstation=target, starts_at=begins,
                ends_at=begins + timedelta(hours=1),
            )
    before = list(Booking.objects.order_by("pk").values())
    creation = post("/api/bookings", {key: candidate[key] for key in (
        "workstation_id", "starts_at", "ends_at",
    )})
    assert creation.status_code == (201 if change == "none" else 409)
    after = list(Booking.objects.order_by("pk").values())
    if change == "none":
        assert len(after) == len(before) + 1
        assert after[-1]["owner_id"] == user.pk
    else:
        assert after == before
    assert len(fake.calls) == 1  # Confirmation does not invoke the model again.
