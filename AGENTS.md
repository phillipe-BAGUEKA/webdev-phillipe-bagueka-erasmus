# Instructions for the agent

Read this file at the start of every session. Keep it short and correct; update it when the project changes.

## Project
<!-- One or two sentences: what the app does and for whom. Link SPEC.md. -->
See `SPEC.md` for goals, non-goals and acceptance criteria.

Lab booking's final goal is workstation reservations and staff catalogue management. Slice 1 implements only local sessions and a protected database-backed laboratory list. The student reported checkpoint 1/2 observations and the API error body after logout (not its HTTP status). Codex observed the real browser list and AC-48's 3 → 2 → 3 with identical Beta restoration. The responsive check was deferred during Slice 1 and resumed on 19 November. Slice 1 is published; the four GitHub Actions jobs passed on delivery commit 4243d717716142b45ab8304abf21c2056f28fdb7. Check the exact SHA of any later commit independently. TP3 proceeds only through the explicitly authorized checkpoint below. See `docs/TP2_FINALIZATION.md`, `docs/SLICE1_PLAN.md` and the CHECKPOINT guides.

## Commands

TP3 authorization now covers reservation-slice finalization and normal publication,
including PostgreSQL CI alignment. See docs/SLICE2_FINALIZATION.md and docs/STUDENT_UI_4.md.
Business decisions remain in shared services. Never automatically resend a POST
after an uncertain network result. Distinguish DOM tests from real browser proof.
The user additionally authorized one dedicated PostgreSQL development demo;
student-ui@demo.example was created without a usable password. User sets its
password locally and signed in. Codex observed the authorized Edge journey on
2026-11-12: availability, explicit creation, own history and retained cancellation.
SQLite and 5432 remain preserved. No Google, provider call or deployment. Project MCP is
approved for MCP finalization and normal publication after checks/review:
the four shared-service tools, client launch verification, docs and CI reporting.
No provider call, real-token handoff or demo mutation was performed. One-time rotation of the
exposed local PostgreSQL test-role password was authorized and verified; do not
repeat it. See docs/MCP_FINALIZATION.md. Gemini CLI 0.65.0 MCP-only connection
was observed with a synthetic token and isolated home; its actual tool calls
and real-token handoff remain unverified because no provider call is authorized.
Use synthetic test sessions only at this checkpoint.
Current AI authorization covers finalization and normal publication of the three
completed substeps, including necessary CI corrections and independent review.
Current Lab 03 authorization covers the scoped layout fix, test isolation,
traceability and normal publication after checks. Personal note and deep
personal review stay deferred. See docs/LAB03_CLOSURE.md.
Edge measurements at 380, 768 and 1280 CSS px, the synthetic login refusal
at 380 CSS px and the remaining AC-42 limits are recorded in docs/UI.md.
The current checkpoint authorizes the staff catalogue for AC-6 to AC-8,
isolated tests and a local commit. Workstation state changes are a later slice.
See docs/STAFF_CATALOGUE.md and docs/STAFF_BOOKINGS.md.
Further features, real provider calls, key access, installation, billing and Lab 04 are out of scope.
The provider stays disabled by default. See docs/AI_FINALIZATION.md and AI_UI_3.md.
Local controlled-process timing is not Google access or browser latency proof.
Local checkpoint commit authorized. The user also authorized PostgreSQL CI
alignment and normal pushes for TP3 finalization after its checks; do not publish
prematurely or equate green CI with complete TP3 acceptance. Keep the student's
architecture note personal. The latest viewport results are in docs/UI.md.
PostgreSQL commands are opt-in: --settings=src.config.postgres for development,
--ds=tests.settings_postgres --reuse-db for tests, after local provisioning.
Never run the SQLite demonstration seed against PostgreSQL.
The independent user-owned cluster uses only 127.0.0.1:5433. Lifecycle:
`.\.venv\Scripts\python.exe tools/local_postgres.py start` (or status/stop/verify).
Restart it manually after Windows reboot; no service was registered. Existing
5432 and TP2 SQLite remain separate. Never rerun init on an existing cluster.
<!-- How to install, run, test. Keep these exact and working. -->
- Install (PowerShell, local venv): `.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt`
- Django check without local secrets: `.\.venv\Scripts\python.exe manage.py check --settings=tests.settings`
- Current application tests: `.\.venv\Scripts\python.exe -m pytest --ds=tests.settings_postgres --reuse-db -k 'not test_guard_refuses_unmarked_or_wrong_database' -v`
- Run current booking UI (PostgreSQL): `.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --settings=src.config.postgres --insecure --noreload` (restart with Ctrl+C after code changes)
- Preserved TP2 SQLite catalogue only: `.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --insecure --noreload`
- Complete test command: `npm test` (local .venv preferred; PostgreSQL application/concurrency, isolated historical SQLite guard, TP1, all Node tests)
- TP1 only: `python -m unittest discover -s mcp-server -p "test_*.py" -v`
- Current coverage (PostgreSQL and TP1 subprocesses): `.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql`
- Catalogue UI logic (simulated DOM/network): `node --test tests/labs_ui.test.mjs`
- Current student UI and catalogue tests: `node --test tests/labs_ui.test.mjs tests/booking_ui.test.mjs tests/ai_suggestion_ui.test.mjs`
- Staff reservations tests: `.\.venv\Scripts\python.exe -m pytest tests/test_staff_bookings.py --ds=tests.settings_postgres --reuse-db -q` and `node --test tests/staff_bookings_ui.test.mjs`
- Staff catalogue tests: `.\.venv\Scripts\python.exe -m pytest tests/test_staff_catalogue.py --ds=tests.settings_postgres --reuse-db -q` and `node --test tests/staff_catalogue_ui.test.mjs`
- JavaScript coverage (loaded catalogue/booking modules): `node --test --experimental-test-coverage --test-coverage-include='src/**' --test-coverage-exclude='tests/**' --test-coverage-lines=80 tests/labs_ui.test.mjs tests/booking_ui.test.mjs tests/ai_suggestion_ui.test.mjs`
- MCP server: `python mcp-server/server.py` (from the repository root)
- MCP check: `node mcp-server/check.mjs -- python mcp-server/server.py`
- MCP auth/bootstrap tests: `.\.venv\Scripts\python.exe -m pytest tests/test_mcp_session_auth.py tests/test_project_mcp.py --ds=tests.settings_postgres --reuse-db --tb=short -q`
- MCP reads/security tests: `.\.venv\Scripts\python.exe -m pytest tests/test_mcp_reads.py tests/test_secret_error_safety.py --ds=tests.settings_postgres --reuse-db -q`
- MCP mutation tests: `.\.venv\Scripts\python.exe -m pytest tests/test_mcp_mutations.py --ds=tests.settings_postgres --reuse-db -q`
- AI service tests (fake clients only): `.\.venv\Scripts\python.exe -m pytest tests/test_ai_suggestion.py --ds=tests.settings_postgres --reuse-db -q`
- AI transport/API (offline only): `.\.venv\Scripts\python.exe -m pytest tests/test_gemini_adapter.py tests/test_ai_suggestion_api.py tests/test_ai_suggestion.py tests/test_ai_json_limits.py --ds=tests.settings_postgres --reuse-db -q`

