"""Read-only MCP adapters: authenticated service calls, no ORM or HTTP access."""

from datetime import date, datetime, timezone
import json
import re
from typing import Any

from project_runtime import current_actor
from src.services.access import AuthenticationRequired
from src.services import booking_reads

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
]
TOOL_NAMES = frozenset(tool["name"] for tool in TOOLS)


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


def call_tool(parameters: dict[str, Any]) -> dict[str, Any]:
    """Authenticate every call, then invoke exactly the HTTP route's service."""
    try:
        actor = current_actor()
        arguments = parameters.get("arguments", {})
        if not isinstance(arguments, dict):
            raise InvalidToolInput
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
    except Exception:
        # Never serialize driver exceptions, session keys or connection details.
        code, message = "InternalError", "Consultation temporairement indisponible."
    return tool_result({"error": {"code": code, "message": message}}, True)
