"""AC-47 local login; provider login and laboratory API remain out of scope."""

import pytest
from django.contrib.sessions.models import Session
from django.test import Client

from src.data.models import Laboratory, User
from src.routes.auth import INVALID_CREDENTIALS_MESSAGE
from src.services.auth import InvalidCredentials, authenticate_user
from tests.http_helpers import csrf_post


@pytest.fixture(autouse=True, params=["AC-47"], ids=str)
def criterion_id(request: pytest.FixtureRequest) -> str:
    return request.param


def test_AC_47_login_page_has_accessible_fields_and_csrf(csrf_client: Client) -> None:
    response = csrf_client.get("/login")
    html = response.content.decode()
    assert response.status_code == 200
    assert '<html lang="fr">' in html
    assert "Connexion · Lab booking" in html
    assert 'for="id_email"' in html and 'for="id_password"' in html
    assert 'autocomplete="current-password"' in html
    assert 'name="csrfmiddlewaretoken"' in html
    assert 'method="post"' in html
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "no-store" in response.headers["Cache-Control"]


@pytest.mark.parametrize("accept", ["application/json", "text/html"])
def test_AC_47_valid_login_creates_session_and_preserves_account(
    active_student: User,
    generated_password: str,
    csrf_client: Client,
    accept: str,
) -> None:
    password_hash = active_student.password
    old_csrf = csrf_client.cookies["csrftoken"].value
    response = csrf_post(
        csrf_client,
        "/api/auth/login",
        {"email": active_student.email.upper(), "password": generated_password},
        accept=accept,
    )
    if accept == "application/json":
        assert response.status_code == 200
        assert response.json() == {"redirect": "/labs"}
    else:
        assert response.status_code == 302 and response.url == "/labs"
    assert csrf_client.session["_auth_user_id"] == str(active_student.pk)
    assert Session.objects.filter(session_key=csrf_client.session.session_key).exists()
    assert csrf_client.cookies["csrftoken"].value != old_csrf
    assert csrf_client.cookies["sessionid"]["httponly"]
    assert csrf_client.cookies["sessionid"]["samesite"] == "Lax"
    assert csrf_client.get("/labs").status_code == 200
    active_student.refresh_from_db()
    assert active_student.password == password_hash
    assert active_student.role == User.Role.STUDENT
    assert not active_student.is_staff and not active_student.is_superuser
    assert User.objects.count() == 1
    assert Laboratory.objects.count() == 0


@pytest.mark.parametrize("case", ["wrong-password", "unknown-email", "inactive"])
def test_AC_47_generic_refusal_without_changes(
    active_student: User,
    generated_password: str,
    csrf_client: Client,
    case: str,
) -> None:
    credentials = {"email": active_student.email, "password": generated_password}
    if case == "wrong-password":
        credentials["password"] += "wrong"
    elif case == "unknown-email":
        credentials["email"] = "absent@tests.example"
    else:
        active_student.is_active = False
        active_student.save(update_fields=["is_active"])
    before = list(User.objects.values())
    response = csrf_post(csrf_client, "/api/auth/login", credentials)
    assert response.status_code == 401
    assert response.json() == {"error": INVALID_CREDENTIALS_MESSAGE}
    assert "_auth_user_id" not in csrf_client.session
    assert list(User.objects.values()) == before
    assert Laboratory.objects.count() == 0


def test_AC_47_html_refusal_does_not_redisplay_password(
    active_student: User, generated_password: str, csrf_client: Client
) -> None:
    attempted_password = generated_password + "wrong"
    response = csrf_post(
        csrf_client,
        "/api/auth/login",
        {"email": active_student.email, "password": attempted_password},
        accept="text/html",
    )
    assert response.status_code == 401
    html = response.content.decode()
    assert INVALID_CREDENTIALS_MESSAGE in html
    assert attempted_password not in html
    assert 'role="alert"' in html


@pytest.mark.parametrize(
    "case", ["missing-token", "invalid-token", "no-cookie", "origin"]
)
def test_AC_47_csrf_refusal_with_real_middleware(
    active_student: User,
    generated_password: str,
    csrf_client: Client,
    case: str,
) -> None:
    headers = {"HTTP_ACCEPT": "application/json"}
    if case != "missing-token":
        headers["HTTP_X_CSRFTOKEN"] = csrf_client.cookies["csrftoken"].value
    if case == "invalid-token":
        headers["HTTP_X_CSRFTOKEN"] = "A" * 32
    if case == "no-cookie":
        csrf_client.cookies.clear()
    if case == "origin":
        headers["HTTP_ORIGIN"] = "https://outside.example"
    before = list(User.objects.values())
    response = csrf_client.post(
        "/api/auth/login",
        {"email": active_student.email, "password": generated_password},
        **headers,
    )
    assert response.status_code == 403
    assert "vérification de sécurité" in response.json()["error"]
    assert "_auth_user_id" not in csrf_client.session
    assert list(User.objects.values()) == before


@pytest.mark.parametrize(
    "target",
    [
        "https://outside.example/path",
        "//outside.example/path",
        "///outside.example/path",
        r"/\outside.example/path",
        "javascript:alert(1)",
        "https://testserver@outside.example/path",
        "https://testserver.outside.example/path",
        "/login",
        "/api/auth/logout",
        "/labs?view=mine#main",
    ],
)
@pytest.mark.parametrize("accept", ["application/json", "text/html"])
def test_AC_47_post_login_redirect_stays_inside_application(
    active_student: User,
    generated_password: str,
    csrf_client: Client,
    target: str,
    accept: str,
) -> None:
    expected = target if target == "/labs?view=mine#main" else "/labs"
    page = csrf_client.get("/login", {"next": target})
    assert page.context["next"] == expected
    # Test a forged POST too: checking only the hidden form field is insufficient.
    response = csrf_post(
        csrf_client,
        "/api/auth/login",
        {
            "email": active_student.email,
            "password": generated_password,
            "next": target,
        },
        accept=accept,
    )
    if accept == "application/json":
        destination = response.json()["redirect"]
    else:
        destination = response.url
    assert destination == expected


def test_AC_47_existing_anonymous_session_is_rotated(
    active_student: User, generated_password: str, csrf_client: Client
) -> None:
    session = csrf_client.session
    session["test_before_login"] = True
    session.save()
    previous_key = session.session_key
    csrf_post(
        csrf_client,
        "/api/auth/login",
        {"email": active_student.email, "password": generated_password},
    )
    assert csrf_client.session.session_key != previous_key
    assert not Session.objects.filter(session_key=previous_key).exists()


def test_AC_47_service_rejects_inactive_adapter_result(
    active_student: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    active_student.is_active = False
    monkeypatch.setattr(
        "src.data.users.check_credentials", lambda *args: active_student
    )
    with pytest.raises(InvalidCredentials):
        authenticate_user(active_student.email, "")
