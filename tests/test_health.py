"""Readiness is public, cheap and does not reveal connection errors."""

from unittest.mock import patch

from django.db import DatabaseError
from django.test import Client

from src.data.health import database_ready


def test_health_returns_200_for_reachable_database(db):
    response = Client().get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}
    assert response["Cache-Control"].startswith("max-age=0")


def test_health_returns_generic_503_when_database_fails(db):
    with patch("src.data.health.connection.cursor", side_effect=DatabaseError("private-db-detail")):
        response = Client().get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "error", "db": "down"}
    assert b"private-db-detail" not in response.content


def test_health_rejects_post_without_query(db):
    response = Client().post("/health")
    assert response.status_code == 405
    assert database_ready() is True