The existing demo accounts are configured by the student; do not rerun password preparation. Checkpoint 3 commands and the backup/withdraw/restore procedure are in `docs/CHECKPOINT3.md`. Do not execute that procedure on the demo database during automated work. On Linux use `.venv/bin/python`. Never read the local key or any Gemini secret to report status; tests load separate non-secret settings.

## Conventions
<!-- Folder layout, naming, where business rules live, how errors are returned to the client. -->

- Target stack: Django 5.2 LTS, HTML/CSS and plain JavaScript using fetch against the REST API. SQLite is for slice 1; PostgreSQL is required from the booking slice, including its concurrency tests.
- Keep HTTP routes, business services and data access separate: `src/routes/` → `src/services/` → `src/data/`. GET `/api/labs` uses the shared authenticated-access service and returns JSON 401 without data for invalid sessions. Application ORM queries and SQL belong in data access, not in routes, services or MCP tools.
- Put business permissions in the services reused by HTTP and the future project MCP tools. Services receive an actor and domain inputs; they must not depend on an HTTP request or MCP message.
- Reuse Django password hashing, authentication and database-backed sessions. Define the email-based custom user in the first migration. HTTP/session plumbing remains in Django middleware and adapters; Django's internal authentication/session queries are framework behavior, not permission to add application queries outside data access.
- Deliver schema changes as numbered migrations; never silently rewrite a migration that has run. Seed demonstration data separately and preserve existing data.
- Tests must carry the exact relevant AC-n in their collected title (for example through pytest parameter ids). Keep meaningful assertions for success and refusal cases. Report Python coverage with its actual scope; a passing Node job is not evidence of Python coverage. Preserve the existing service/global thresholds below.

