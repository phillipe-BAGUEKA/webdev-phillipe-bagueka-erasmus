"""Direct suggestion contracts with isolated PostgreSQL and no network client."""

from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from importlib import import_module
from types import ModuleType
from typing import Any

import pytest
from django.db import connection

from src.data.models import Booking, Laboratory, User, Workstation
from src.services.access import Actor, AuthenticationRequired
from src.services.booking_creation import StudentRequired
from src.services.booking_reads import LaboratoryNotFound, list_available_slots

NOW = datetime(2030, 1, 7, 5, tzinfo=timezone.utc)
DAY = date(2030, 1, 7)


def service() -> ModuleType:
    return import_module("src.services.ai_suggestion")


class FakeClient:
    """Record only synthetic inputs and optionally simulate a client event."""

    def __init__(self, output: object = None, action: Any = None) -> None:
        self.output = {"candidate_id": "c1"} if output is None else output
        self.action = action
        self.calls: list[tuple[str, tuple[Any, ...], float]] = []

    def select_candidate(self, need: str, candidates: tuple[Any, ...],
                         *, deadline: float) -> object:
        self.calls.append((need, candidates, deadline))
        if self.action is not None:
            self.action()
        return self.output


@pytest.fixture
def world(db: None) -> tuple[Any, ...]:
    assert connection.vendor == "postgresql"
    user = User.objects.create_user("suggestion@tests.example")
    lab = Laboratory.objects.create(name="Suggestion tests")
    station = Workstation.objects.create(laboratory=lab, name="A")
    actor = Actor(user.pk, user.email, user.role, True)
    return user, lab, station, actor


def snapshot() -> tuple[Any, ...]:
    return tuple(list(model.objects.order_by("pk").values())
                 for model in (User, Laboratory, Workstation, Booking))


def suggest(world: tuple[Any, ...], client: Any, **changes: Any) -> Any:
    _, lab, _, actor = world
    inputs = dict(actor=actor, laboratory_id=lab.pk, day=DAY, need="  a desk  ",
                  client=client, clock=lambda: NOW, timer=lambda: 100.0)
    inputs.update(changes)
    return service().suggest_slot(**inputs)


@pytest.mark.parametrize("case", ["anonymous", "inactive", "staff", "missing"],
                         ids=lambda value: f"AC-29-access-{value}")
def test_refuse_actor_without_call_or_mutation(world: tuple[Any, ...], case: str) -> None:
    user, _, _, actor = world
    expected = AuthenticationRequired
    changes = {}
    if case == "anonymous":
        changes["actor"] = None
    elif case == "inactive":
        user.is_active = False
        user.save()
    elif case == "staff":
        user.role = "personnel"
        user.save()
        expected = StudentRequired
    else:
        user.delete()
    before = snapshot()
    client = FakeClient()
    with pytest.raises(expected):
        suggest(world, client, **changes)
    assert not client.calls
    assert snapshot() == before


@pytest.mark.parametrize("need", [None, 1, True, "", " \n\t", "a\0b", "x" * 1001],
                         ids=[f"AC-29-input-{n}" for n in range(7)])
def test_invalid_need_is_explicit(world: tuple[Any, ...], need: Any) -> None:
    before = snapshot()
    client = FakeClient()
    with pytest.raises(service().InvalidSuggestionInput):
        suggest(world, client, need=need)
    assert not client.calls
    assert snapshot() == before


@pytest.mark.parametrize("change", [
    {"laboratory_id": True}, {"laboratory_id": 0}, {"laboratory_id": "1"},
    {"day": NOW}, {"day": "2030-01-07"}, {"clock": lambda: NOW.replace(tzinfo=None)},
], ids=[f"AC-29-filters-{n}" for n in range(6)])
def test_invalid_filters(world: tuple[Any, ...], change: dict[str, Any]) -> None:
    from src.services.booking_reads import InvalidReadInput

    client = FakeClient()
    with pytest.raises(InvalidReadInput):
        suggest(world, client, **change)
    assert not client.calls


@pytest.mark.parametrize("label", ["AC-29-missing-lab"])
def test_missing_lab(world: tuple[Any, ...], label: str) -> None:
    with pytest.raises(LaboratoryNotFound):
        suggest(world, FakeClient(), laboratory_id=999999)


