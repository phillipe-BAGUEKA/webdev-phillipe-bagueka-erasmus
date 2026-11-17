"""Local controlled worker: no provider imports, credentials or network."""

import json
import os
import sys
import time


def main() -> None:
    mode = sys.argv[1]
    if mode != "blocked-input":
        json.load(sys.stdin)
    if mode == "excessive":
        sys.stdout.write("x" * 100000)
        sys.stdout.flush()
    elif mode == "crash":
        sys.exit(7)
    elif mode == "malformed":
        print("not JSON")
    elif mode in {"quota", "timeout", "invalid_output", "not_configured", "provider_error"}:
        print(json.dumps({"error": mode}))
    elif mode == "normal":
        print(json.dumps({"value": {"candidate_id": "c1"}}))
    else:
        if mode == "slow-cleanup":
            print(json.dumps({"value": {"candidate_id": "c1"}}), flush=True)
            os.close(sys.stdout.fileno())
        time.sleep(60)


if __name__ == "__main__":
    main()
