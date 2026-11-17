"""Authenticated MCP adapters calling shared services without ORM or HTTP."""

from datetime import date, datetime, timezone
import json
import re
from typing import Any

from project_runtime import current_actor
from src.services.access import AuthenticationRequired
from src.services import booking_cancellation, booking_creation, booking_reads

TOOLS = [
    {
        "name": "list_free_slots",
        "description": (
            "Consulter les créneaux réservables pour un laboratoire et une date ; "
            "cette lecture ne réserve rien."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "laboratory_id": {"type": "integer", "minimum": 1},
                "date": {"type": "string", "format": "date"},
            },
            "required": ["laboratory_id", "date"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "my_bookings",
        "description": (
            "Consulter uniquement son historique de réservations, avec les "
            "annulations et l'état actuel des postes."
        ),
        "inputSchema": {
            "type": "object", "properties": {}, "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "book_slot",
        "description": (
            "Après confirmation explicite de l'utilisateur, réserver pour soi "
            "un poste sur un créneau précis. Création non idempotente : après "
            "une réponse perdue, consulter my_bookings avant toute décision."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "workstation_id": {"type": "integer", "minimum": 1},
                "starts_at": {"type": "string", "format": "date-time"},
                "ends_at": {"type": "string", "format": "date-time"},
            },
            "required": ["workstation_id", "starts_at", "ends_at"],
            "additionalProperties": False,
        },
        "annotations": {
            "readOnlyHint": False, "destructiveHint": False,
            "idempotentHint": False, "openWorldHint": False,
        },
    },
    {
        "name": "cancel_booking",
        "description": (
            "Après confirmation explicite, annuler sa propre réservation avant "
            "son début. Répéter une annulation déjà effectuée restitue son état "
            "sans nouvelle écriture, toujours après contrôle du propriétaire."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"booking_id": {"type": "integer", "minimum": 1}},
            "required": ["booking_id"], "additionalProperties": False,
        },
        "annotations": {
            "readOnlyHint": False, "destructiveHint": True,
            "idempotentHint": True, "openWorldHint": False,
        },
    },
]
TOOL_NAMES = frozenset(tool["name"] for tool in TOOLS)
BOOKING_ERRORS = {
    booking_creation.StudentRequired: "Seuls les étudiants peuvent réserver.",
    booking_creation.WorkstationNotFound: "Poste introuvable.",
    booking_creation.WorkstationUnavailable: "Ce poste est hors service.",
    booking_creation.InvalidBookingInput: "Identifiant ou créneau invalide.",
    booking_creation.SlotNotFuture: "Le créneau doit commencer dans le futur.",
    booking_creation.WorkstationConflict: "Ce poste est déjà réservé sur ce créneau.",
    booking_creation.PersonalConflict: "Tu as déjà une réservation sur ce créneau.",
    booking_creation.QuotaExceeded: "Tu as déjà trois réservations à venir.",
    booking_cancellation.BookingNotFound: "Réservation introuvable.",
    booking_cancellation.NotBookingOwner: (
        "Tu ne peux annuler que tes propres réservations."
    ),
    booking_cancellation.CancellationTooLate: (
        "Ce créneau a commencé ; annulation impossible."
    ),
    booking_cancellation.BookingChanged: (
        "La réservation a changé. Consulte ton historique."
    ),
}


class InvalidToolInput(Exception):
    """Transport validation failed before the shared read service was called."""


def tool_result(payload: dict[str, Any], is_error: bool = False) -> dict[str, Any]:
    """Keep structured content and legacy text exactly equivalent."""
    return {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        "structuredContent": payload,
        "isError": is_error,
    }


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def slot_json(row: booking_reads.AvailableSlot) -> dict[str, Any]:
    return {
        "workstation_id": row.workstation_id,
        "workstation_name": row.workstation_name,
        "starts_at": utc_text(row.starts_at), "ends_at": utc_text(row.ends_at),
    }


