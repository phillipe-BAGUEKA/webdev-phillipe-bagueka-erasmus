"""REST simulation and real local processes, never a Google connection."""

import io
import json
import subprocess
import sys
import os
import socket
from types import SimpleNamespace
from datetime import datetime, timezone
from importlib import import_module
from time import monotonic, sleep
from typing import Any
from unittest.mock import Mock
from urllib.error import HTTPError

import pytest

from src.services.ai_suggestion import (
    Candidate, ClientError, ClientQuotaExceeded, ClientUnavailable,
)


@pytest.fixture(autouse=True)
def no_network(monkeypatch: Any) -> None:
    def refuse(*args: Any, **kwargs: Any) -> None:
        pytest.fail("Network forbidden in AI adapter tests.")

    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket.socket, "connect", refuse)


def transport() -> Any:
    return import_module("src.integrations.gemini_http")


def adapter() -> Any:
    return import_module("src.integrations.gemini")


def candidate() -> tuple[Candidate, ...]:
    return (Candidate("c1", "A", datetime(2030, 1, 7, 6, tzinfo=timezone.utc),
                      datetime(2030, 1, 7, 7, tzinfo=timezone.utc)),)


def answer(value: object = None) -> bytes:
    text = json.dumps({"candidate_id": "c1"} if value is None else value)
    return json.dumps({"candidates": [{"finishReason": "STOP", "content": {
        "parts": [{"text": text}],
    }}]}).encode()


def response(body: bytes, status: int = 200, content_type: str = "application/json") -> Any:
    result = Mock()
    result.status = status
    result.headers = {"Content-Type": content_type}
    result.read = io.BytesIO(body).read
    result.__enter__ = Mock(return_value=result)
    result.__exit__ = Mock(return_value=False)
    return result


@pytest.mark.parametrize("label", ["AC-31-REST-AC-32-structured"])
def test_one_rest_request_has_only_minimal_inputs(label: str) -> None:
    opener = Mock()
    opener.open.return_value = response(answer())
    result = transport().generate("synthetic-key", "A desk", [
        {"candidate_id": "c1", "workstation_name": "A", "starts_at": "2030-01-07T06:00:00Z",
         "ends_at": "2030-01-07T07:00:00Z"},
    ], deadline=monotonic() + 5, opener=opener)
    assert result == {"candidate_id": "c1"}
    assert opener.open.call_count == 1
    request = opener.open.call_args.args[0]
    assert request.full_url.endswith("/gemini-3.5-flash-lite:generateContent")
    assert "synthetic-key" not in request.full_url
    assert request.get_header("X-goog-api-key") == "synthetic-key"
    payload = json.loads(request.data)
    supplied = json.loads(payload["contents"][0]["parts"][0]["text"])
    assert supplied["need"] == "A desk"
    assert set(supplied) == {"need", "candidates"}
    config = payload["generationConfig"]
    assert config["candidateCount"] == 1
    assert config["responseMimeType"] == "application/json"
    assert config["responseJsonSchema"]["properties"]["candidate_id"]["enum"] == ["c1"]
    assert 0 < opener.open.call_args.kwargs["timeout"] <= 5


@pytest.mark.parametrize("body", [
    b"not-json", b"", b"x" * 65537, b'{}', b'{"promptFeedback":{"blockReason":"SAFETY"}}',
    b'{"candidates":[]}', b'{"candidates":[{},{}]}',
    b'{"candidates":[{"finishReason":"MAX_TOKENS","content":{"parts":[]}}]}',
    b'{"candidates":[{"finishReason":"STOP","content":{"parts":[{"text":"{}"},{"text":"{}"}]}}]}',
    b'{"candidates":[{"finishReason":"STOP","content":{"parts":[{"text":"{\\\"candidate_id\\\":\\\"c1\\\",\\\"candidate_id\\\":\\\"c2\\\"}"}]}}]}',
    answer({"candidate_id": 1}), answer({"candidate_id": "unknown"}),
    answer({"candidate_id": "c1", "extra": "invented"}),
], ids=[f"AC-33-REST-invalid-{n}" for n in range(13)])
def test_rest_rejects_unusable_output(body: bytes) -> None:
    opener = Mock()
    opener.open.return_value = response(body)
    with pytest.raises(transport().TransportFailure) as caught:
        transport().generate("fake", "private synthetic need", [{"candidate_id": "c1"}],
                             deadline=monotonic() + 5, opener=opener)
    assert caught.value.reason == "invalid_output"
    assert "private" not in str(caught.value)
    assert opener.open.call_count == 1


@pytest.mark.parametrize("status,reason", [(429, "quota"), (500, "provider_error"),
                                         (403, "provider_error"), (302, "provider_error")],
                         ids=lambda value: f"AC-35-{value}")
def test_http_errors_no_retry(status: int, reason: str) -> None:
    opener = Mock()
    opener.open.return_value = response(b"sensitive raw error", status)
    with pytest.raises(transport().TransportFailure) as caught:
        transport().generate("fake", "need", [], deadline=monotonic() + 5, opener=opener)
    assert caught.value.reason == reason
    assert opener.open.call_count == 1


