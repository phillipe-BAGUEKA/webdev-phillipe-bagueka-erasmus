# Lab booking · Web Development, TU Sofia

This repository contains Exercise 1 in `mcp-server/` and Lab booking in the rest of it. The first slice was developed locally on Windows with Python 3.13, Django 5.2 LTS, SQLite and plain JavaScript. The course Codespaces template remains available; its Python 3.12 environment has not been validated in this work.

The final target in [SPEC.md](SPEC.md) includes workstation reservations, staff management, Google sign-in, a model suggestion and project MCP tools. Slice 1 provides local sign-in/sign-out and a protected database-backed laboratory list. TP3 now provides PostgreSQL booking services, protected HTTP APIs and the student journey on /labs. See [student checkpoint 4](docs/STUDENT_UI_4.md) and [Slice 2 finalization](docs/SLICE2_FINALIZATION.md) for commands, automated evidence and the Edge creation/history/cancellation, keyboard, network retry and palette checks on 2026-11-12. Full accessibility and width checks remain incomplete; 380 pixels is deferred. Staff management, Google and full AI integration (provider adapter, API, UI and real calls) remain future work; the injectable AI service and the four project MCP tools are implemented, with final MCP-client validation still pending. Specification wording and code were prepared with ChatGPT/Codex assistance, recorded in AGENT_LOG.md and USAGE.md; they are not presented as wholly independent student work.

## Start

AI substep 1 adds only a read-only injectable suggestion service, tested with
fake clients on PostgreSQL. No AI endpoint, UI, provider adapter or real call is
implemented. The five-second deadline contract is not network-timeout proof.
See [AI service checkpoint](docs/AI_SERVICE_1.md) for contracts and partial AC
evidence; provider conditions for EEA users remain to be clarified.

Project MCP substeps 1–3 add an opt-in Django/PostgreSQL bootstrap, session
authentication and four tools: list_free_slots, my_bookings, book_slot and
cancel_booking. Tested through real stdio with synthetic sessions; final-client
validation and real-token handoff remain pending. Creation is not idempotent;
never automatically retry a mutation after a lost response. The default TP1
command stays independent of Django/PostgreSQL. See
[MCP mutation checkpoint](docs/MCP_MUTATIONS_3.md) for commands and limits.

Gemini CLI 0.65.0 MCP-only launch/connection has now been observed without a
provider call, using an isolated home and a fake token. Actual Gemini tool use
and personal-session handoff remain unverified. See
[MCP finalization](docs/MCP_FINALIZATION.md) for evidence and publication status.

Historical slice 1 progress: **checkpoints 1–3** are implemented. The student reported
the [foundation checks](docs/CHECKPOINT1.md) and the session/keyboard observations
for [checkpoint 2](docs/CHECKPOINT2.md). Codex has now observed all three laboratories
in the actual port-8000 browser after the module MIME/cache correction. See
[checkpoint 3](docs/CHECKPOINT3.md) for the running-server details and the observed
AC-48 demonstration: **3 → 2 → 3**, with Beta restored identically. The student
reported the API error body after logout, without an observed HTTP status.
The 380-pixel check is explicitly deferred, not passed. The booking journey also
has real Edge evidence (creation/cancellation, keyboard and network retry), kept
separate from automated HTTP status checks in [Slice 2 finalization](docs/SLICE2_FINALIZATION.md).

The [checkpoint 1](docs/CHECKPOINT1.md) guide records the original TP2 foundation.
Preserve existing SQLite data and accounts; do not run the current PostgreSQL
migration chain on SQLite or repeat demonstration password preparation. Current
booking work requires the dedicated PostgreSQL profiles/instance documented in
[POSTGRES_1A](docs/POSTGRES_1A.md), with no automatic account/data transfer.

