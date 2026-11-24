"""Production-only settings: explicit secrets, hosts, TLS and PostgreSQL."""

import os
import re
from urllib.parse import parse_qs, unquote, urlsplit

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import BASE_DIR, MIDDLEWARE


def required(name: str) -> str:
    """Fail at startup without printing a secret or connection string."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"missing {name}: see .env.example")
    return value


SECRET_KEY = required("DJANGO_SECRET_KEY")
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY is too short; see .env.example")
raw_url = required("DATABASE_URL")
render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
if render_hostname and not re.fullmatch(
    r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.onrender\.com",
    render_hostname,
):
    raise ImproperlyConfigured("Invalid RENDER_EXTERNAL_HOSTNAME.")
raw_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "").strip()
raw_origins = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").strip()
if not raw_hosts:
    raw_hosts = render_hostname or required("DJANGO_ALLOWED_HOSTS")
if not raw_origins:
    raw_origins = (
        f"https://{render_hostname}"
        if render_hostname else required("DJANGO_CSRF_TRUSTED_ORIGINS")
    )

ALLOWED_HOSTS = [part.strip() for part in raw_hosts.split(",") if part.strip()]
CSRF_TRUSTED_ORIGINS = [
    part.strip() for part in raw_origins.split(",") if part.strip()
]
if not ALLOWED_HOSTS or any(
    "*" in host or "://" in host for host in ALLOWED_HOSTS
):
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must list specific hostnames.")
if not CSRF_TRUSTED_ORIGINS or any(
    not origin.startswith("https://")
    or "*" in origin
    or not urlsplit(origin).hostname
    or urlsplit(origin).path not in ("", "/")
    or urlsplit(origin).username
    for origin in CSRF_TRUSTED_ORIGINS
):
    raise ImproperlyConfigured("DJANGO_CSRF_TRUSTED_ORIGINS must list HTTPS origins.")

try:
    parsed = urlsplit(raw_url)
    query = parse_qs(parsed.query, strict_parsing=True)
    if (
        parsed.scheme not in {"postgres", "postgresql"}
        or not parsed.hostname or not parsed.path.strip("/")
        or not parsed.username or not parsed.password
        or "sslmode" not in query
        or not set(query) <= {"sslmode", "channel_binding", "sslrootcert"}
        or query["sslmode"] not in (["require"], ["verify-full"])
        or (
            parsed.hostname.endswith(".neon.tech")
            and (
                query["sslmode"] != ["verify-full"]
                or query.get("sslrootcert") != ["system"]
                or query.get("channel_binding") != ["require"]
            )
        )
        or (
            "sslrootcert" in query
            and (
                query["sslrootcert"] != ["system"]
                or query["sslmode"] != ["verify-full"]
            )
        )
        or (
            "channel_binding" in query
            and query["channel_binding"] != ["require"]
        )
    ):
        raise ValueError
    db_port = parsed.port or 5432
except ValueError:
    raise ImproperlyConfigured("Invalid DATABASE_URL; use a TLS PostgreSQL URL.") from None

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parsed.path.lstrip("/")),
        "USER": unquote(parsed.username),
        "PASSWORD": unquote(parsed.password),
        "HOST": parsed.hostname,
        "PORT": db_port,
        "CONN_MAX_AGE": 0,
        "OPTIONS": {
            "sslmode": query["sslmode"][0],
            "connect_timeout": 5,
            **({"channel_binding": "require"} if "channel_binding" in query else {}),
            **({"sslrootcert": "system"} if "sslrootcert" in query else {}),
        },
    },
}

DEBUG = False
MIDDLEWARE = [
    MIDDLEWARE[0],
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^health$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
