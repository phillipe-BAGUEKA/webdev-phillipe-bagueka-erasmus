"""Production settings reject incomplete or unsafe configuration at startup."""

import importlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db import DatabaseError
from django.test import Client, override_settings


VALID = {
    "DJANGO_SECRET_KEY": "test-only-secret-with-enough-characters-to-pass-django-checks-12345",
    "DATABASE_URL": "postgresql://example:fake@db.example.test/lab?sslmode=require",
    "DJANGO_ALLOWED_HOSTS": "lab.example.test",
    "DJANGO_CSRF_TRUSTED_ORIGINS": "https://lab.example.test",
}


def load_production(overrides=None):
    values = VALID | (overrides or {})
    with patch.dict(os.environ, values, clear=True):
        return importlib.reload(importlib.import_module("src.config.production"))


def test_production_settings_use_postgres_tls_and_secure_cookies():
    settings = load_production()
    assert settings.DATABASES["default"]["OPTIONS"]["sslmode"] == "require"
    assert settings.DATABASES["default"]["HOST"] == "db.example.test"
    assert settings.SECURE_SSL_REDIRECT is True
    assert settings.SECURE_REDIRECT_EXEMPT == [r"^health$"]
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
    assert settings.MIDDLEWARE[1] == "whitenoise.middleware.WhiteNoiseMiddleware"


def test_production_settings_accept_neon_channel_binding():
    settings = load_production({
        "DATABASE_URL": (
            "postgresql://example:fake@db.example.test/lab?"
            "sslmode=require&channel_binding=require"
        ),
    })
    assert settings.DATABASES["default"]["OPTIONS"]["channel_binding"] == "require"


def test_production_settings_accept_verified_system_ca():
    settings = load_production({
        "DATABASE_URL": (
            "postgresql://example:fake@ep-demo.aws.neon.tech/lab?"
            "sslmode=verify-full&sslrootcert=system&channel_binding=require"
        ),
    })
    options = settings.DATABASES["default"]["OPTIONS"]
    assert options["sslmode"] == "verify-full"
    assert options["sslrootcert"] == "system"
    assert options["channel_binding"] == "require"


@pytest.mark.parametrize("parameters", [
    "sslmode=require&channel_binding=require",
    "sslmode=verify-full&channel_binding=require",
    "sslmode=verify-full&sslrootcert=system",
])
def test_production_settings_reject_weaker_neon_tls(parameters):
    with pytest.raises(ImproperlyConfigured, match="Invalid DATABASE_URL"):
        load_production({
            "DATABASE_URL": (
                "postgresql://example:fake@ep-demo.aws.neon.tech/lab?"
                f"{parameters}"
            ),
        })


@pytest.mark.parametrize("parameters", [
    "sslmode=require&sslrootcert=system",
    "sslmode=verify-full&sslrootcert=/tmp/untrusted.pem",
    "sslmode=verify-full&sslrootcert=system&sslrootcert=other",
])
def test_production_settings_reject_unapproved_ca_options(parameters):
    with pytest.raises(ImproperlyConfigured, match="Invalid DATABASE_URL"):
        load_production({
            "DATABASE_URL": f"postgresql://example:fake@db.example.test/lab?{parameters}",
        })


@pytest.mark.parametrize("name", list(VALID))
def test_production_settings_require_each_variable(name):
    with pytest.raises(ImproperlyConfigured, match=f"missing {name}"):
        load_production({name: ""})


@pytest.mark.parametrize("value", ["sqlite:///local.db", "postgresql://u:p@h/d", "postgresql://u:p@h/d?sslmode=disable"])
def test_production_settings_reject_non_tls_or_non_postgres_urls(value):
    with pytest.raises(ImproperlyConfigured, match="Invalid DATABASE_URL"):
        load_production({"DATABASE_URL": value})


