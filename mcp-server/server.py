"""Serve the course's two lecture tools over line-delimited MCP stdio."""

import json
import math
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, NoReturn


PROTOCOL_VERSION = "2025-11-25"
COMPATIBLE_PROTOCOL_VERSIONS = {PROTOCOL_VERSION, "2025-06-18"}
TOOLS = [
    {
        "name": "find_lecture",
        "description": (
            "Find one course lecture by its number. Use for questions about a "
            "specific lecture; return its title and topics."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"number": {"type": "integer"}},
            "required": ["number"],
        },
    },
    {
        "name": "search_lectures",
        "description": (
            "Search lecture titles and topics by text. Use when the lecture "
            "number is unknown; return matching numbers, titles and topics."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string", "minLength": 1}},
            "required": ["query"],
        },
    },
]


def load_lectures() -> list[dict[str, Any]]:
    """Read and check the local data once, before accepting requests."""
    data_path = Path(__file__).with_name("lectures.json")
    with data_path.open(encoding="utf-8") as data_file:
        lectures = json.load(data_file)

    if not isinstance(lectures, list):
        raise ValueError("lectures.json must contain a list")

    for lecture in lectures:
        if not isinstance(lecture, dict):
            raise ValueError("each lecture must be an object")
        if type(lecture.get("number")) is not int:
            raise ValueError("each lecture needs an integer number")
        if not isinstance(lecture.get("title"), str):
            raise ValueError("each lecture needs a title")
        if not isinstance(lecture.get("topics"), str):
            raise ValueError("each lecture needs topics")

    return lectures


def result_response(request_id: object, result: dict[str, Any]) -> dict[str, Any]:
    """Wrap an operation's result in a JSON-RPC response."""
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(request_id: object, code: int, message: str) -> dict[str, Any]:
    """Report an invalid protocol message or call without stopping the server."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def tool_result(message: str, is_error: bool) -> dict[str, Any]:
    """Give the model readable feedback from an executed tool."""
    return {
        "content": [{"type": "text", "text": message}],
        "isError": is_error,
    }


def describe_lecture(lecture: dict[str, Any]) -> str:
    """Keep both tools' lecture formatting consistent."""
    return (
        f"Lecture {lecture['number']}: {lecture['title']}. "
        f"Topics: {lecture['topics']}"
    )


def call_tool(
    request_id: object,
    parameters: dict[str, Any],
    lectures: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate a tool call, then search only the bundled lecture data."""
    name = parameters.get("name")
    if not isinstance(name, str) or name not in {
        "find_lecture",
        "search_lectures",
    }:
        return error_response(request_id, -32602, f"Unknown tool: {name}")

    arguments = parameters.get("arguments", {})
    if not isinstance(arguments, dict):
        return error_response(request_id, -32602, "Tool arguments must be an object")

    if name == "find_lecture":
        number = arguments.get("number")
        # bool is a subclass of int in Python, but it is not a JSON integer.
        if type(number) is not int:
            return error_response(request_id, -32602, "number must be an integer")

        lecture = next(
            (item for item in lectures if item["number"] == number),
            None,
        )
        if lecture is None:
            return result_response(
                request_id,
                tool_result(f"There is no lecture {number}.", True),
            )
        return result_response(
            request_id,
            tool_result(describe_lecture(lecture), False),
        )

    query = arguments.get("query")
    if not isinstance(query, str) or not query.strip():
        return error_response(request_id, -32602, "query must be a non-empty string")

    query = query.strip()
    matches = [
        lecture
        for lecture in lectures
        if query.casefold() in lecture["title"].casefold()
        or query.casefold() in lecture["topics"].casefold()
    ]
    if not matches:
        return result_response(
            request_id,
            tool_result(f"No lectures match {query!r}.", False),
        )

    text = "\n".join(describe_lecture(lecture) for lecture in matches)
    return result_response(request_id, tool_result(text, False))


def handle_message(
    message: object,
    lectures: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Route one parsed JSON-RPC request, leaving notifications unanswered."""
    if not isinstance(message, dict):
        return error_response(None, -32600, "Invalid Request")

    request_id = message.get("id")
    if "id" in message and (
        isinstance(request_id, bool)
        or not isinstance(request_id, (str, int, float, type(None)))
        or (isinstance(request_id, float) and not math.isfinite(request_id))
    ):
        return error_response(None, -32600, "Invalid Request")

    if message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
        return error_response(None, -32600, "Invalid Request")

    # A notification has no id, including when its method is not recognized.
    if "id" not in message:
        return None

    method = message["method"]
    parameters = message.get("params", {})
    if not isinstance(parameters, dict):
        return error_response(request_id, -32602, "params must be an object")

    if method == "initialize":
        requested_version = parameters.get("protocolVersion")
        if not isinstance(requested_version, str):
            return error_response(request_id, -32602, "protocolVersion is required")

        # Gemini CLI 0.64.0 offers 2025-06-18; the course checker uses 2025-11-25.
        agreed_version = (
            requested_version
            if requested_version in COMPATIBLE_PROTOCOL_VERSIONS
            else PROTOCOL_VERSION
        )
        return result_response(
            request_id,
            {
                "protocolVersion": agreed_version,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "lecture-tools", "version": "1.0.0"},
            },
        )

    if method == "tools/list":
        return result_response(request_id, {"tools": TOOLS})

    if method == "tools/call":
        return call_tool(request_id, parameters, lectures)

    return error_response(request_id, -32601, f"Unknown method: {method}")


def reject_invalid_constant(value: str) -> NoReturn:
    """Reject NaN and Infinity, which Python otherwise accepts as JSON."""
    raise ValueError(f"Invalid JSON number: {value}")


def main() -> int:
    """Keep one JSON object per line on stdout until stdin closes."""
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if sys.argv[1:] not in ([], ["--project"]):
        print("Usage: server.py [--project]", file=sys.stderr)
        return 2
    if sys.argv[1:] == ["--project"]:
        try:
            from project_runtime import initialize_project

            with redirect_stdout(sys.stderr):
                initialize_project()
        except Exception:
            # Configuration/database exceptions can contain connection secrets.
            print("Project initialization failed; check local configuration.", file=sys.stderr)
            return 1

    try:
        lectures = load_lectures()
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Cannot load lecture data: {error}", file=sys.stderr)
        return 1

    try:
        for line in sys.stdin:
            try:
                message = json.loads(line, parse_constant=reject_invalid_constant)
            except (json.JSONDecodeError, ValueError):
                response = error_response(None, -32700, "Parse error")
            else:
                response = handle_message(message, lectures)

            if response is not None:
                print(json.dumps(response, ensure_ascii=False), flush=True)
    except KeyboardInterrupt:
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
