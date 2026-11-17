"""Read-only suggestions using an injected client, independent of HTTP/MCP."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from time import monotonic
from typing import Literal, Protocol

from django.utils import timezone

from src.data.users import account_state
from .access import Actor, AuthenticationRequired, require_authenticated
from .booking_creation import StudentRequired
from .booking_reads import AvailableSlot, list_available_slots

CLIENT_BUDGET_SECONDS = 5.0


class InvalidSuggestionInput(ValueError):
    """The need must be a nonempty string of at most 1,000 characters."""


class ClientError(Exception):
    """The injected client could not return a usable response."""


class ClientUnavailable(ClientError):
    """No configured client is available; do not attempt a provider call."""


class ClientQuotaExceeded(ClientError):
    """The provider quota prevents this attempt."""


@dataclass(frozen=True)
class Candidate:
    """Minimal application facts permitted to leave the suggestion service."""

    candidate_id: str
    workstation_name: str
    starts_at: datetime
    ends_at: datetime


class SuggestionClient(Protocol):
    """One attempt, honoring a monotonic deadline including cleanup.

    Future adapters must stop their own wait by this deadline; the service
    rejects late answers but cannot interrupt a blocking injected function.
    A decoded JSON object is still untrusted. A transport must reject duplicate
    JSON keys and incomplete responses before decoding to this contract.
    """

    def select_candidate(
        self, need: str, candidates: tuple[Candidate, ...], *, deadline: float,
    ) -> object:
        """Return untrusted structured content; never log or retry the request."""


@dataclass(frozen=True)
class SuggestionResult:
    status: Literal["suggested", "no_candidates", "unavailable"]
    candidate: AvailableSlot | None = None
    reason: str | None = None


def _student(actor: Actor | None) -> Actor:
    actor = require_authenticated(actor)
    state = account_state(actor.user_id)
    if state is None:
        raise AuthenticationRequired
    role, active = state
    if not active:
        raise AuthenticationRequired
    if role != "student":
        raise StudentRequired("Only students may request booking suggestions.")
    return Actor(actor.user_id, actor.email, role, active)


def _candidate_slots(slots: list[AvailableSlot]) -> dict[str, AvailableSlot]:
    seen = set()
    result = {}
    for slot in slots:
        key = (slot.workstation_id, slot.starts_at, slot.ends_at)
        if key in seen:
            continue
        seen.add(key)
        result[f"c{len(result) + 1}"] = slot
        if len(result) == 10:
            break
    return result


def _ask(
    client: SuggestionClient, need: str, candidates: tuple[Candidate, ...],
    deadline: float,
) -> tuple[object, str | None]:
    try:
        return client.select_candidate(need, candidates, deadline=deadline), None
    except ClientUnavailable:
        return None, "not_configured"
    except TimeoutError:
        return None, "timeout"
    except ClientQuotaExceeded:
        return None, "quota"
    except Exception:
        # This boundary alone catches arbitrary client errors. Never expose
        # their messages (which may contain prompts or connection secrets).
        return None, "provider_error"


def suggest_slot(
    actor: Actor | None, laboratory_id: int, day: date, need: str,
    *, client: SuggestionClient | None,
    clock: Callable[[], datetime] = timezone.now,
    timer: Callable[[], float] = monotonic,
) -> SuggestionResult:
    """Suggest one presently admissible slot, without reserving or locking it.

    The supplied client sees no actor/history. Free text can itself contain
    personal information; trimming and length checks are not anonymization.
    Callers must not wrap the client wait in a database transaction.
    """
    current = _student(actor)
    if not isinstance(need, str):
        raise InvalidSuggestionInput("Provide a textual need.")
    need = need.strip()
    if not 1 <= len(need) <= 1000 or "\0" in need:
        raise InvalidSuggestionInput("Provide 1 to 1,000 characters without NUL.")
    slots = list_available_slots(current, laboratory_id, day, now=clock())
    choices = _candidate_slots(slots)
    if not choices:
        return SuggestionResult("no_candidates")
    if client is None:
        return SuggestionResult("unavailable", reason="not_configured")
    candidates = tuple(Candidate(
        identifier, slot.workstation_name, slot.starts_at, slot.ends_at,
    ) for identifier, slot in choices.items())
    deadline = timer() + CLIENT_BUDGET_SECONDS
    output, failure = _ask(client, need, candidates, deadline)
    if timer() >= deadline:
        failure = "timeout"
    if failure is not None:
        return SuggestionResult("unavailable", reason=failure)
    if (type(output) is not dict or set(output) != {"candidate_id"}
            or type(output["candidate_id"]) is not str):
        return SuggestionResult("unavailable", reason="invalid_output")
    original = choices.get(output["candidate_id"])
    if original is None:
        return SuggestionResult("unavailable", reason="invalid_output")
    # Keep the original application identity; never trust a model name/time.
    current = _student(actor)
    for slot in list_available_slots(current, laboratory_id, day, now=clock()):
        if (slot.workstation_id, slot.starts_at, slot.ends_at) == (
            original.workstation_id, original.starts_at, original.ends_at,
        ):
            return SuggestionResult("suggested", candidate=slot)
    return SuggestionResult("unavailable", reason="candidate_unavailable")
