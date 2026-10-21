"""Targeted stdio checks beyond the course's Exercise 1 self-check."""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any


SERVER = Path(__file__).with_name("server.py")


def request(request_id: int, method: str, params: dict[str, Any]) -> str:
    """Build one request line while keeping the test cases easy to read."""
    return json.dumps(
        {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
    )


class ServerStdioTests(unittest.TestCase):
    """Exercise the server as a client would, through its standard streams."""

    def exchange(self, *lines: str) -> list[dict[str, Any]]:
        """Send several lines to one process and parse every stdout reply."""
        process = subprocess.run(
            [sys.executable, str(SERVER)],
            input="\n".join(lines) + "\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            check=True,
        )
        self.assertEqual(process.stderr, "")
        return [json.loads(line) for line in process.stdout.splitlines()]

    def test_initialize_notification_and_tool_catalog(self) -> None:
        replies = self.exchange(
            request(0, "initialize", {"protocolVersion": "unknown-version"}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            request(2, "tools/list", {}),
        )

        self.assertEqual([reply["id"] for reply in replies], [0, 2])
        self.assertEqual(replies[0]["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(replies[0]["result"]["capabilities"], {"tools": {}})
        tools = replies[1]["result"]["tools"]
        self.assertEqual(
            [tool["name"] for tool in tools],
            ["find_lecture", "search_lectures"],
        )
        self.assertTrue(all(len(tool["description"]) >= 20 for tool in tools))
        self.assertEqual(tools[0]["inputSchema"]["required"], ["number"])
        self.assertEqual(tools[1]["inputSchema"]["required"], ["query"])

    def test_initialize_accepts_gemini_cli_protocol_version(self) -> None:
        replies = self.exchange(
            request(1, "initialize", {"protocolVersion": "2025-06-18"}),
        )

        self.assertEqual(replies[0]["result"]["protocolVersion"], "2025-06-18")

    def test_find_lecture_success_and_missing_number(self) -> None:
        replies = self.exchange(
            request(
                1,
                "tools/call",
                {"name": "find_lecture", "arguments": {"number": 5}},
            ),
            request(
                2,
                "tools/call",
                {"name": "find_lecture", "arguments": {"number": 99}},
            ),
        )

        self.assertFalse(replies[0]["result"]["isError"])
        self.assertIn(
            "What the agent built, part 1",
            replies[0]["result"]["content"][0]["text"],
        )
        self.assertTrue(replies[1]["result"]["isError"])
        self.assertIn("99", replies[1]["result"]["content"][0]["text"])

    def test_search_matches_and_no_match(self) -> None:
        replies = self.exchange(
            request(
                1,
                "tools/call",
                {"name": "search_lectures", "arguments": {"query": "  aGeNt  "}},
            ),
            request(
                2,
                "tools/call",
                {"name": "search_lectures", "arguments": {"query": "unfindable"}},
            ),
        )

        match = replies[0]["result"]
        self.assertFalse(match["isError"])
        self.assertIn("Lecture 1:", match["content"][0]["text"])
        self.assertIn("Topics:", match["content"][0]["text"])
        no_match = replies[1]["result"]
        self.assertFalse(no_match["isError"])
        self.assertIn("No lectures match", no_match["content"][0]["text"])

    def test_missing_and_wrong_argument_types(self) -> None:
        invalid_calls = [
            {"name": "find_lecture", "arguments": {}},
            {"name": "find_lecture", "arguments": {"number": "5"}},
            {"name": "find_lecture", "arguments": {"number": True}},
            {"name": "search_lectures", "arguments": {}},
            {"name": "search_lectures", "arguments": {"query": "   "}},
            {"name": "search_lectures", "arguments": {"query": 5}},
        ]
        replies = self.exchange(
            *(
                request(index, "tools/call", call)
                for index, call in enumerate(invalid_calls)
            )
        )

        self.assertEqual([reply["error"]["code"] for reply in replies], [-32602] * 6)

    def test_parse_error_invalid_request_and_recovery(self) -> None:
        replies = self.exchange(
            "{broken json",
            "NaN",
            "[]",
            request(0, "tools/list", {}),
        )

        self.assertEqual([reply["id"] for reply in replies], [None, None, None, 0])
        self.assertEqual(replies[0]["error"]["code"], -32700)
        self.assertEqual(replies[1]["error"]["code"], -32700)
        self.assertEqual(replies[2]["error"]["code"], -32600)
        self.assertIn("tools", replies[3]["result"])

    def test_malformed_tool_name_does_not_stop_the_server(self) -> None:
        replies = self.exchange(
            request(1, "tools/call", {"name": [], "arguments": {}}),
            request(2, "tools/list", {}),
        )

        self.assertEqual(replies[0]["error"]["code"], -32602)
        self.assertIn("tools", replies[1]["result"])

    def test_unknown_method_and_unknown_tool(self) -> None:
        replies = self.exchange(
            request(1, "not/a/method", {}),
            request(2, "tools/call", {"name": "missing_tool", "arguments": {}}),
        )

        self.assertEqual(
            [reply["error"]["code"] for reply in replies],
            [-32601, -32602],
        )

    def test_utf8_remains_valid_json_on_stdout(self) -> None:
        replies = self.exchange(
            request(
                1,
                "tools/call",
                {"name": "search_lectures", "arguments": {"query": "Éclipse"}},
            )
        )

        self.assertIn("Éclipse", replies[0]["result"]["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
