"""AC-49 session invalidation for both the protected page and the JSON API."""

import pytest
from django.contrib.sessions.models import Session
from django.test import Client

from src.data.models import User
from tests.http_helpers import csrf_post


@pytest.fixture(autouse=True, params=["AC-49"], ids=str)
def criterion_id(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.mark.parametrize("accept", ["application/json", "text/html"])
def test_AC_49_logout_invalidates_server_session_and_old_cookie(
    active_student: User,
    generated_password: str,
    csrf_client: Client,
    accept: str,
) -> None:
    csrf_post(
        csrf_client,
        "/api/auth/login",
        {"email": active_student.email, "password": generated_password},
    )
    old_key = csrf_client.cookies["sessionid"].value
    before = list(User.objects.values())
    assert Session.objects.filter(session_key=old_key).exists()
    response = csrf_post(csrf_client, "/api/auth/logout", accept=accept)
    if accept == "application/json":
        assert response.status_code == 200
        assert response.json() == {"redirect": "/login?logged_out=1"}
    else:
        assert response.status_code == 302
        assert response.url == "/login?logged_out=1"
    assert not Session.objects.filter(session_key=old_key).exists()
    assert "_auth_user_id" not in csrf_client.session
    assert csrf_client.get("/labs").url == "/login?next=/labs"
    api = csrf_client.get("/api/labs")
    assert api.status_code == 401
    assert api.json() == {"error": "Connexion requise."}
    assert "Location" not in api.headers
    replay = Client(enforce_csrf_checks=True)
    replay.cookies["sessionid"] = old_key
    assert replay.get("/labs").url == "/login?next=/labs"
    api = replay.get("/api/labs")
    assert api.status_code == 401
    assert api.json() == {"error": "Connexion requise."}
    assert "Location" not in api.headers
    assert list(User.objects.values()) == before
    page = csrf_client.get("/login?logged_out=1")
    assert "Tu es déconnecté." in page.content.decode()


@pytest.mark.parametrize("case", ["get", "missing-token", "invalid-token", "origin"])
def test_AC_49_logout_requires_post_and_valid_csrf(
    active_student: User,
    generated_password: str,
    csrf_client: Client,
    case: str,
) -> None:
    csrf_post(
        csrf_client,
        "/api/auth/login",
        {"email": active_student.email, "password": generated_password},
    )
    old_key = csrf_client.cookies["sessionid"].value
    if case == "get":
        response = csrf_client.get("/api/auth/logout")
        assert response.status_code == 405
    else:
        headers = {}
        if case == "invalid-token":
            headers["HTTP_X_CSRFTOKEN"] = "A" * 32
        if case == "origin":
            headers["HTTP_X_CSRFTOKEN"] = csrf_client.cookies["csrftoken"].value
            headers["HTTP_ORIGIN"] = "https://outside.example"
        response = csrf_client.post("/api/auth/logout", **headers)
        assert response.status_code == 403
        assert "vérification de sécurité" in response.content.decode()
    assert Session.objects.filter(session_key=old_key).exists()
    assert csrf_client.get("/labs").status_code == 200