For the preserved TP2 sessions/catalogue only, run from the root in PowerShell:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --insecure --noreload
```

Open <http://127.0.0.1:8000/login>, then <http://127.0.0.1:8000/labs>.
If the existing server already owns port 8000, use it instead of starting a second
one. Stop a terminal-owned server with Ctrl+C before restarting changed code;
CHECKPOINT3.md explains the separately launched background instance. `--insecure`
only serves local static assets with DEBUG=False; this is not a production command.

Tests and coverage use isolated settings, without the development key or demo
database; the dedicated PostgreSQL test profile is required:

```powershell
.\.venv\Scripts\python.exe manage.py check --settings=tests.settings
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=tests.settings_postgres
npm test
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
node --test tests/labs_ui.test.mjs tests/booking_ui.test.mjs tests/test_runner.test.mjs
node mcp-server/check.mjs -- .\.venv\Scripts\python.exe mcp-server/server.py
node checks/ex2.mjs
git diff --check
```

The coverage command runs Django/PostgreSQL and TP1, with unchanged service/global
gates. `npm test` also runs the historical SQLite guard on an isolated original
schema and all Node tests; it no longer runs only TP1. Provision the dedicated
test profile first using the PostgreSQL guides. For application tests alone:
`.\.venv\Scripts\python.exe -m pytest tests --ds=tests.settings_postgres --reuse-db -k 'not test_guard_refuses_unmarked_or_wrong_database' -q`.
See [TP2 finalization](docs/TP2_FINALIZATION.md) for the CI commands, measured scope,
results and publication file list. Delivery commit
[`4243d71`](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/commit/4243d717716142b45ab8304abf21c2056f28fdb7)
is published on main; its [GitHub Actions run](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/41758283141)
passed all four jobs on Ubuntu. This remote evidence is separate from the local
Windows and browser results. Each subsequent commit must have its own CI result checked.

Slice 2 delivery commit
[`2011d95`](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/commit/2011d95d6d711dd0ee84d60af7eb2135801ae9de)
passed all four [CI jobs](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/43262915943),
including empty PostgreSQL migrations, real concurrent tests and coverage gates.
Python CI lines: 94.08%; service lines/branches: 100%; loaded JavaScript modules:
98.18% lines. This does not close TP3: see the sourced gaps and personal-note
questions in [Slice 2 finalization](docs/SLICE2_FINALIZATION.md). Later commits
must be checked on their own SHA.

### Original course workspace setup

1. On the course template page, click **Use this template → Create a new repository**. Make it **public** and name it `webdev-<your faculty number>`.
2. Your repository is public, so the lecturer and your Exercise 5 review partner can read it without an invitation. That also means **no keys, passwords or client secrets ever go into it**: put them in **Settings → Secrets and variables → Codespaces** instead, where the workspace picks them up as environment variables.
3. Click **Code → Codespaces → Create codespace on main**. The first start takes a few minutes while the tools are installed.
4. When the terminal shows `Workspace ready`, type `gemini` and follow the sign-in steps on the course setup page.
5. Fill in `AGENTS.md` as you go, and add one entry to `AGENT_LOG.md` and `USAGE.md` after every agent session.

The course setup page explains accounts, sign-in, free limits and what to do if something goes wrong.

### Exercise 1 on local Windows (2026-10-20)

Gemini CLI 0.64.0 was installed with the official stable npm package, separately
from the Python MCP server. The course's "Sign in with Google" instructions no
longer work for individual accounts: Google [ended that access on 18 June
2026](https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals),
and this account received "This client is no longer supported for Gemini Code
Assist for individuals." The [Gemini CLI authentication
guide](https://geminicli.com/docs/get-started/authentication/) supports a
Gemini API key instead. Keep the project's key in the ignored `.gemini/.env`
file as `GEMINI_API_KEY=...`; never commit or paste its value. From the repository root,
start `gemini.cmd --approval-mode default`, choose "Use Gemini API key", and
select a Flash model available to the unpaid AI Studio project.
The [CLI quota guide](https://geminicli.com/docs/resources/quota-and-pricing/)
lists an unpaid API-key tier for Flash models; this does not imply that a
particular AI Studio project is unbilled. Check the project's billing status
there and do not enable billing for this exercise.

The existing `.gemini/settings.json` still loads `AGENTS.md` and starts the
Python server with `python mcp-server/server.py`. No project-wide automatic
tool approval was added. Gemini CLI 0.64.0 connects to the server after the
version-negotiation adjustment documented in `mcp-server/README.md`, which
also records the two tool-call trials and their limits.

## What is already here

| Path | What it is for |
|---|---|
| `.devcontainer/` | The workspace definition: Node 22, Python 3.12, SQLite, Docker, GitHub CLI, Gemini CLI |
| `.gemini/settings.json` | Tells Gemini CLI to read `AGENTS.md`, and where it finds your MCP servers (Exercise 1) |
| `.vscode/mcp.json` | The same for Copilot, if you use it (the key is `servers`) |
| `.github/workflows/ci.yml` | Runs your tests, the coverage gate, the MCP conformance check and the spec check on every push |
| `AGENTS.md` | Instructions your agent reads every session |
| `SPEC.md` | Your project specification (Exercise 2) |
| `AGENT_LOG.md`, `USAGE.md` | The logs you keep from Exercise 1 on |
| `mcp-server/` | Exercise 1, with `lectures.json`, `messages.jsonl` and the self-check `check.mjs` |
| `checks/` | One self-check per exercise: `node checks/ex2.mjs`, `ex3`, `ex4`, `ex5`, plus `project.mjs` before the defence |
| `docs/UI.md` | The UI checklist your project is graded against (Exercise 4) |
| `DEFENSE.md` | Your notes for the defence (Exercise 5) |
| `.env.example` | Course configuration placeholders for future integrations; slice 1 does not load a real .env |
| `course.json` | How to start your MCP server, and where your deployment answers |

## Fill in `course.json` first

Two facts about your copy that nobody can work out by reading the code:

```json
{
  "mcp": "npm run mcp",
  "liveUrl": "https://webdev-121220001.onrender.com"
}
```

`mcp` is the command that starts your MCP server, which the Exercise 1 check runs, so
add an `mcp` script to `package.json` and leave the default alone. `liveUrl` is filled
in at Exercise 4. The self-checks read both.

## Check yourself before you hand in

Each exercise ships a self-check you run from the repository root:

```bash
node mcp-server/check.mjs -- python mcp-server/server.py  # exercise 1 (Python)
node checks/ex2.mjs                                       # exercise 2
node checks/ex3.mjs                                       # exercise 3
node checks/ex4.mjs https://your-app.onrender.com         # exercise 4, URL optional
node checks/ex5.mjs                                       # exercise 5
node checks/project.mjs                                   # the night before the defence
```

They check **structure**, not quality: they catch a missing section, an unwritten acceptance criterion or a fix committed without its test. Every check must pass before you hand in: an exercise that fails one comes back to you as incomplete. Passing them all is the minimum, not the point. What the work is worth is decided by the evidence you wrote down and by the defence at the end of the course, where you explain your own code.

## Showing your work

When an exercise is done, commit and push, so your work is on GitHub and CI has run on it. Then ask the assistant to check your work in the room. They go through the exercise page's **What the assistant checks** list with you, at your codespace, and either accept the exercise or tell you exactly what is still missing.

## Save your free quota

Stop the codespace when you finish (**Code → Codespaces → … → Stop codespace**) and delete codespaces you no longer need.
