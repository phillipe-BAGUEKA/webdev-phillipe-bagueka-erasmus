"""AC-46/48 API authentication and observable catalogue changes in isolated data."""

from datetime import timedelta
from unittest.mock import Mock

import pytest
from django.contrib.sessions.models import Session
from django.test import Client
from django.utils import timezone

from src.data.models import Laboratory, User
from src.services.access import Actor, AuthenticationRequired
from src.services.labs import list_laboratories
from tests.http_helpers import csrf_post


@pytest.fixture
def signed_in(
    active_student: User, generated_password: str, csrf_client: Client
) -> Client:
    response = csrf_post(
        csrf_client, "/api/auth/login",
        {"email": active_student.email, "password": generated_password},
    )
    assert response.status_code == 200
    return csrf_client


@pytest.mark.parametrize("case", ["absent", "invalid", "expired", "inactive"])
@pytest.mark.parametrize("criterion", ["AC-46"], ids=str)
def test_api_refuses_without_html_redirect(
    signed_in: Client, active_student: User, case: str, criterion: str
) -> None:
    Laboratory.objects.create(name="Do not disclose")
    key = signed_in.cookies["sessionid"].value
    if case == "absent":
        signed_in.cookies.clear()
    elif case == "invalid":
        signed_in.cookies["sessionid"] = "invalid-session"
    elif case == "expired":
        Session.objects.filter(session_key=key).update(
            expire_date=timezone.now() - timedelta(seconds=1)
        )
    else:
        active_student.is_active = False
        active_student.save(update_fields=["is_active"])
    before_users = list(User.objects.values())
    response = signed_in.get("/api/labs", HTTP_ACCEPT="text/html")
    assert response.status_code == 401
    assert response.json() == {"error": "Connexion requise."}
    assert response.headers["Content-Type"] == "application/json"
    assert "Location" not in response.headers
    assert "Do not disclose" not in response.content.decode()
    assert "no-store" in response.headers["Cache-Control"]
    assert signed_in.get("/labs").url == "/login?next=/labs"
    assert list(User.objects.values()) == before_users
    assert Laboratory.objects.count() == 1


@pytest.mark.parametrize("criterion", ["AC-48"], ids=str)
def test_catalogue_database_round_trip_and_empty(
    signed_in: Client, criterion: str
) -> None:
    first = Laboratory.objects.create(pk=11, name="Zeta isolated")
    second = Laboratory.objects.create(pk=3, name="<b>Alpha from database</b>")
    before_users = list(User.objects.values())
    original = list(Laboratory.objects.order_by("id").values("id", "name"))
    response = signed_in.get("/api/labs")
    assert response.status_code == 200
    assert response.json() == {"laboratories": original}
    assert list(Laboratory.objects.order_by("id").values("id", "name")) == original
    saved = {"id": second.pk, "name": second.name}
    second.delete()
    assert signed_in.get("/api/labs").json() == {
        "laboratories": [{"id": first.pk, "name": first.name}]
    }
    Laboratory.objects.create(**saved)
    assert signed_in.get("/api/labs").json() == {"laboratories": original}
    Laboratory.objects.all().delete()
    assert signed_in.get("/api/labs").json() == {"laboratories": []}
    assert list(User.objects.values()) == before_users


@pytest.mark.parametrize("criterion", ["AC-46"], ids=str)
@pytest.mark.parametrize(
    "actor", [None, Actor(1, "test@example.test", "student", False)]
)
def test_service_rejects_before_reading(
    actor: Actor | None, criterion: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    read = Mock(side_effect=AssertionError("Unauthorised database read"))
    monkeypatch.setattr("src.data.labs.list_laboratories", read)
    with pytest.raises(AuthenticationRequired):
        list_laboratories(actor)
    read.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("criterion", ["AC-48"], ids=str)
def test_service_reads_without_http_context(criterion: str) -> None:
    lab = Laboratory.objects.create(name="Service data")
    actor = Actor(12, "test@example.test", "student", True)
    assert list_laboratories(actor) == [{"id": lab.pk, "name": lab.name}]


@pytest.mark.parametrize("criterion", ["AC-48"], ids=str)
def test_catalogue_rejects_writes(signed_in: Client, criterion: str) -> None:
    response = csrf_post(signed_in, "/api/labs", {"name": "No write"})
    assert response.status_code == 405
    assert Laboratory.objects.count() == 0
