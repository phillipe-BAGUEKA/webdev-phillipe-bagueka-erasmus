"""HTTP-only parsing, serialization and explicit booking error translation."""

from collections.abc import Callable
from datetime import date, datetime, timezone
from functools import wraps
import json
import logging
import re
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache

from src.services.access import AuthenticationRequired
from src.services.booking_cancellation import (
    BookingChanged, BookingNotFound, CancellationResult, CancellationTooLate,
    NotBookingOwner,
)
from src.services.booking_creation import (
    CreatedBooking, InvalidBookingInput, PersonalConflict, QuotaExceeded,
    SlotNotFuture, StudentRequired, WorkstationConflict, WorkstationNotFound,
    WorkstationUnavailable,
)
from src.services.booking_reads import (
    AvailableSlot, InvalidReadInput, LaboratoryNotFound, PersonalBooking,
)

API_ROUTE_NAMES = {"availability-api", "bookings-api", "cancel-booking-api"}
LOGGER = logging.getLogger(__name__)
ERRORS = {
    AuthenticationRequired: (401, "Connexion requise."),
    StudentRequired: (403, "Seuls les étudiants peuvent réserver."),
    NotBookingOwner: (403, "Tu ne peux annuler que tes propres réservations."),
    LaboratoryNotFound: (404, "Laboratoire introuvable."),
    WorkstationNotFound: (404, "Poste introuvable."),
    BookingNotFound: (404, "Réservation introuvable."),
    WorkstationUnavailable: (409, "Ce poste est hors service."),
    WorkstationConflict: (409, "Ce poste est déjà réservé sur ce créneau."),
    PersonalConflict: (409, "Tu as déjà une réservation sur ce créneau."),
    QuotaExceeded: (409, "Tu as déjà trois réservations à venir."),
    CancellationTooLate: (409, "Ce créneau a commencé ; annulation impossible."),
    BookingChanged: (409, "La réservation a changé. Renouvelle ta demande."),
    SlotNotFuture: (422, "Le créneau doit commencer dans le futur."),
    InvalidBookingInput: (422, "Identifiant ou créneau invalide."),
    InvalidReadInput: (422, "Date ou identifiant invalide."),
}


class PayloadError(Exception):
    """Transport input error, separate from service admissibility decisions."""

    def __init__(self, message: str, status: int = 422) -> None:
        super().__init__(message)
        self.status = status


def api_methods(*methods: str) -> Callable:
    """Bound only the new API views; keep unexpected failures as safe JSON 500."""
    def decorate(view: Callable) -> Callable:
        @never_cache
        @wraps(view)
        def wrapped(request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
            if request.method not in methods:
                response = JsonResponse({"error": "Méthode non autorisée."}, status=405)
                response["Allow"] = ", ".join(methods)
                return response
            try:
                return view(request, *args, **kwargs)
            except PayloadError as error:
                return JsonResponse({"error": str(error)}, status=error.status)
            except Exception as error:
                for error_type, (status, message) in ERRORS.items():
                    if isinstance(error, error_type):
                        return JsonResponse({"error": message}, status=status)
                # Never log exception messages/arguments: database failures may
                # contain SQL or sensitive values. Preserve HTTP 500 semantics.
                LOGGER.error("Internal booking API failure (%s).", type(error).__name__)
                return JsonResponse({"error": "Erreur interne."}, status=500)
        return wrapped
    return decorate


def no_query(request: HttpRequest) -> None:
    if request.GET:
        raise PayloadError("Aucun paramètre de recherche n'est accepté ici.")


def requested_day(request: HttpRequest) -> date:
    if set(request.GET) != {"date"} or len(request.GET.getlist("date")) != 1:
        raise PayloadError("Fournis une seule date au format YYYY-MM-DD.")
    value = request.GET["date"]
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise PayloadError("Date attendue au format YYYY-MM-DD.")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise PayloadError("Date invalide.") from error


def json_object(request: HttpRequest, fields: set[str]) -> dict[str, Any]:
    if request.content_type != "application/json":
        raise PayloadError("Content-Type application/json requis.", 415)
    try:
        value = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        raise PayloadError("JSON mal formé.", 400) from error
    if not isinstance(value, dict) or set(value) != fields:
        raise PayloadError("Champs JSON manquants ou non autorisés.")
    return value


def timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T", value):
        raise PayloadError("Date et heure ISO 8601 avec fuseau requises.")
    try:
        instant = datetime.fromisoformat(value)
    except ValueError as error:
        raise PayloadError("Date et heure invalides.") from error
    if instant.utcoffset() is None:
        raise PayloadError("Le fuseau horaire est obligatoire.")
    return instant


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def slot_json(slot: AvailableSlot) -> dict[str, Any]:
    return {
        "workstation_id": slot.workstation_id,
        "workstation_name": slot.workstation_name,
        "starts_at": utc_text(slot.starts_at),
        "ends_at": utc_text(slot.ends_at),
    }


def booking_json(row: CreatedBooking | CancellationResult) -> dict[str, Any]:
    cancelled_at = getattr(row, "cancelled_at", None)
    return {
        "id": row.booking_id,
        "workstation_id": row.workstation_id,
        "starts_at": utc_text(row.starts_at),
        "ends_at": utc_text(row.ends_at),
        "created_at": utc_text(row.created_at),
        "cancelled_at": utc_text(cancelled_at) if cancelled_at is not None else None,
    }


def history_json(row: PersonalBooking) -> dict[str, Any]:
    return {
        "id": row.booking_id,
        "workstation_id": row.workstation_id,
        "workstation_name": row.workstation_name,
        "laboratory_id": row.laboratory_id,
        "laboratory_name": row.laboratory_name,
        "starts_at": utc_text(row.starts_at),
        "ends_at": utc_text(row.ends_at),
        "created_at": utc_text(row.created_at),
        "cancelled_at": utc_text(row.cancelled_at) if row.cancelled_at is not None else None,
        "is_operational": row.is_operational,
        "status": row.status,
    }
