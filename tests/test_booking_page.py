"""AC-40/41/42: real protected template and imported JavaScript MIME."""

import pytest
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.wsgi import get_wsgi_application
from django.test import Client, RequestFactory

from src.data.models import User


@pytest.mark.parametrize("criterion", ["AC-40-AC-41-AC-42"], ids=str)
def test_student_journey_template_keeps_session_csrf_and_navigation(db: None, criterion: str) -> None:
    client = Client(enforce_csrf_checks=True)
    assert client.get("/labs").status_code == 302
    user = User.objects.create_user("ui-page@tests.example")
    client.force_login(user)
    response = client.get("/labs")
    assert response.status_code == 200
    html = response.content.decode()
    assert "no-store" in response.headers["Cache-Control"]
    for target in ("availability", "personal-bookings", "booking-confirm", "booking-csrf"):
        assert f'id="{target}"' in html
    assert 'for="booking-date"' in html
    assert 'type="date" required' in html
    assert "Europe/Sofia" in html
    assert 'aria-live="polite"' in html
    assert 'id="booking-confirm" type="button" disabled' in html
    assert 'src="/static/js/labs.mjs?v=2" type="module"' in html


@pytest.mark.parametrize("asset", ["labs.mjs", "booking.mjs"], ids=["AC-48-root", "AC-40-import"])
def test_root_and_imported_module_are_served_as_javascript(asset: str) -> None:
    handler = StaticFilesHandler(get_wsgi_application())
    response = handler.get_response(RequestFactory().get(f"/static/js/{asset}?v=1"))
    try:
        assert response.status_code == 200
        assert response.headers["Content-Type"].split(";")[0] == "text/javascript"
        assert b"".join(response.streaming_content)
    finally:
        response.close()