def test_production_settings_reject_wildcard_hosts():
    with pytest.raises(ImproperlyConfigured, match="DJANGO_ALLOWED_HOSTS"):
        load_production({"DJANGO_ALLOWED_HOSTS": "*"})


def test_production_settings_reject_short_signing_key():
    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY is too short"):
        load_production({"DJANGO_SECRET_KEY": "short"})


def test_production_settings_reject_non_https_csrf_origins():
    with pytest.raises(ImproperlyConfigured, match="DJANGO_CSRF_TRUSTED_ORIGINS"):
        load_production({"DJANGO_CSRF_TRUSTED_ORIGINS": "http://lab.example.test"})


def test_production_settings_reject_csrf_origin_with_path():
    with pytest.raises(ImproperlyConfigured, match="DJANGO_CSRF_TRUSTED_ORIGINS"):
        load_production({"DJANGO_CSRF_TRUSTED_ORIGINS": "https://lab.example.test/path"})


def test_render_hostname_supplies_exact_host_and_https_origin():
    settings = load_production({
        "DJANGO_ALLOWED_HOSTS": "",
        "DJANGO_CSRF_TRUSTED_ORIGINS": "",
        "RENDER_EXTERNAL_HOSTNAME": "lab-booking-abc.onrender.com",
    })
    assert settings.ALLOWED_HOSTS == ["lab-booking-abc.onrender.com"]
    assert settings.CSRF_TRUSTED_ORIGINS == [
        "https://lab-booking-abc.onrender.com",
    ]


def test_explicit_host_and_origin_override_render_defaults():
    settings = load_production({
        "RENDER_EXTERNAL_HOSTNAME": "lab-booking-abc.onrender.com",
    })
    assert settings.ALLOWED_HOSTS == ["lab.example.test"]
    assert settings.CSRF_TRUSTED_ORIGINS == ["https://lab.example.test"]


@pytest.mark.parametrize("hostname", [
    "other.example.com",
    "lab-booking.onrender.com:443",
    "https://lab-booking.onrender.com",
])
def test_render_hostname_rejects_unexpected_values(hostname):
    with pytest.raises(ImproperlyConfigured, match="Invalid RENDER_EXTERNAL_HOSTNAME"):
        load_production({"RENDER_EXTERNAL_HOSTNAME": hostname})


@override_settings(SECURE_SSL_REDIRECT=True, SECURE_REDIRECT_EXEMPT=[r"^health$"])
def test_health_checks_reach_database_before_https_redirect(db):
    assert Client().get("/health").status_code == 200
    with patch("src.data.health.connection.cursor", side_effect=DatabaseError("fake down")):
        assert Client().get("/health").status_code == 503
    assert Client().get("/no-such-page").status_code == 301


def test_gunicorn_binds_to_supplied_port():
    with patch.dict(os.environ, {"PORT": "12345"}):
        config = importlib.reload(importlib.import_module("src.config.gunicorn_conf"))
    assert config.bind == "0.0.0.0:12345"
    assert config.accesslog is None


def test_gunicorn_rejects_invalid_port():
    with patch.dict(os.environ, {"PORT": "99999"}):
        with pytest.raises(ValueError, match="PORT must be"):
            importlib.reload(importlib.import_module("src.config.gunicorn_conf"))


def test_collected_javascript_is_served_by_whitenoise(db):
    from src.config.base import MIDDLEWARE

    production_middleware = [
        MIDDLEWARE[0], "whitenoise.middleware.WhiteNoiseMiddleware", *MIDDLEWARE[1:],
    ]
    storage = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    with TemporaryDirectory() as directory:
        with override_settings(
            MIDDLEWARE=production_middleware,
            STATIC_ROOT=Path(directory),
            STORAGES=storage,
        ):
            call_command("collectstatic", interactive=False, verbosity=0)
            response = Client().get("/static/js/booking.mjs")
            try:
                assert response.status_code == 200
                assert response["Content-Type"].startswith("text/javascript")
            finally:
                response.close()
