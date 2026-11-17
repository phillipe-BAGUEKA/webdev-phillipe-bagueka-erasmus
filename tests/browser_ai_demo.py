"""Explicit loopback-only browser fixture, never imported by normal deployment.

Uses only the dedicated PostgreSQL test database and an unusable-password user.
Cookie names are separate from the student's development session. Own rows are
cleaned on exit. Run only while automated tests are stopped.
"""

import argparse
from datetime import timedelta
import logging
import os
from pathlib import Path
import sys
from typing import Any, Callable
from uuid import uuid4
from wsgiref.simple_server import WSGIRequestHandler, make_server

STATE: dict[str, Any] = {}
MODES = {
    "disabled", "success", "timeout", "quota", "invalid", "error", "empty",
    "expired",
}


def mode() -> str:
    value = STATE["case_file"].read_text(encoding="utf-8-sig").strip()
    return value if value in MODES else "disabled"


class SimulationMiddleware:
    """Label every HTML fixture and support an isolated session-expiry case."""

    def __init__(self, get_response: Callable[[Any], Any]) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        from django.contrib.auth.models import AnonymousUser

        current = mode()
        if current == "expired" and request.path.endswith("/suggestion"):
            request.session.flush()
            request.user = AnonymousUser()
        response = self.get_response(request)
        is_html = response.get("Content-Type", "").startswith("text/html")
        if not response.streaming and is_html:
            banner = (
                '<aside style="border:4px solid;padding:1rem">SIMULATION LOCALE — '
                f'PostgreSQL de test, fournisseur factice (mode au chargement : {current}), '
                'aucun appel Google.</aside>'
            )
            html = response.content.decode("utf-8").replace(
                "<body>", "<body>" + banner, 1,
            )
            day = STATE["day"]
            if current == "empty":
                day += timedelta(days=(5 - day.weekday()) % 7)
            html = html.replace(
                'id="booking-date" type="date" required',
                f'id="booking-date" type="date" '
                f'value="{day.isoformat()}" required',
            )
            response.content = html.encode("utf-8")
            response["Content-Length"] = str(len(response.content))
        return response


class BrowserFake:
    """No network or provider key; select only an actual supplied candidate."""

    def select_candidate(
        self, need: str, candidates: tuple[Any, ...], *, deadline: float,
    ) -> Any:
        from src.services.ai_suggestion import (
            ClientError, ClientQuotaExceeded,
        )

        current = mode()
        if current == "timeout":
            raise TimeoutError
        if current == "quota":
            raise ClientQuotaExceeded
        if current == "error":
            raise ClientError
        if current == "invalid":
            return {}
        return {"candidate_id": candidates[0].candidate_id}


class QuietHandler(WSGIRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        """No request/credential/need diagnostics in this interactive fixture."""


def enter(request: Any) -> Any:
    from django.contrib.auth import login
    from django.http import HttpResponseRedirect

    login(
        request, STATE["user"],
        backend="django.contrib.auth.backends.ModelBackend",
    )
    STATE["sessions"].add(request.session.session_key)
    return HttpResponseRedirect("/labs")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-file", type=Path, required=True)
    parser.add_argument("--stop-file", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8011)
    args = parser.parse_args()
    if args.stop_file.exists() or not args.case_file.is_file():
        raise RuntimeError("Prepare a new stop path and a non-secret case file.")
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings_postgres"
    os.environ["LAB_BOOKING_AI_ENABLED"] = "0"
    import django

    django.setup()
    from django.conf import settings
    from django.contrib.sessions.models import Session
    from django.contrib.staticfiles.handlers import StaticFilesHandler
    from django.core.wsgi import get_wsgi_application
    from django.db import connection
    from django.urls import path
    from django.utils import timezone
    from src.config.urls import urlpatterns as application_urls
    from src.data.models import Booking, Laboratory, User, Workstation
    from src.routes import ai_suggestion

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_database(), current_user, inet_server_port()",
        )
        identity = cursor.fetchone()
    if identity != ("test_lab_booking_1a", "lab_booking_1a_test", 5433):
        raise RuntimeError("Dedicated test database identity required.")
    settings.ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
    settings.SESSION_COOKIE_NAME = "lab_booking_ai_browser_session"
    settings.CSRF_COOKIE_NAME = "lab_booking_ai_browser_csrf"
    sys.modules["tests.browser_ai_demo"] = sys.modules[__name__]
    settings.MIDDLEWARE = [
        *settings.MIDDLEWARE, "tests.browser_ai_demo.SimulationMiddleware",
    ]
    settings.ROOT_URLCONF = "tests.browser_ai_demo"
    global urlpatterns
    urlpatterns = [path("__test__/enter", enter), *application_urls]
    day = timezone.localdate() + timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    STATE.update(case_file=args.case_file, day=day, sessions=set())
    token = uuid4().hex
    user = User.objects.create_user(f"browser-ai-{token}@tests.example")
    lab = Laboratory.objects.create(name="SIMULATION IA — Laboratoire de test")
    Workstation.objects.create(laboratory=lab, name="SIMULATION IA — Poste A")
    Workstation.objects.create(laboratory=lab, name="SIMULATION IA — Poste B")
    STATE["user"] = user
    original_factory = ai_suggestion.configured_client
    ai_suggestion.configured_client = lambda: (
        original_factory({}) if mode() == "disabled" else BrowserFake()
    )
    logging.getLogger("django.server").disabled = True
    try:
        with make_server(
            "127.0.0.1", args.port, StaticFilesHandler(get_wsgi_application()),
            handler_class=QuietHandler,
        ) as server:
            server.timeout = 0.5
            print(
                f"SIMULATION READY http://127.0.0.1:{args.port}/__test__/enter"
                f" ; date {day}", flush=True,
            )
            while not args.stop_file.exists():
                server.handle_request()
    finally:
        ai_suggestion.configured_client = original_factory
        Booking.objects.filter(workstation__laboratory=lab).delete()
        Workstation.objects.filter(laboratory=lab).delete()
        lab.delete()
        user.delete()
        Session.objects.filter(session_key__in=STATE["sessions"]).delete()
        connection.close()
        print("SIMULATION STOPPED; own test rows cleaned.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(
            "Isolated browser fixture failed; no connection details displayed.",
            file=sys.stderr,
        )
        raise SystemExit(1)