## Layers
<!-- Fill in the file or folder for each layer. -->
Requests arrive two ways and both end in the same place:

- HTTP route handler → service → data access → database
- MCP tool → **the same service** → data access → database

A route handler reads the request and turns a result into a status code. A service holds the
rules and knows nothing about HTTP or about MCP. Only the data layer writes SQL. An MCP tool
that talks to the database directly is a second, unguarded way into your data: never add one.

## The model feature
<!-- Provider, env var, and the call site. -->
- The injectable read-only suggestion service, bounded REST adapter and protected
  POST /api/labs/{id}/suggestion and optional /labs UI are implemented through
  AI substep 3. Real provider use remains untested and disabled by default.
  `src/services/ai_suggestion.py` reuses availability, validates the candidate and
  rechecks account/availability. src/integrations/gemini_http.py is the sole REST
  call site; gemini.py supervises a stdlib-only worker without Django/database.
  LAB_BOOKING_AI_ENABLED defaults off; only explicit future enablement may read
  GEMINI_API_KEY from the app environment. Never read Gemini CLI dotenv files.
  Tests disable real clients, inject fakes and use local controlled workers only.
- The key comes from an environment variable and is never committed or logged.
- Every call has a timeout and a deterministic fallback, so the app still works when the provider is down or rate-limited.
- The model's output is re-checked against real data before anything is saved or shown.
- Tests never call the provider: they pass in a fake client.

## The MCP server
<!-- Where it lives and how it authenticates. -->
- Lives in `mcp-server/`, grew out of Exercise 1.
- Default mode exposes the two TP1 course tools without Django or PostgreSQL.
- `--project` additionally exposes list_free_slots, my_bookings, book_slot and
  cancel_booking, calling the same services as HTTP. Do not retry a mutation
  automatically after transport uncertainty; inspect personal history first.
  Annotations/descriptions guide confirmations but cannot prove human consent.
  `project_runtime.current_actor()` authenticates anew from
  `LAB_BOOKING_MCP_SESSION` on every project call.
  It uses Django get_user with a read-only database SessionStore: no session
  creation/renewal/flush, no cached actor, no privileged Django account.
- Every future project tool must call a shared service function; none may touch the data layer or database directly.
- Project tools must carry a user and enforce exactly the same authorization rules as the HTTP API.
- Adding a tool means adding a row to the table in `SPEC.md` too.

## Tests and coverage
- Every implemented acceptance criterion must have a test whose title contains its exact AC-n; final-project criteria outside slice 1 remain future work.
- The CI gate uses `tools/check_coverage.py`: 100% of Python service lines and branches, at least 80% of global Python lines, including TP1. Keep `.coveragerc` and its production inventory; remote results must be checked for the published SHA, not inferred from local success. JavaScript coverage is separate and not proof of whole-frontend or visual coverage.
- A test is evidence. Changing a test so the code passes destroys the evidence.

## Always ask before
- deleting files or folders
- editing a migration that has already run
- installing or removing dependencies
- pushing, tagging or changing CI
- anything that touches secrets or `.env`
- changing an authentication or authorization rule
- adding, renaming or removing an MCP tool
- changing a coverage threshold
- sending user data to a third-party model

## Never
- commit secrets, passwords, API keys or an OAuth client secret
- weaken or delete a test to make it pass
- lower a coverage threshold or switch off a CI job to make the build green
- add an MCP tool that reaches past the service layer
- log a prompt that contains somebody's personal data