@pytest.mark.parametrize("kind", [TimeoutError, OSError], ids=["AC-36-socket", "AC-35-network"])
def test_network_exceptions_are_safe(kind: type[Exception]) -> None:
    opener = Mock()
    opener.open.side_effect = kind("synthetic-sensitive")
    with pytest.raises(transport().TransportFailure) as caught:
        transport().generate("fake", "need", [], deadline=monotonic() + 5, opener=opener)
    assert caught.value.reason == ("timeout" if kind is TimeoutError else "provider_error")
    assert "synthetic-sensitive" not in str(caught.value)
    assert opener.open.call_count == 1


@pytest.mark.parametrize("mode", ["normal", "blocked", "blocked-input", "excessive",
                                  "crash", "slow-cleanup", "cleanup-delay", "malformed", "quota",
                                  "timeout", "invalid_output", "not_configured", "provider_error"],
                         ids=lambda value: f"AC-35-AC-36-process-{value}")
def test_real_process_is_bounded_and_reaped(mode: str, monkeypatch: Any,
                                          record_property: Any) -> None:
    real_spawn = subprocess.Popen
    children = []

    def spawn(*args: Any, **kwargs: Any) -> Any:
        assert "synthetic-key" not in repr(args)
        assert "GEMINI_API_KEY" not in kwargs["env"]
        child = real_spawn(*args, **kwargs)
        if mode == "cleanup-delay":
            actual_wait = child.wait

            def delayed_wait(timeout: float | None = None) -> int:
                assert timeout is not None
                started = monotonic()
                sleep(min(0.25, timeout))
                return actual_wait(timeout=max(0, timeout - (monotonic() - started)))

            child.wait = delayed_wait
        children.append(child)
        return child

    monkeypatch.setattr(adapter().subprocess, "Popen", spawn)
    client = adapter().GeminiClient("synthetic-key", worker_command=(
        sys.executable, "-m", "tests.ai_worker_fixture", mode,
    ))
    started = monotonic()
    if mode == "normal":
        assert client.select_candidate("x" * 1000, candidate(), deadline=started + 5) == {
            "candidate_id": "c1",
        }
    else:
        error = TimeoutError if mode in {
            "blocked", "blocked-input", "slow-cleanup", "cleanup-delay", "timeout",
        } else ClientError
        if mode == "quota":
            error = ClientQuotaExceeded
        if mode == "not_configured":
            error = ClientUnavailable
        with pytest.raises(error):
            client.select_candidate("x" * 1000, candidate(), deadline=started + 5)
    elapsed = monotonic() - started
    record_property("elapsed_seconds", round(elapsed, 6))
    assert elapsed < 5.35  # 350 ms scheduler/instrumentation tolerance, not added budget.
    assert len(children) == 1 and children[0].poll() is not None
    assert children[0].stdin.closed and children[0].stdout.closed
    assert "synthetic-key" not in repr(client)


@pytest.mark.parametrize("label", ["AC-35-disabled-no-key-read"])
def test_configuration_defaults_to_no_client(label: str, monkeypatch: Any) -> None:
    environment = {}
    assert adapter().configured_client(environment) is None
    assert environment == {}


@pytest.mark.parametrize("environment,present", [
    ({"LAB_BOOKING_AI_ENABLED": "0", "GEMINI_API_KEY": "fake"}, False),
    ({"LAB_BOOKING_AI_ENABLED": "1"}, False),
    ({"LAB_BOOKING_AI_ENABLED": "1", "GEMINI_API_KEY": " fake "}, True),
], ids=["AC-35-disabled", "AC-35-key-absent", "AC-31-synthetic-config"])
def test_configuration_uses_only_explicit_synthetic_environment(
    environment: dict[str, str], present: bool,
) -> None:
    assert (adapter().configured_client(environment) is not None) is present


@pytest.mark.parametrize("label", ["AC-31-AC-35-no-implicit-handlers"])
def test_default_opener_cannot_redirect_or_retry(monkeypatch: Any, label: str) -> None:
    def open_fake(opener: Any, request: Any, **kwargs: Any) -> Any:
        assert [type(handler).__name__ for handler in opener.handlers] == ["HTTPSHandler"]
        return response(answer())

    monkeypatch.setattr(transport().OpenerDirector, "open", open_fake)
    assert transport().generate("fake", "desk", [{"candidate_id": "c1"}],
                                deadline=monotonic() + 5) == {"candidate_id": "c1"}


@pytest.mark.parametrize("case", ["normal", "quota", "unexpected", "oversize"],
                         ids=lambda value: f"AC-33-AC-35-worker-{value}")
