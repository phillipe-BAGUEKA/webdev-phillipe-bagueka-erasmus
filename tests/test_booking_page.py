"""AC-40/41/42: real protected template and imported JavaScript MIME."""

import pytest
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.signals import request_finished
from django.core.wsgi import get_wsgi_application
from django.db import close_old_connections
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
    for results_class, list_id in (
        ("catalogue-results", "labs-list"),
        ("slot-results", "slots-list"),
        ("history-results", "bookings-list"),
    ):
        _, marker, remainder = html.partition(f'class="booking-results {results_class}"')
        assert marker, f"Missing reserved results region for {list_id}"
        region = remainder.split("</div>", 1)[0]
        assert 'role="region"' in region
        accessible_name = region.partition('aria-label="')[2].split('"', 1)[0]
        assert accessible_name.strip()
        assert 'tabindex="0"' in region
        assert f'id="{list_id}"' in region
    assert 'for="booking-date"' in html
    assert 'type="date" required' in html
    assert "Europe/Sofia" in html
    assert 'aria-live="polite"' in html
    assert 'id="booking-confirm" type="button" disabled' in html
    assert 'src="/static/js/labs.mjs?v=3" type="module"' in html
    assert 'for="ai-need"' in html
    assert 'maxlength="1000" required' in html
    assert 'aria-describedby="ai-privacy"' in html
    assert html.index('id="ai-privacy"') < html.index('id="ai-request"')


@pytest.mark.parametrize("asset", ["labs.mjs", "booking.mjs"], ids=["AC-48-root", "AC-40-import"])
def test_root_and_imported_module_are_served_as_javascript(asset: str) -> None:
    handler = StaticFilesHandler(get_wsgi_application())
    response = handler.get_response(RequestFactory().get(f"/static/js/{asset}?v=1"))
    try:
        assert response.status_code == 200
        assert response.headers["Content-Type"].split(";")[0] == "text/javascript"
        assert b"".join(response.streaming_content)
    finally:
        # Match Django's test client: closing a response must not touch an
        # unrelated database connection retained by an earlier test.
        disconnected = request_finished.disconnect(close_old_connections)
        try:
            response.close()
        finally:
            if disconnected:
                request_finished.connect(close_old_connections)
