"""Session/JSON adapters; all booking decisions stay in the shared services."""

from django.http import HttpRequest, JsonResponse

from src.services.access import require_authenticated
from src.services.booking_cancellation import cancel_booking
from src.services.booking_creation import create_booking
from src.services.booking_reads import list_available_slots, list_personal_bookings

from .booking_http import (
    PayloadError, api_methods, booking_json, history_json, json_object, no_query,
    requested_day, slot_json, timestamp,
)
from .session import current_actor


@api_methods("GET")
def availability_api(request: HttpRequest, laboratory_id: int) -> JsonResponse:
    actor = require_authenticated(current_actor(request))
    slots = list_available_slots(actor, laboratory_id, requested_day(request))
    return JsonResponse({"slots": [slot_json(slot) for slot in slots]})


@api_methods("GET", "POST")
def bookings_api(request: HttpRequest) -> JsonResponse:
    actor = require_authenticated(current_actor(request))
    no_query(request)
    if request.method == "GET":
        rows = list_personal_bookings(actor)
        return JsonResponse({"bookings": [history_json(row) for row in rows]})
    payload = json_object(request, {"workstation_id", "starts_at", "ends_at"})
    station_id = payload["workstation_id"]
    if type(station_id) is not int or station_id <= 0:
        raise PayloadError("workstation_id doit être un entier positif.")
    result = create_booking(
        actor, station_id, timestamp(payload["starts_at"]),
        timestamp(payload["ends_at"]),
    )
    return JsonResponse({"booking": booking_json(result)}, status=201)


@api_methods("POST")
def cancel_api(request: HttpRequest, booking_id: int) -> JsonResponse:
    actor = require_authenticated(current_actor(request))
    no_query(request)
    json_object(request, set())
    result = cancel_booking(actor, booking_id)
    return JsonResponse({"booking": booking_json(result)})
