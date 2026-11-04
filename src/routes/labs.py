"""JSON catalogue endpoint; authentication errors never redirect to HTML."""

from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from src.services.access import AuthenticationRequired
from src.services.labs import list_laboratories

from .session import current_actor


@never_cache
@require_GET
def laboratories_api(request: HttpRequest) -> JsonResponse:
    try:
        laboratories = list_laboratories(current_actor(request))
    except AuthenticationRequired:
        return JsonResponse({"error": "Connexion requise."}, status=401)
    return JsonResponse({"laboratories": laboratories})
