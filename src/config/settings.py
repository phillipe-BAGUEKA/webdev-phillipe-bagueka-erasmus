"""Local demonstration only. Not production settings."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403 - Django settings inherit the common configuration.
from .base import BASE_DIR

try:
    SECRET_KEY = (BASE_DIR / ".local" / "django-dev-key").read_text(
        encoding="utf-8"
    ).strip()
except FileNotFoundError as error:
    raise ImproperlyConfigured("Run python tools/init_local.py first.") from error
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("The local Django key is missing or invalid.")

DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
DEMO_DATABASE_PATH = BASE_DIR / "data" / "demo.sqlite3"
DEMO_MARKER_PATH = BASE_DIR / "data" / "demo.marker"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DEMO_DATABASE_PATH,
    }
}
# These settings are only for local HTTP. HTTPS settings belong to a later slice.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
