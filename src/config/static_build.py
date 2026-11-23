"""Non-secret settings used only to collect static files in the image build."""

from .base import *  # noqa: F403
from .base import BASE_DIR

STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
