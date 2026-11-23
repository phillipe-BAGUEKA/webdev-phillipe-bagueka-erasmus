"""Public, non-sensitive application readiness endpoint."""

from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from src.services.health import is_ready


@never_cache
@require_GET
def health(request: HttpRequest) -> JsonResponse:
    """Expose only generic state, never database connection details."""
    ready = is_ready()
    response = JsonResponse(
        {"status": "ok" if ready else "error", "db": "ok" if ready else "down"},
        status=200 if ready else 503,
    )
    return response