def history_json(row: booking_reads.PersonalBooking) -> dict[str, Any]:
    return {
        "id": row.booking_id,
        "workstation_id": row.workstation_id,
        "workstation_name": row.workstation_name,
        "laboratory_id": row.laboratory_id,
        "laboratory_name": row.laboratory_name,
        "starts_at": utc_text(row.starts_at), "ends_at": utc_text(row.ends_at),
        "created_at": utc_text(row.created_at),
        "cancelled_at": utc_text(row.cancelled_at) if row.cancelled_at else None,
        "is_operational": row.is_operational, "status": row.status,
    }


def calendar_day(value: object) -> date:
    if (not isinstance(value, str)
            or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value)):
        raise InvalidToolInput
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise InvalidToolInput from None


def positive_id(value: object) -> int:
    if type(value) is not int or value <= 0:
        raise InvalidToolInput
    return value


def timestamp(value: object) -> datetime:
    """Parse transport syntax only; canonical slot rules belong to the service."""
    if (not isinstance(value, str)
            or not re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T", value)):
        raise InvalidToolInput
    try:
        instant = datetime.fromisoformat(value)
    except ValueError:
        raise InvalidToolInput from None
    if instant.utcoffset() is None:
        raise InvalidToolInput
    return instant


def booking_json(
    row: booking_creation.CreatedBooking | booking_cancellation.CancellationResult,
) -> dict[str, Any]:
    cancelled = getattr(row, "cancelled_at", None)
    return {
        "id": row.booking_id, "workstation_id": row.workstation_id,
        "starts_at": utc_text(row.starts_at), "ends_at": utc_text(row.ends_at),
        "created_at": utc_text(row.created_at),
        "cancelled_at": utc_text(cancelled) if cancelled is not None else None,
    }


def call_tool(parameters: dict[str, Any]) -> dict[str, Any]:
    """Authenticate every call, then invoke exactly the HTTP route's service."""
    try:
        actor = current_actor()
        arguments = parameters.get("arguments", {})
        if not isinstance(arguments, dict):
            raise InvalidToolInput
        if parameters.get("name") == "book_slot":
            if set(arguments) != {"workstation_id", "starts_at", "ends_at"}:
                raise InvalidToolInput
            row = booking_creation.create_booking(
                actor, positive_id(arguments["workstation_id"]),
                timestamp(arguments["starts_at"]), timestamp(arguments["ends_at"]),
            )
            return tool_result({"booking": booking_json(row)})
        if parameters.get("name") == "cancel_booking":
            if set(arguments) != {"booking_id"}:
                raise InvalidToolInput
            row = booking_cancellation.cancel_booking(
                actor, positive_id(arguments["booking_id"]),
            )
            return tool_result({"booking": booking_json(row)})
        if parameters.get("name") == "my_bookings":
            if arguments:
                raise InvalidToolInput
            rows = booking_reads.list_personal_bookings(actor)
            return tool_result({"bookings": [history_json(row) for row in rows]})
        if parameters.get("name") != "list_free_slots":
            raise InvalidToolInput
        if set(arguments) != {"laboratory_id", "date"}:
            raise InvalidToolInput
        laboratory_id = arguments["laboratory_id"]
        if type(laboratory_id) is not int or laboratory_id <= 0:
            raise InvalidToolInput
        day = calendar_day(arguments["date"])
        slots = booking_reads.list_available_slots(actor, laboratory_id, day)
        return tool_result({"slots": [slot_json(slot) for slot in slots]})
    except AuthenticationRequired:
        code, message = "AuthenticationRequired", "Connexion requise."
    except InvalidToolInput:
        code, message = "InvalidToolInput", "Paramètres invalides pour cet outil."
    except booking_reads.InvalidReadInput:
        code, message = "InvalidReadInput", "Date ou identifiant invalide."
    except booking_reads.LaboratoryNotFound:
        code, message = "LaboratoryNotFound", "Laboratoire introuvable."
    except booking_creation.BookingError as error:
        message = BOOKING_ERRORS.get(type(error))
        if message is None:
            code, message = "InternalError", "Opération temporairement indisponible."
        else:
            code = type(error).__name__
    except Exception:
        # Never serialize driver exceptions, session keys or connection details.
        code, message = "InternalError", "Opération temporairement indisponible."
    return tool_result({"error": {"code": code, "message": message}}, True)
