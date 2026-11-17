"""Session/CSRF HTTP adapter for the shared read-only suggestion service."""

from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.utils.timezone import now as business_clock

from src.integrations.gemini import configured_client
from src.services.access import require_authenticated
from src.services.ai_suggestion import suggest_slot
from .booking_http import api_methods, calendar_date, json_object, no_query, slot_json
from .session import current_actor

FAILURES = {
    "not_configured": (503, "La suggestion IA n'est pas configurée. Choisis manuellement."),
    "quota": (503, "Le quota de suggestion IA est atteint. Choisis manuellement."),
    "provider_error": (503, "La suggestion IA est indisponible. Choisis manuellement."),
    "timeout": (504, "La suggestion IA a dépassé le délai. Choisis manuellement."),
    "invalid_output": (502, "La réponse IA est invalide. Choisis manuellement."),
    "candidate_unavailable": (409, "Le créneau proposé n'est plus disponible. Consulte la liste."),
}


@transaction.non_atomic_requests
@api_methods("POST")
def suggestion_api(request: HttpRequest, laboratory_id: int) -> JsonResponse:
    actor = require_authenticated(current_actor(request))
    no_query(request)
    payload = json_object(request, {"date", "need"}, max_bytes=16384)
    result = suggest_slot(actor, laboratory_id, calendar_date(payload["date"]), payload["need"],
                          client=configured_client(), clock=business_clock)
    if result.status == "suggested":
        return JsonResponse({"status": "suggested", "candidate": slot_json(result.candidate)})
    if result.status == "no_candidates":
        return JsonResponse({"status": "no_candidates", "candidate": None,
                             "message": "Aucun créneau réservable pour cette recherche."})
    status, message = FAILURES[result.reason]
    return JsonResponse({"status": "unavailable", "candidate": None,
                         "code": result.reason, "error": message}, status=status)
