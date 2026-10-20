# Exercise 1 · MCP server

The MCP server lives in this folder. The course normally asks the student to write it by hand. This Python version was generated with Codex at the student's explicit request as a learning aid; the code and its decisions still need to be studied before the defence. The full task is on the exercise page.

## What is already here

| File | What it is |
|---|---|
| `lectures.json` | The course lectures. Your first tool reads this file. |
| `messages.jsonl` | The messages a client sends, in order, with what your server must answer. |
| `check.mjs` | The self-check. It starts your server, sends those messages and tells you what is wrong. |

## The two tools

1. **`find_lecture`**: everyone writes this one. Input: `number` (1 to 10). It returns the title and topics of that lecture from `lectures.json`. A number outside the range is not a crash and not a protocol error: it is a result with `isError: true` and a readable message.
2. **`search_lectures`**: searches titles and topics using a non-empty text query, ignoring case. It returns the matching numbers, titles and topics, or a successful no-match message.

## Where this goes next

Do not throw this folder away after Exercise 1. From Exercise 3 it becomes **your project's own MCP server**: the same protocol loop, with the tools rewired from `lectures.json` to your real data. Its tools call exactly the same service functions your HTTP routes call, so a tool obeys the same rules an API request does, and it carries a user (the `MCP_TOKEN` in `.env.example`) so it may do what that person may do and no more.

That is the whole design, and it is one sentence: **one set of rules, two front doors.** An MCP tool that writes its own database query is a second way into your data with none of your rules on it, and Exercise 5 is very good at finding those.

The `mcp` script in `package.json` starts `python mcp-server/server.py` so an agent, CI and the lecturer can use the same entry point.

## Run the self-check

```bash
node mcp-server/check.mjs -- <your start command>
# for example
node mcp-server/check.mjs -- python mcp-server/server.py
# Linux/Codespaces, through the npm script
node mcp-server/check.mjs -- npm run --silent mcp
```

It prints one line per check. This generated version is for learning: review the handler and its failure cases before relying on it.

## How to start it

From the repository root, run `python mcp-server/server.py` or `npm run --silent mcp` on Windows and Linux/Codespaces. `python` is Python 3.13.7 on the inspected Windows machine; `py -3.12 mcp-server/server.py` selects its installed Python 3.12.6 explicitly. Codespaces supplies Python 3.12. No external Python packages are needed.

On this Windows machine, the direct check `node mcp-server/check.mjs -- npm run --silent mcp` fails with `spawn npm ENOENT`: Node's `spawn` does not resolve the Windows npm wrapper as the checker expects. `npm.cmd` fails with `spawn EINVAL`. The checked Windows equivalent, without changing `check.mjs`, is:

```powershell
node mcp-server/check.mjs -- node 'C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js' run --silent mcp
```

Both the direct Python check and this Windows npm check reported `12/12 checks passed` on 2026-10-20. The additional standard-library tests reported `Ran 8 tests ... OK`. They also run through `npm test`, which the existing CI invokes when `package.json` is present:

```powershell
python -m unittest discover -s mcp-server -p 'test_*.py' -v
npm.cmd test
```

For a one-line manual PowerShell check, use `'{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp-server/server.py 2>$null`. PowerShell's `2>$null` replaces the Bash example's `2>/dev/null`; it hides diagnostics only for this manual check. The server itself reserves stdout for protocol messages and stderr for diagnostics.

## Session transcript

The following five lines were sent to one Python process on 2026-10-20, in this order. The second line is a notification and has no reply:

```jsonl
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"manual-check","version":"1.0.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"find_lecture","arguments":{"number":5}}}
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"find_lecture","arguments":{"number":99}}}
```

Actual stdout (four lines, matching ids 1 to 4; no line for the notification):

```jsonl
{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-11-25", "capabilities": {"tools": {}}, "serverInfo": {"name": "lecture-tools", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "find_lecture", "description": "Find one course lecture by its number. Use for questions about a specific lecture; return its title and topics.", "inputSchema": {"type": "object", "properties": {"number": {"type": "integer"}}, "required": ["number"]}}, {"name": "search_lectures", "description": "Search lecture titles and topics by text. Use when the lecture number is unknown; return matching numbers, titles and topics.", "inputSchema": {"type": "object", "properties": {"query": {"type": "string", "minLength": 1}}, "required": ["query"]}}]}}
{"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "Lecture 5: What the agent built, part 1. Topics: HTTP, REST vs GraphQL, data modeling, ORM, layers"}], "isError": false}}
{"jsonrpc": "2.0", "id": 4, "result": {"content": [{"type": "text", "text": "There is no lecture 99."}], "isError": true}}
```

The course page mentions lectures 1–12, while this repository's `lectures.json` contains 1–10. The server uses the file as supplied; it does not invent lectures 11 and 12.

Invalid or missing tool arguments produce JSON-RPC `-32602`, following Lecture 2's convention that arguments failing the schema are protocol errors. The [MCP 2025-11-25 tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools#error-handling) describes some input validation failures as tool execution results with `isError: true`. This course-oriented server therefore does not claim exhaustive MCP conformance. It implements only the four methods needed here, with no pagination, resources or prompts.

## The description experiment

Protocol for the later agent session: ask the same question that could use `search_lectures` twice, without naming the tool. Between trials, change only that tool's description, making its use case more or less precise; record whether the agent chose it and explain the observed difference. No model trial was performed here because Gemini CLI was not available, so no behavioural change is claimed.
