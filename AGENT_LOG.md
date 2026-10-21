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

## 2026-10-20 · Gemini CLI setup and first TP1 trial
- Goal: Connect the Python server to Gemini CLI and ask `What does lecture 5 cover?` without naming a tool.
- Delegated: At my explicit request, Codex installed Gemini CLI 0.64.0, adapted the server's MCP version negotiation and added a test. The student operated Gemini CLI and reported its output; Codex, not the student, wrote the code.
- Checkpoints: `/mcp list` showed `my-project — Ready (2 tools)`: `mcp_my-project_find_lecture` and `mcp_my-project_search_lectures`. `/stats tools` showed one successful `find_lecture` call, 21.0 s average duration, one accepted authorization, no rejected or modified authorizations. The final answer described lecture 5 and its topics. Session-level model counts are preserved in `USAGE.md`; the exact call arguments and raw result were not recorded.
- Went wrong: Individual-account Google sign-in no longer worked. The first API key appeared in a diagnostic terminal output; the student revoked and replaced it, and the replacement remains in an ignored local file. Before the compatibility change, Gemini reported the server disconnected; inspecting its installed MCP client suggested a `2025-06-18` versus `2025-11-25` version mismatch, although the wire exchange was not captured. The session displayed `API Error: exception TypeError: fetch failed sending request` and many model errors.
- Changed by hand: The student supplied and rotated the local key and ran the Gemini session. No key value is in tracked files or this log.

## 2026-10-21 · Gemini CLI description comparison
- Goal: Repeat the same question in a new session after changing only the description of `find_lecture`.
- Delegated: Codex temporarily replaced the description with `Return details for a numbered entry in the course data.` The student ran the second Gemini session and reported what was visible.
- Checkpoints: Gemini called `find_lecture(number: 5)` on `my-project` and displayed `Lecture 5: What the agent built, part 1. Topics: HTTP, REST vs GraphQL, data modeling, ORM, layers`. The chosen tool did not change between the two trials.
- Went wrong: The CLI displayed `Usage limit reached for gemini-3.8-flash` after the tool result. The student selected Stop, but no final model answer was confirmed. Complete second-session statistics were not recorded, and the student's screenshot was not supplied as a repository artifact. Two trials do not establish that descriptions have no effect.
- Changed by hand: The student ran the new session and selected Stop. Codex restored the original clear description afterwards.

## 2026-10-21 · Codex TP1 closure
- Goal: Document the evidence faithfully and prepare only the TP1 changes for publication.
- Delegated: At my explicit request, Codex updated the server, one test and the documentation. This remains generated code that the student must study and explain; no student authorship is claimed.
- Checkpoints: After restoring the clear description, the supplied checker passed 12/12 with the direct Python command and the Windows npm entry point. Nine Python tests passed directly and via `npm.cmd test`. An independent read-only reviewer found no blocking code issue; its two documentation inconsistencies were corrected.
- Went wrong: Gemini model calls were not repeated because of the usage limit. The exercise page asks students to type their own code, so the explicitly requested Codex authorship remains a pedagogical exception to discuss with the professor.
- Changed by hand: None in this Codex session. No billing, new API key or Exercise 2 work was started.
