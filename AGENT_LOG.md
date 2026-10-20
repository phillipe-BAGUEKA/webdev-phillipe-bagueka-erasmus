# Agent log

One entry per agent session, newest at the bottom. Be honest: what went wrong is the useful part.

<!-- Copy this block for each session:

## YYYY-MM-DD · <short title>
- Goal:
- Delegated:
- Checkpoints:
- Went wrong:
- Changed by hand:

-->

## 2026-10-20 · Exercise 1 Python MCP server
- Goal: Build the Exercise 1 stdio server and verify its two lecture tools.
- Delegated: At my explicit request, Codex generated the complete Python server, targeted tests, startup configuration and documentation as a learning aid. I did not write this version myself.
- Checkpoints: The supplied MCP checker passed 12/12 with the direct Python command and 12/12 through npm's JavaScript entry point on Windows. Eight targeted standard-library tests passed directly and through the npm test script. A five-message transcript is recorded in `mcp-server/README.md`.
- Went wrong: The supplied checker could not spawn `npm` directly on Windows (`ENOENT`), nor `npm.cmd` (`EINVAL`). Using npm's JavaScript entry point with Node worked without changing the checker. Independent review found that the new `package.json` also needed a `test` script for the existing CI; that script was added and passed. No real agent session or description experiment was performed because Gemini CLI was unavailable.
- Changed by hand: None by the student in this session. The student still needs to study and explain each part of the generated server.
