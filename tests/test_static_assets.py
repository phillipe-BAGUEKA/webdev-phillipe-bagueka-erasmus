"""AC-48: browsers must be able to execute the module served by runserver."""

import os
import subprocess
import sys
from textwrap import dedent

from django.conf import settings


def test_AC_48_module_response_overrides_incorrect_platform_mime() -> None:
    # A fresh process reproduces startup after an OS registers .mjs as plain text.
    # Do not reload settings or alter the MIME registry of the other tests.
    script = dedent(
        """
        import mimetypes

        mimetypes.add_type("text/plain", ".mjs")

        import django

        django.setup()

        from django.conf import settings
        from django.contrib.staticfiles.handlers import StaticFilesHandler
        from django.core.wsgi import get_wsgi_application
        from django.test import RequestFactory

        handler = StaticFilesHandler(get_wsgi_application())
        request = RequestFactory().get("/static/js/labs.mjs")
        response = handler.get_response(request)
        try:
            assert response.status_code == 200
            content_type = response.headers["Content-Type"].split(";")[0]
            assert content_type == "text/javascript", content_type
            source = settings.BASE_DIR / "src/static/js/labs.mjs"
            assert b"".join(response.streaming_content) == source.read_bytes()
            print("HTTP 200; text/javascript; original module body")
        finally:
            response.close()
        """
    )
    environment = os.environ.copy()
    environment["DJANGO_SETTINGS_MODULE"] = "tests.settings"
    result = subprocess.run(
        [sys.executable, "-"],
        input=script,
        text=True,
        capture_output=True,
        cwd=settings.BASE_DIR,
        env=environment,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