@pytest.mark.parametrize("hour,expected", [(12, 3), (5, 10)],
                         ids=["AC-29-three", "AC-29-more-than-ten"])
def test_bound_order_and_payload(world: tuple[Any, ...], hour: int, expected: int) -> None:
    _, lab, _, actor = world
    if hour == 5:
        Workstation.objects.create(laboratory=lab, name="B")
    now = NOW.replace(hour=hour)
    available = list_available_slots(actor, lab.pk, DAY, now=now)
    before = snapshot()
    client = FakeClient()
    result = suggest(world, client, clock=lambda: now, need=" " + "x" * 1000 + " ")
    need, candidates, deadline = client.calls[0]
    assert need == "x" * 1000
    assert deadline == 105.0
    assert len(candidates) == expected
    assert [candidate.candidate_id for candidate in candidates] == [
        f"c{n + 1}" for n in range(expected)
    ]
    assert [(c.starts_at, c.ends_at, c.workstation_name) for c in candidates] == [
        (s.starts_at, s.ends_at, s.workstation_name) for s in available[:expected]
    ]
    assert set(asdict(candidates[0])) == {
        "candidate_id", "workstation_name", "starts_at", "ends_at",
    }
    assert result.status == "suggested"
    assert result.candidate == available[0]
    assert result.reason is None
    assert len(client.calls) == 1
    assert snapshot() == before


@pytest.mark.parametrize("label", ["AC-30-empty"])
def test_empty_means_zero_calls(world: tuple[Any, ...], label: str) -> None:
    client = FakeClient()
    before = snapshot()
    result = suggest(world, client, day=date(2030, 1, 6))
    assert (result.status, result.candidate, result.reason) == ("no_candidates", None, None)
    assert not client.calls
    assert snapshot() == before
    assert suggest(world, None, day=date(2030, 1, 6)).status == "no_candidates"


@pytest.mark.parametrize("label", ["AC-31-payload-AC-32-application-values"])
def test_only_application_fields_and_no_identity(world: tuple[Any, ...], label: str) -> None:
    _, _, station, _ = world

    def rename() -> None:
        station.name = "Current application name"
        station.save()

    client = FakeClient(action=rename)
    result = suggest(world, client, need="A quiet workstation")
    assert result.candidate.workstation_name == "Current application name"
    assert client.calls[0][0] == "A quiet workstation"
    assert "suggestion@tests.example" not in repr(client.calls)
    assert Booking.objects.count() == 0


@pytest.mark.parametrize("output", [
    "{\"candidate_id\":\"c1\"}", [], False, 3, {}, {"candidate_id": None},
    {"candidate_id": True}, {"candidate_id": 1}, {"candidate_id": ""},
    {"candidate_id": "c99"}, {"candidate_id": "c1", "name": "invented"},
], ids=[f"AC-33-invalid-{n}" for n in range(11)])
def test_reject_untrusted_response(world: tuple[Any, ...], output: object) -> None:
    before = snapshot()
    client = FakeClient(output)
    result = suggest(world, client)
    assert (result.status, result.candidate, result.reason) == (
        "unavailable", None, "invalid_output",
    )
    assert len(client.calls) == 1
    assert snapshot() == before


@pytest.mark.parametrize("change", ["offline", "occupied", "quota", "personal", "time"],
                         ids=lambda value: f"AC-33-recheck-{value}")
def test_recheck_after_client(world: tuple[Any, ...], change: str) -> None:
    user, lab, station, _ = world
    now = [NOW]

    def change_availability() -> None:
        if change == "offline":
            station.is_operational = False
            station.save()
        elif change == "time":
            now[0] = NOW.replace(hour=6)
        else:
            owner = user
            target = station
            if change == "occupied":
                owner = User.objects.create_user("competitor@tests.example")
            if change == "personal":
                target = Workstation.objects.create(laboratory=lab, name="Other")
            hours = [8, 9, 10] if change == "quota" else [6]
            for hour in hours:
                start = NOW.replace(hour=hour)
                Booking.objects.create(owner=owner, workstation=target, starts_at=start,
                                       ends_at=start + timedelta(hours=1))

    client = FakeClient(action=change_availability)
    result = suggest(world, client, clock=lambda: now[0])
    assert result.reason == "candidate_unavailable"
    assert result.candidate is None
    assert len(client.calls) == 1
    assert not Booking.objects.filter(cancelled_at__isnull=False).exists()


