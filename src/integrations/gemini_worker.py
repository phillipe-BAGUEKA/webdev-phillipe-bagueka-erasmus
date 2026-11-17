"""Private stdin/stdout worker; no Django, database, dotenv or diagnostic output."""

import json
import sys

from .gemini_http import TransportFailure, generate, strict_json

MAX_INPUT_BYTES = 16384


def main() -> None:
    """Emit only a bounded selection or safe fixed failure code to the parent."""
    try:
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise TransportFailure("invalid_output")
        packet = strict_json(raw)
        value = generate(packet["api_key"], packet["need"], packet["candidates"],
                         deadline=packet["deadline"])
        reply = {"value": value}
    except TransportFailure as error:
        reply = {"error": error.reason}
    except Exception:
        reply = {"error": "provider_error"}
    sys.stdout.write(json.dumps(reply))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
