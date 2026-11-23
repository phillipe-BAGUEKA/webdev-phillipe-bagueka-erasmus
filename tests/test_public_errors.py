"""Public fallback pages never expose internal error details."""

import logging
from unittest.mock import patch

from django.test import Client, override_settings


@override_settings(DEBUG=False)
def test_unknown_page_is_short_and_safe():
    response = Client().get("/no-such-page")
    assert response.status_code == 404
    assert response.content == b"Page introuvable."


@override_settings(DEBUG=False)
def test_server_error_handler_is_short_and_safe(caplog):
    with caplog.at_level(logging.ERROR, logger="django.request"):
        with patch("src.routes.health.is_ready", side_effect=RuntimeError("synthetic-private-detail")):
            response = Client(raise_request_exception=False).get("/health")
    assert response.status_code == 500
    assert response.content == b"Une erreur est survenue."
    assert b"synthetic-private-detail" not in response.content
    assert any(
        record.exc_info and str(record.exc_info[1]) == "synthetic-private-detail"
        for record in caplog.records
    )