@pytest.mark.parametrize("case", ["inactive", "staff", "deleted"],
                         ids=lambda value: f"AC-33-actor-recheck-{value}")
def test_recheck_actor(world: tuple[Any, ...], case: str) -> None:
    user, _, _, _ = world

    def change_actor() -> None:
        if case == "deleted":
            user.delete()
        else:
            if case == "inactive":
                user.is_active = False
            else:
                user.role = "personnel"
            user.save()

    with pytest.raises(StudentRequired if case == "staff" else AuthenticationRequired):
        suggest(world, FakeClient(action=change_actor))
    assert Booking.objects.count() == 0


@pytest.mark.parametrize("kind,reason", [
    ("ClientUnavailable", "not_configured"), ("ClientQuotaExceeded", "quota"),
    ("ClientError", "provider_error"), ("TimeoutError", "timeout"),
    ("RuntimeError", "provider_error"),
], ids=[f"AC-35-AC-36-error-{n}" for n in range(5)])
def test_errors_are_safe_and_never_retried(
    world: tuple[Any, ...], kind: str, reason: str, caplog: Any,
) -> None:
    error_type = {"TimeoutError": TimeoutError, "RuntimeError": RuntimeError}.get(kind)
    if error_type is None:
        error_type = getattr(service(), kind)

    def fail() -> None:
        raise error_type("synthetic-sensitive-need-and-response")

    before = snapshot()
    client = FakeClient(action=fail)
    result = suggest(world, client)
    assert (result.status, result.candidate, result.reason) == ("unavailable", None, reason)
    assert len(client.calls) == 1
    assert "synthetic-sensitive" not in repr(result) + caplog.text
    assert snapshot() == before


@pytest.mark.parametrize("label", ["AC-35-client-absent"])
def test_absent_client(world: tuple[Any, ...], label: str) -> None:
    before = snapshot()
    result = suggest(world, None)
    assert result.reason == "not_configured"
    assert result.candidate is None
    assert snapshot() == before


@pytest.mark.parametrize("elapsed", [5.0, 5.1], ids=["AC-36-at-deadline", "AC-36-late"])
def test_late_response_is_not_suggested(world: tuple[Any, ...], elapsed: float) -> None:
    ticks = iter([100.0, 100.0 + elapsed])
    before = snapshot()
    client = FakeClient()
    result = suggest(world, client, timer=lambda: next(ticks))
    assert result.reason == "timeout"
    assert len(client.calls) == 1
    assert snapshot() == before


@pytest.mark.parametrize("label", ["AC-29-deduplicate-AC-33-full-recheck"])
def test_duplicates_and_changed_top_ten(world: tuple[Any, ...], monkeypatch: Any, label: str) -> None:
    _, lab, _, actor = world
    slots = list_available_slots(actor, lab.pk, DAY, now=NOW)
    replies = iter([[slots[0], slots[0]] + slots, [slots[-1]] * 10 + slots])
    monkeypatch.setattr(service(), "list_available_slots", lambda *args, **kwargs: next(replies))
    client = FakeClient({"candidate_id": "c1"})
    result = suggest(world, client)
    assert result.candidate == slots[0]
    assert len(client.calls[0][1]) == 10


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("label", ["AC-32-no-transaction-no-mutation"])
def test_client_wait_holds_no_transaction(label: str) -> None:
    user = User.objects.create_user("no-transaction@tests.example")
    lab = Laboratory.objects.create(name="Autocommit tests")
    station = Workstation.objects.create(laboratory=lab, name="A")
    world = user, lab, station, Actor(user.pk, user.email, user.role, True)

    def inspect_transaction() -> None:
        assert connection.get_autocommit()
        assert not connection.in_atomic_block

    before = snapshot()
    assert suggest(world, FakeClient(action=inspect_transaction)).status == "suggested"
    assert snapshot() == before
