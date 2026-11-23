"""Short production-facing errors without stack traces or request data."""

from django.http import HttpRequest, HttpResponse


def not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Return a single readable line for an unknown route."""
    return HttpResponse(
        "Page introuvable.", status=404,
        content_type="text/plain; charset=utf-8",
    )


def server_error(request: HttpRequest) -> HttpResponse:
    """Keep exception details in Django's server log, not in the response."""
    return HttpResponse(
        "Une erreur est survenue.", status=500,
        content_type="text/plain; charset=utf-8",
    )