def test_worker_entry_with_substituted_transport(case: str, monkeypatch: Any) -> None:
    worker = import_module("src.integrations.gemini_worker")
    packet = json.dumps({"api_key": "synthetic", "need": "desk", "candidates": [],
                         "deadline": 123.0}).encode()
    if case == "oversize":
        packet = b"x" * 16385
    output = io.StringIO()
    monkeypatch.setattr(worker, "sys", SimpleNamespace(
        stdin=SimpleNamespace(buffer=io.BytesIO(packet)), stdout=output,
    ))

    def fake(*args: Any, **kwargs: Any) -> dict[str, str]:
        if case == "quota":
            raise transport().TransportFailure("quota")
        if case == "unexpected":
            raise RuntimeError("synthetic-secret")
        return {"candidate_id": "c1"}

    monkeypatch.setattr(worker, "generate", fake)
    worker.main()
    result = json.loads(output.getvalue())
    assert result == ({"value": {"candidate_id": "c1"}} if case == "normal" else {
        "error": {"quota": "quota", "unexpected": "provider_error",
                  "oversize": "invalid_output"}[case],
    })
    assert "synthetic-secret" not in output.getvalue()


@pytest.mark.parametrize("label", ["AC-35-real-worker-missing-packet-no-network"])
def test_real_default_worker_fails_closed(label: str) -> None:
    environment = {name: os.environ[name] for name in (
        "SystemRoot", "WINDIR", "TEMP", "TMP", "COVERAGE_RCFILE", "COVERAGE_FILE",
    ) if name in os.environ}
    result = subprocess.run([sys.executable, "-m", "src.integrations.gemini_worker"],
                            input=b"{}", capture_output=True, env=environment, timeout=5)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"error": "provider_error"}
    assert result.stderr == b""


@pytest.mark.parametrize("body,content_type", [(answer(), "text/plain"), (b"NaN", "application/json")],
                         ids=["AC-33-content-type", "AC-33-json-constant"])
def test_media_type_and_nonstandard_json(body: bytes, content_type: str) -> None:
    opener = Mock()
    opener.open.return_value = response(body, content_type=content_type)
    with pytest.raises(transport().TransportFailure):
        transport().generate("fake", "desk", [], deadline=monotonic() + 5, opener=opener)


@pytest.mark.parametrize("label", ["AC-35-AC-36-no-attempt"])
def test_absent_key_and_expired_deadline_do_not_open(label: str) -> None:
    opener = Mock()
    for key, deadline, reason in [("", monotonic() + 5, "not_configured"),
                                  ("fake", monotonic() - 1, "timeout")]:
        with pytest.raises(transport().TransportFailure) as caught:
            transport().generate(key, "need", [], deadline=deadline, opener=opener)
        assert caught.value.reason == reason
    assert not opener.open.called


@pytest.mark.parametrize("label", ["AC-35-launch-error-AC-36-expired-before-launch"])
def test_worker_launch_failures_are_safe(monkeypatch: Any, label: str) -> None:
    def refuse(*args: Any, **kwargs: Any) -> None:
        raise OSError("synthetic-private-connection-detail")

    monkeypatch.setattr(adapter().subprocess, "Popen", refuse)
    client = adapter().GeminiClient("fake")
    with pytest.raises(TimeoutError):
        client.select_candidate("desk", candidate(), deadline=monotonic())
    with pytest.raises(ClientError) as caught:
        client.select_candidate("desk", candidate(), deadline=monotonic() + 5)
    assert "synthetic-private" not in str(caught.value)


@pytest.mark.parametrize("label", ["AC-33-request-size"])
def test_oversized_packet_never_starts_worker(monkeypatch: Any, label: str) -> None:
    spawn = Mock(side_effect=AssertionError("Must not start"))
    monkeypatch.setattr(adapter().subprocess, "Popen", spawn)
    with pytest.raises(ClientError):
        adapter().GeminiClient("fake").select_candidate("x" * 20000, candidate(),
                                                       deadline=monotonic() + 5)
    assert not spawn.called


@pytest.mark.parametrize("label", ["AC-33-duplicate-JSON-keys"])
def test_duplicate_keys_in_valid_envelope_are_rejected(label: str) -> None:
    raw = json.dumps({"candidates": [{"finishReason": "STOP", "content": {
        "parts": [{"text": '{"candidate_id":"c1","candidate_id":"c1"}'}],
    }}]}).encode()
    with pytest.raises(transport().TransportFailure):
        transport().decode_response(raw, ["c1"])


@pytest.mark.parametrize("status,reason", [(429, "quota"), (503, "provider_error")],
                         ids=["AC-35-raised-429", "AC-35-raised-503"])
def test_raised_http_errors_keep_safe_classification(status: int, reason: str) -> None:
    opener = Mock()
    body = io.BytesIO(b"synthetic-sensitive-body")
    opener.open.side_effect = HTTPError("https://example.invalid/", status,
                                        "synthetic-sensitive-message", {}, body)
    with pytest.raises(transport().TransportFailure) as caught:
        transport().generate("fake", "need", [], deadline=monotonic() + 5, opener=opener)
    assert caught.value.reason == reason
    assert "synthetic-sensitive" not in str(caught.value)
    assert body.closed
    assert opener.open.call_count == 1
