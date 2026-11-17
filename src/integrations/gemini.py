"""Bound a private provider process, including I/O and cleanup, by one deadline."""

from collections.abc import Mapping, Sequence
import json
import os
from pathlib import Path
from queue import Empty, Queue
import subprocess
import sys
from threading import Thread
from time import monotonic
from typing import BinaryIO

from src.services.ai_suggestion import (
    Candidate, ClientError, ClientInvalidOutput, ClientQuotaExceeded, ClientUnavailable,
)
from .gemini_http import strict_json

ROOT = Path(__file__).resolve().parents[2]
MAX_PACKET_BYTES = 16384
MAX_REPLY_BYTES = 65536
CLEANUP_SECONDS = 0.5


def _exchange(
    incoming: BinaryIO, outgoing: BinaryIO, packet: bytes, result: Queue,
) -> None:
    try:
        remaining = memoryview(packet)
        while remaining:
            written = incoming.write(remaining)
            remaining = remaining[written:]
        incoming.close()
        output = bytearray()
        while len(output) <= MAX_REPLY_BYTES:
            chunk = outgoing.read(min(4096, MAX_REPLY_BYTES + 1 - len(output)))
            if not chunk:
                break
            output.extend(chunk)
        result.put(bytes(output))
    except (OSError, ValueError):
        result.put(None)


def _remaining(deadline: float) -> float:
    return max(0.0, deadline - monotonic())


def _cleanup(process: subprocess.Popen, thread: Thread, deadline: float) -> None:
    try:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=_remaining(deadline))
        if thread.ident is not None:
            thread.join(timeout=_remaining(deadline))
        if thread.is_alive():
            raise ClientError("Worker cleanup failed.")
    except (subprocess.TimeoutExpired, OSError):
        raise ClientError("Worker cleanup failed.") from None
    finally:
        process.stdin.close()
        process.stdout.close()


def _worker_value(raw: bytes) -> object:
    try:
        reply = strict_json(raw)
        if type(reply) is not dict:
            raise ValueError
        if set(reply) == {"value"}:
            return reply["value"]
        if set(reply) != {"error"} or type(reply["error"]) is not str:
            raise ValueError
        reason = reply["error"]
    except (ValueError, TypeError, KeyError):
        raise ClientInvalidOutput("Provider reply invalid.") from None
    if reason == "quota":
        raise ClientQuotaExceeded("Provider quota reached.")
    if reason == "timeout":
        raise TimeoutError("Provider deadline expired.")
    if reason == "invalid_output":
        raise ClientInvalidOutput("Provider reply invalid.")
    if reason == "not_configured":
        raise ClientUnavailable("Provider not configured.")
    raise ClientError("Provider unavailable.")


class GeminiClient:
    """One child and one REST attempt; the key is never part of repr/argv/env."""

    def __init__(self, api_key: str, *, worker_command: Sequence[str] | None = None) -> None:
        self._api_key = api_key
        self._command = tuple(worker_command or (
            sys.executable, "-m", "src.integrations.gemini_worker",
        ))

    def select_candidate(
        self, need: str, candidates: tuple[Candidate, ...], *, deadline: float,
    ) -> object:
        """Return a decoded pick only after the child is confirmed reaped."""
        deadline = min(deadline, monotonic() + 5.0)
        work_deadline = deadline - CLEANUP_SECONDS
        if _remaining(work_deadline) == 0:
            raise TimeoutError("Provider deadline expired.")
        packet = json.dumps({
            "api_key": self._api_key, "need": need, "deadline": work_deadline,
            "candidates": [{
                "candidate_id": item.candidate_id, "workstation_name": item.workstation_name,
                "starts_at": item.starts_at.isoformat(), "ends_at": item.ends_at.isoformat(),
            } for item in candidates],
        }, ensure_ascii=False).encode("utf-8")
        if len(packet) > MAX_PACKET_BYTES:
            raise ClientInvalidOutput("Provider request is too large.")
        environment = {name: os.environ[name] for name in (
            "SystemRoot", "WINDIR", "TEMP", "TMP", "COVERAGE_PROCESS_START",
            "COVERAGE_RCFILE", "COVERAGE_FILE",
        ) if name in os.environ}
        try:
            process = subprocess.Popen(
                self._command, cwd=ROOT, env=environment, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        except OSError:
            raise ClientError("Provider worker unavailable.") from None
        result: Queue = Queue(maxsize=1)
        thread = Thread(target=_exchange, args=(process.stdin, process.stdout, packet, result))
        try:
            thread.start()
            raw = result.get(timeout=_remaining(work_deadline))
            if raw is None or len(raw) > MAX_REPLY_BYTES:
                raise ClientInvalidOutput("Provider reply invalid.")
            process.wait(timeout=_remaining(work_deadline))
            if process.returncode != 0:
                raise ClientError("Provider worker failed.")
            value = _worker_value(raw)
            if _remaining(work_deadline) == 0:
                raise TimeoutError("Provider deadline expired.")
            return value
        except (Empty, subprocess.TimeoutExpired):
            raise TimeoutError("Provider deadline expired.") from None
        except TimeoutError:
            raise
        except (OSError, RuntimeError):
            raise ClientError("Provider worker failed.") from None
        finally:
            _cleanup(process, thread, deadline)


def configured_client(environment: Mapping[str, str] | None = None) -> GeminiClient | None:
    """Fail closed unless explicitly enabled; never search CLI/secret files."""
    environment = os.environ if environment is None else environment
    if environment.get("LAB_BOOKING_AI_ENABLED") != "1":
        return None
    api_key = environment.get("GEMINI_API_KEY", "").strip()
    return GeminiClient(api_key) if api_key else None
