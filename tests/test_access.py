"""AC-46 page access; the API contract is covered separately in test_labs.py."""

import re

import pytest
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.wsgi import get_wsgi_application
from django.test import Client, RequestFactory

from src.data.models import Laboratory, User
from src.services.access import Actor, AuthenticationRequired, require_authenticated
from tests.http_helpers import csrf_post


@pytest.fixture(autouse=True, params=["AC-46"], ids=str)
def criterion_id(request: pytest.FixtureRequest) -> str:
    return request.param


def test_AC_46_anonymous_page_redirects_to_login(csrf_client: Client) -> None:
    response = csrf_client.get("/labs")
    assert response.status_code == 302
    assert response.url == "/login?next=/labs"


def test_AC_46_authenticated_page_has_fetch_container_without_embedded_catalogue(
    active_student: User, generated_password: str, csrf_client: Client
) -> None:
    lab = Laboratory.objects.create(name="ISOLATED LAB RETURNED ONLY BY API")
    csrf_post(
        csrf_client,
        "/api/auth/login",
        {"email": active_student.email, "password": generated_password},
    )
    response = csrf_client.get("/labs")
    assert response.status_code == 200
    html = response.content.decode()
    assert "<h1>Laboratoires</h1>" in html
    assert active_student.email in html
    assert "Se déconnecter" in html and 'method="post"' in html
    assert lab.name not in html
    assert 'id="labs-list"' in html
    assert '<script src="/static/js/labs.mjs?v=3" type="module"></script>' in html
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "no-store" in response.headers["Cache-Control"]
    assert Laboratory.objects.get(pk=lab.pk).name == lab.name


def test_AC_46_active_session_cannot_bypass_service_policy(
    active_student: User,
    generated_password: str,
    csrf_client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    csrf_post(
        csrf_client,
        "/api/auth/login",
        {"email": active_student.email, "password": generated_password},
    )

    def refuse_access(actor: Actor | None) -> Actor:
        raise AuthenticationRequired

    monkeypatch.setattr("src.routes.pages.require_authenticated", refuse_access)
    assert csrf_client.get("/labs").status_code == 302


@pytest.mark.parametrize(
    "actor", [None, Actor(1, "test@example.test", "student", False)]
)
def test_AC_46_service_rejects_missing_or_inactive_actor(actor: Actor | None) -> None:
    with pytest.raises(AuthenticationRequired):
        require_authenticated(actor)


def test_AC_46_service_accepts_active_actor_without_http_context() -> None:
    actor = Actor(1, "test@example.test", "student", True)
    assert require_authenticated(actor) == actor


def test_AC_46_account_deactivated_after_login_loses_page_access(
    active_student: User, generated_password: str, csrf_client: Client
) -> None:
    csrf_post(
        csrf_client,
        "/api/auth/login",
        {"email": active_student.email, "password": generated_password},
    )
    active_student.is_active = False
    active_student.save(update_fields=["is_active"])
    assert csrf_client.get("/labs").url == "/login?next=/labs"


@pytest.mark.parametrize("catalogue_criterion", ["AC-48"], ids=str)
def test_catalogue_does_not_revalidate_old_plain_text_module(
    active_student: User,
    generated_password: str,
    csrf_client: Client,
    catalogue_criterion: str,
) -> None:
    """An old URL's cached MIME must not survive through a 304 response."""
    csrf_post(
        csrf_client,
        "/api/auth/login",
        {"email": active_student.email, "password": generated_password},
    )
    html = csrf_client.get("/labs").content.decode()
    module = re.search(r'<script src="([^"]+)" type="module">', html)
    assert module is not None
    module_url = module.group(1)
    handler = StaticFilesHandler(get_wsgi_application())
    requests = RequestFactory()
    old_url = "/static/js/labs.mjs"
    cached = handler.get_response(requests.get(old_url))
    last_modified = cached.headers["Last-Modified"]
    cached.close()

    # A browser revalidates only an exact cached URL. On that URL, a 304
    # preserves the original text/plain metadata even after the server fix.
    headers = {}
    if module_url == old_url:
        headers["HTTP_IF_MODIFIED_SINCE"] = last_modified
    response = handler.get_response(requests.get(module_url, **headers))
    try:
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/javascript"
        assert b"export function createCatalogue" in b"".join(
            response.streaming_content
        )
    finally:
        response.close()
