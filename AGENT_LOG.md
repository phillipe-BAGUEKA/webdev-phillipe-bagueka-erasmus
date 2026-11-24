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

## 2026-11-03 · Exercise 2 topic and specification preparation
- Goal: Resume from the published TP1 work and prepare the student-written specification before approving any implementation plan.
- Delegated: Codex inspected the applicable instructions, local Git state, specification template, configuration and Exercise 2 checker. The student explicitly chose the official Lab booking topic: users, laboratories, workstations and bookings; students consult availability, book and cancel their own bookings, while staff manage laboratories and workstations. The proposed first slice is local sign-in, sign-out and a protected laboratories list backed by a real database.
- Checkpoints: The initial working tree was clean on main at c2300cfaf273b2cdf4d84476980e99aff4039a85. Python reports 3.13.7 locally; the Codespaces configuration targets Python 3.12. The Exercise 2 structural check passed 13/30 checks initially, 15/30 after naming the project and option, and 18/30 after recording the student's technical choices; the specification and application remain incomplete. Course pages were retrieved with curl after Web access and the sandbox proxy failed. Codex transcribed the confirmed project name, option and slice heading into SPEC.md, without writing the student's goals or criteria. The diff was reviewed and git diff --check passed. TP1 tests were not rerun because only documentation changed; no independent reviewer was triggered for this documentation-only preparation.
- Went wrong: The structural checker accepts the existing MCP commands as filled commands even though application install/run commands are still absent. Its uniqueness helper also deduplicates acceptance ids before comparing them, so a passing duplicate-id check is not sufficient evidence. The existing Node coverage job does not measure Python coverage. These checks were not weakened or changed. The site's general project guide lists only SPEC.md and AGENTS.md, but Exercise 2 also requires AGENT_LOG.md and USAGE.md, which are retained.
- Changed by hand: The student supplied the topic and intended slice, then accepted Django 5.2 LTS with HTML/CSS/plain JavaScript and fetch. The student clarified that SQLite is for slice 1 and PostgreSQL must be introduced for the booking slice, to test constraints and simultaneous bookings on the target database. The student also required an email-based user model from the first migrations, Django's password/session mechanisms and business permissions in shared HTTP/MCP services. Codex transcribed these decisions into Constraints, Auth and UI; this technical approval does not approve construction. Next: the student drafts Non-goals, then Goals and acceptance criteria; Codex critiques the draft and prepares a plan for approval after the specification is complete. My course registration and student understanding have not been verified. No application code, dependencies, provider calls, secrets, commit or push were changed in this session.

## 2026-11-03 · Exercise 2 non-goals
- Goal: Check and record the student's three selected exclusions before discussing Goals.
- Delegated: The student explicitly reported preparing these formulations with ChatGPT's help. Codex reviewed them against the Exercise 2 and final-project requirements already retrieved in this conversation, then copied the supplied French wording into Non-goals only. These are assisted formulations selected by the student, not a claim of entirely independent student writing.
- Checkpoints: All three exclusions name concrete features. Payments are not required by the course; excluding native mobile apps preserves the required mobile-friendly website; excluding booking notifications preserves both on-site booking information and authentication mechanisms. The subject, stack and all other specification sections were preserved. SPEC.md, AGENT_LOG.md and USAGE.md already had local changes at the start of this step; only SPEC.md and AGENT_LOG.md were edited in this step.
- Verification: node checks/ex2.mjs returned exit code 1 with 19/30 checks passed, including Non-goals. The 11 remaining failures concern unfinished Goals, acceptance criteria and their ids, Spec vs result, the model feature and failure plan, MCP tools and descriptions, the social provider and account linking, and AGENTS.md conventions. git diff --check passed; the diff was reviewed. No application tests were rerun for this documentation-only change.
- Went wrong: No incompatibility was identified in the supplied exclusions. The full Exercise 2 check remains incomplete for the expected reasons above; passing the Non-goals structure check is not proof of professor acceptance.
- Changed by hand: The student selected and supplied the three exclusions with disclosed ChatGPT assistance. Goals still require the student's answers about the student workflow and staff management. No application code, installation, model API call, commit or push was performed. No independent reviewer was triggered for this documentation-only change.

## 2026-11-03 · Exercise 2 goals and workstation availability rules
- Goal: Review and record the student's final-project goals before clarifying acceptance criteria.
- Delegated: The student supplied two goals prepared with ChatGPT's help and explicitly disclosed that assistance. Codex checked them against the course requirements already retrieved, the selected non-goals and the recorded technical decisions, then transcribed them into Goals. The workstation availability details were recorded under Constraints / Business rules as expected behavior, not an implementation or test result.
- Checkpoints: No contradiction was identified. The student workflow matches Lab booking, ownership restrictions remain in shared services, and staff management includes an in-service/out-of-service state without a maintenance calendar. Existing bookings remain visible with the workstation's unavailability indicated; no booking is automatically cancelled or moved, and no automatic notification is introduced. The first slice still contains only local sign-in, sign-out and a database-backed protected laboratories list. SPEC.md, AGENT_LOG.md and USAGE.md were already modified when this step started; only SPEC.md and AGENT_LOG.md were edited here.
- Went wrong: The goals do not yet settle precise time-slot boundaries, permitted booking times, cancellation boundaries or all testable outcomes. Acceptance criteria and the other incomplete specification sections remain to be written with the student.
- Verification: node checks/ex2.mjs returned exit code 1 with 20/30 checks passed, including Goals. The 10 expected remaining failures concern acceptance criteria and their ids, Spec vs result, the model feature and failure plan, MCP tools and descriptions, the social provider and account linking, and AGENTS.md conventions. git diff --check passed and the diff was reviewed. No application tests were run because this step changed documentation only.
- Changed by hand: The student selected and supplied the assisted goals and workstation rules. No claim of wholly independent wording or validated understanding is made. No application code, installation, model API call, commit or push was performed. No independent reviewer was triggered for this documentation-only change.

## 2026-11-03 · Exercise 2 time-slot rules
- Goal: Record the student's temporal decisions as expected final-project behavior before discussing cancellation and per-student limits.
- Delegated: The student supplied the selected rules and asked to retain the disclosure of ChatGPT assistance. Codex checked consistency with the existing specification and recorded the rules under Constraints / Business rules / Time slots, without claiming independent student wording, implementation or functional verification.
- Checkpoints: No contradiction was identified. Reservations use predefined one-hour slots on whole hours, Monday to Friday from 08:00 to 18:00 in Europe/Sofia. These are project conventions, not official university hours; holiday calendars and laboratory-specific hours are outside the selected scope. UTC is the reference for storage and exchanges, with timezone-aware conversion for display rather than a fixed offset. The server must reject slots whose start is not strictly in the future. Half-open intervals allow adjacent bookings on the same workstation without a preparation gap. Existing workstation availability and ownership rules remain applicable. The first slice is unchanged.
- Went wrong: Cancellation boundaries, per-student limits and the remaining specification sections are still undecided or incomplete. No implementation outcome is inferred from these documentation changes.
- Verification: node checks/ex2.mjs returned exit code 1 with 20/30 checks passed. The 10 expected failures still concern acceptance criteria and their ids, Spec vs result, the model feature and failure plan, MCP tools and descriptions, the social provider and account linking, and AGENTS.md conventions. git diff --check passed and the diff was reviewed. These are documentary checks; the temporal rules have not been functionally tested.
- Changed by hand: The student chose the temporal rules in the conversation. SPEC.md, AGENT_LOG.md and USAGE.md already had local changes; only SPEC.md and AGENT_LOG.md were edited in this step. No application code, installation, API call, commit or push was performed. No independent reviewer was triggered for this documentation-only change.

## 2026-11-03 · Exercise 2 cancellation, quotas and remaining decisions
- Goal: Record the student's cancellation and booking-limit decisions, then present recommendations for the still-open specification choices.
- Delegated: The student supplied the rules and requested continued disclosure of ChatGPT assistance. Codex checked their consistency, recorded them as expected behavior in SPEC.md and clarified the student goal so cancelled bookings do not block a workstation. The assisted wording is not presented as entirely independent student writing.
- Checkpoints: Cancellation is restricted to the owner before the slot starts, including when the workstation is out of service. Cancelled bookings remain in history but release the slot and quota. Only non-cancelled bookings with a strictly future start count toward the three-booking limit; future bookings on out-of-service workstations still count. Overlapping non-cancelled bookings by one student are forbidden across all workstations and laboratories; adjacent slots remain possible. Shared-service enforcement and concurrent-creation verification on PostgreSQL are requirements for the booking slice, not completed features or tests. The first slice is unchanged.
- Went wrong: External sign-in, account linking, the model feature, project MCP tools, complete screens and acceptance criteria still need student decisions. Recommendations for these topics were prepared for discussion only and were not recorded as accepted choices in SPEC.md. Public Google OpenID Connect and Gemini model/pricing documentation was read to inform those recommendations; no authentication exchange, model inference or billing operation was performed.
- Verification: node checks/ex2.mjs returned exit code 1 with 20/30 checks passed. The 10 expected remaining failures concern acceptance criteria and their ids, Spec vs result, the model feature and failure plan, MCP tools and descriptions, the social provider and account linking, and AGENTS.md conventions. git diff --check passed and the diff was reviewed. No functional or concurrency test was run; the recorded rules are requirements only.
- Changed by hand: The student selected the cancellation and quota rules in the conversation. SPEC.md, AGENT_LOG.md and USAGE.md were already modified; only SPEC.md and AGENT_LOG.md were edited in this step. No application code, installation, model API call, commit or push was performed. No independent reviewer was triggered for this documentation-only change.

## 2026-11-03 · Exercise 2 external sign-in, model, MCP and UI decisions
- Goal: Record the student's accepted recommendations and refinements, then prepare a grouped checklist to support student-written acceptance criteria.
- Delegated: The student accepted the nine recommendations developed with ChatGPT/Codex assistance and supplied additional requirements. Codex transcribed those decisions into The model feature, Auth, MCP tools and UI; no claim of wholly independent student writing is made.
- Checkpoints: Google OIDC uses server-side processing and the ordinary Django session. Initial linking requires local reauthentication, explicit confirmation, matching email and a verified Google email; subsequent Google sign-in uses the stored stable identity. Unlinked Google accounts create no user; accounts and roles remain administratively provisioned. The text model choice is gemini-3.5-flash-lite, with official sources and their 2026-11-03 consultation date recorded, announced free-tier availability distinguished from project access that has not been tested. The specification covers a bounded candidate list, no model call when it is empty, output validation, confirmation before booking, rule rechecks, possible personal data in free text, a five-second deadline without any automatic client retry, and fake-client tests. Four future project MCP tools supplement the two TP1 tools through shared services. The screen list distinguishes the authenticated account area, personal bookings and the staff area. All are expected behavior, not completed features; slice 1 remains unchanged.
- Went wrong: Acceptance criteria remain student work and have not been written or tested. Spec vs result remains empty because the slice has not been built. No model access or free quota for this project is claimed from reading public documentation.
- Verification: node checks/ex2.mjs returned exit code 1 with 28/32 checks passed. The four expected failures concern acceptance criteria, their ids, Spec vs result and AGENTS.md conventions. The two additional checks verify that the existing .env.example names Google client configuration and a model key; no real secret file was accessed or modified. git diff --check passed and the diff was reviewed. No functional test was run for this documentation-only step. The numerical bound on the model's candidate list still needs to be stated when drafting a criterion for that limit; the other recorded choices are sufficient to begin the grouped acceptance-criteria draft.
- Changed by hand: The student selected and refined the assisted recommendations. Existing local changes to SPEC.md, AGENT_LOG.md and USAGE.md were preserved; only SPEC.md and AGENT_LOG.md were edited in this step. No application code, dependency installation, change to the TP1 MCP server, model call, secret access, billing activation, commit or push occurred. No independent reviewer was triggered for this documentation-only specification update.

## 2026-11-03 · Exercise 2 candidate limit and assistant-authored criteria proposal
- Goal: Record the final candidate-limit decision and prepare a complete acceptance-criteria draft for student review, without implementation.
- Delegated: The student explicitly selected a maximum of ten candidates, each a workstation/time-slot pair satisfying the applicable rules and filters, and explicitly requested that the assistant formulate the criteria proposal. Earlier decisions were developed with disclosed ChatGPT assistance. The criteria wording proposed in the conversation is assistant-authored: it is not claimed as personally written by the student, approved by the professor, accepted into SPEC.md or functionally verified.
- Checkpoints: The model input section now records the cap, the smaller candidate-set case and no call for an empty set. The cap is a design choice, not a recommendation-quality or response-time guarantee. Reservation rules must still be checked after suggestion and confirmation. Applicable instructions and the existing specification were read; docs/UI.md was consulted only for the existing interface requirements. The proposed draft remains in the conversation; Acceptance criteria and Spec vs result were not filled in.
- Went wrong: The application does not exist yet. All proposed functional, fake-provider and PostgreSQL concurrency checks are future verification methods, not executed tests. The four remaining documentary gaps must not be hidden by treating the proposal as approved or by inventing build results.
- Verification: node checks/ex2.mjs returned exit code 1 with 28/32 checks passed. The four expected failures are Acceptance criteria are written, every acceptance criterion carries an id, the spec vs result note is filled in, and conventions are written. git diff --check returned exit code 0. The documentation changes were reviewed; no application or PostgreSQL test was executed.
- Changed by hand: The student chose the candidate limit and requested the draft. SPEC.md, AGENT_LOG.md and USAGE.md already had local changes; only SPEC.md and AGENT_LOG.md were edited here. No application code, installation, model call, secret manipulation, billing activation, TP1 MCP server change, CI change, commit or push occurred. No independent reviewer was triggered for this documentation-only draft preparation.

## 2026-11-03 · Exercise 2 selected criteria and slice 1 construction plan
- Goal: Record the selected AC-1 to AC-49 with the student's corrections, complete agent conventions and propose the first-slice plan before implementation.
- Delegated: The assistant-authored criteria were selected by the student as the functional target. The student supplied refinements for stable Google identity, both local/Google authorization checks, Monday-to-Friday hours, recorded versus simultaneous conflicts, the provider-call time budget, HTTP 401 after missing/invalidated sessions, and isolated demonstration data. Codex incorporated those refinements and prepared the plan; selection is not evidence of student understanding or pedagogical approval.
- Checkpoints: SPEC.md now records 45 final-project criteria and four first-slice criteria as unimplemented requirements, keeping the required headings. Google/AI simulated tests and future real integration trials are distinguished; none was run. docs/UI.md was checked: its concrete accessibility/layout items are present, but colour/radius tokens are a retained design extension and its additional timing, reload, evidence and dark-mode items are not silently claimed covered. AGENTS.md preserves approval/security/coverage rules and records the chosen conventions without inventing operational application commands. docs/SLICE1_PLAN.md proposes three checkpoints, files, dependencies, provisional PowerShell/Linux commands, sessions/services separation, demonstration restoration and a real Python coverage scope including the TP1 server.
- Went wrong: No application exists yet and Spec vs result remains empty. The existing CI does not install the planned development requirements and its default Node coverage is not Python coverage; future workflow alignment needs separate authorization, with no threshold reduction. The plan and future commands have not been executed or validated as working.
- Independent review: The custom reviewer was invoked once, read-only, because the plan specifies authentication/session architecture and coverage measurement. Its actionable finding was retained: the demonstration-password setup needed an explicit local procedure. The plan now describes masked interactive entry for newly seeded accounts, Django hashing, recovery through changepassword and separate fictitious test credentials. Its CI recommendation was also retained as future work: compare scopes and use the same coverage runner and reference result locally and in CI. No finding was discarded. Codex additionally clarified separate line/branch gates so a combined percentage cannot hide a line-coverage shortfall. These are plan corrections, not implementation results; provider access and future CI integration remain unverified.
- Verification: After the plan corrections, node checks/ex2.mjs returned exit code 1 with 31/32 checks passed. The sole expected failure is "the spec vs result note is filled in", deliberately left empty before construction and real trials. git diff --check returned exit code 0. A separate identifier check confirmed exactly AC-1 through AC-49, with 45 final-project criteria and AC-46 through AC-49 for slice 1. These structural checks do not validate behavior, coverage or pedagogical authorship. No functional, provider or concurrency test was executed.
- Changed by hand: The student selected and corrected the criteria in the attached request. Initial local changes to SPEC.md, AGENT_LOG.md and USAGE.md were preserved. This step edits SPEC.md, AGENTS.md and AGENT_LOG.md and adds only the plan document. No application code, installation, secret manipulation, provider call, billing activation, TP1 MCP server edit, CI edit, commit or push occurred.

## 2026-11-03 · Checkpoint 1: Django structure and data
- Goal: Implement only the authorized first checkpoint and stop before HTTP sign-in, protected pages/API or the other checkpoints until the student's manual feedback.
- Delegated: The student approved the three-checkpoint organization and explicitly authorized the project-local venv, necessary dependency installation, files/tests, initial migrations on a new demo database and generation of a new ignored development key. Codex authored the foundation code, tests and instructions; this does not prove student understanding or complete acceptance criteria. Existing assisted specification choices were preserved.
- Checkpoints: Python 3.13.7 in the new .venv; Django 5.2.18, pytest 9.2.0, pytest-django 4.14.0 and tzdata 2026.6 installed locally, with transitive versions pinned. Official Django 5.2/Python compatibility documentation was read; installed metadata and pip check were verified. The email user model and AUTH_USER_MODEL were defined before generating/applying data.0001_initial. Email identifiers are normalized to lowercase and protected against case-variant duplicates; this routine implementation choice is documented. Django hashes/checks passwords, while business roles remain distinct from framework administration flags. Laboratory contains its id and name. Only data/configuration exist; shared business services and HTTP routes remain future work.
- Local state: A new development key was generated without display in ignored .local/django-dev-key; no existing secret or Gemini configuration was read or reused. The dedicated data/demo.sqlite3 and marker are ignored and untracked. First seed --no-input created two fictitious students and three DEMO laboratories; second run created zero/zero. Both demo passwords remain unusable pending the student's masked changepassword commands. The seed never resets an existing password/role and rejects conflicting data without partial writes. Tests use independent settings, in-memory databases and generated temporary credentials.
- Went wrong: Initial venv/installation and temporary-directory access were restricted by the Windows sandbox; the required commands were retried with escalation. First pytest run had 22 successes and three temporary-directory setup errors. A later type annotation introduced a wrong pytest-django import; it was corrected to the actual installed Settings type, and the full suite passed again. No assertion was weakened. The documentary checker also required escalation to traverse pytest's temporary directories. Ignored pytest-cache-files-* leftovers were preserved rather than deleting without authorization. The existing CI does not install requirements-dev.txt and has no checkpoint-1 service layer to measure; it is not claimed ready and was not changed.
- Verification: Final pre-review foundation suite: 25 passed in 9.70 seconds. Django check reported no issues; makemigrations --check --dry-run reported no changes. All migrations applied on the new demo database and are checked in showmigrations; tests also build a fresh database through migrations. pip check reported no broken requirements. The unchanged TP1 unittest suite reported nine passing tests. node checks/ex2.mjs returned 31/32 (exit 1), solely the expected empty Spec vs result; git diff --check passed. No HTTP acceptance, real interactive password entry, provider integration, PostgreSQL concurrency or coverage result is claimed.
- Independent review: The exact custom reviewer was invoked once, read-only, after implementation and tests. No blocking code finding was returned. Its missing-journal finding was already resolved by the checkpoint entry added while the review was running; it is retained as an addressed documentation requirement, not an outstanding defect. Its two forward-looking recommendations were retained in the plan: add clickjacking protection before exposing screens, and name future HTTP acceptance tests with the exact AC ids. HTTPS configuration belongs to later deployment work. No recommendation was silently implemented outside checkpoint 1, and no finding was rejected. Manual password entry, Linux/Codespaces execution and CI alignment remain unverified.
- Changed by hand: Initial modifications to AGENTS.md, AGENT_LOG.md, SPEC.md and USAGE.md and the untracked plan were preserved. This checkpoint adds the Django foundation/tests/requirements, local initialization helper and CHECKPOINT1 guide, and updates .gitignore, AGENTS, README, plan, usage and this log. SPEC.md and the TP1 server are untouched in this checkpoint. No CI change, model call, billing activation, commit or push. Student password entry and manual inspection of the demo database are still pending; no move to checkpoints 2/3 is authorized yet.

## 2026-11-04 · Checkpoint 2: local sign-in, protected page and sign-out
- Goal: Implement only checkpoint 2 after the student's reported checkpoint-1 verification, then wait for the student's browser walkthrough before checkpoint 3.
- Student observations: The student reported personally setting both demonstration passwords, rerunning seed_demo with zero accounts/laboratories created, all migrations marked [X], three laboratories DEMO - Laboratory Alpha/Beta/Gamma, two active students with role=student, is_staff=0 and is_superuser=0, and no workstation/booking table. These are user-reported local checks, not an assertion that Codex replayed them or that the student's understanding was assessed.
- Delegated: Codex authored the HTTP adapters, shared access/authentication services, Django authentication adapter, templates, JavaScript/CSS, tests and documentation from the authorized scope. Existing work was preserved. No new dependency was installed, no seed/password/migration command was applied to the demonstration data, and the initial migration's SHA-256 remained DB3A8FE7A120260B3338A8ABE7B2E91BA1C90FF150EA01F340BC3230861A1D1B.
- Checkpoints: Django's native authenticate/login/logout and database-backed sessions handle credentials and session rotation/invalidation. Services carry no HTTP request or MCP message. Login errors are identical for incorrect, unknown and inactive credentials. POST login/logout retain Django CSRF protection. Return destinations are restricted to the existing internal /labs page and checked on both form display and POST. The protected page calls the shared access service and shows only the signed-in email and sign-out. There is no laboratory list/API, reservation, Google/AI integration or new MCP tool. CSS/templates provide labelled inputs, visible focus, mobile layout and explicit request states; their actual browser verification is still pending.
- Verification: The combined isolated suite reported 71 passed in 56.67 seconds (25 foundation and 46 checkpoint-2 cases). Tests cover AC-47 local sign-in, AC-46 page access and AC-49 page/session behavior, including active/inactive actors, old-cookie replay after server-side session deletion, actual CSRF enforcement and unsafe return URLs. AC-48 and the laboratory API parts remain for checkpoint 3. Django check with tests.settings reported no issues, migration-drift check no changes, and both JavaScript syntax checks passed. No coverage percentage is claimed.
- Local startup check: The documented runserver command served /login, CSS and both scripts with HTTP 200, and redirected anonymous /labs with HTTP 302 to /login?next=/labs. No demonstration credential was submitted. Django loaded its configured local key during ordinary startup; no secret file was displayed, regenerated, edited or reused for another purpose. The temporary server was stopped afterwards. The --insecure option only serves development static assets with DEBUG=False; it does not disable CSRF. No browser rendering or JavaScript execution is inferred from these HTTP responses.
- Documentary checks: node checks/ex2.mjs returned 31/32 (exit 1), solely the expected empty Spec vs result; git diff --check passed (exit 0). New Python modules compiled after the final line-wrapping cleanup. No check was weakened, and there is no diff in the TP1 server or CI workflow.
- Independent review: The exact custom reviewer was invoked once, read-only, after implementation and checks, due to the authentication/security and HTTP-interface changes. It found no blocking or important defect and independently confirmed collection of 46 checkpoint-2 tests with AC ids. Its only suggestion was finer Accept-header negotiation if API needs grow. This is retained as an optional future improvement rather than a required current correction: the existing browser forms and fetch clients use the intended HTML/JSON formats. No code correction was needed after review; browser rendering, student walkthrough, Codespaces and full coverage/CI remain unverified.
- Limits: Student browser/keyboard/mobile verification remains pending. Spec vs result stays empty, with partial traceability recorded explicitly. Existing CI alignment and full coverage measurement remain future work. No TP1 audit, MCP edit, CI modification, billing operation, commit or push.

## 2026-11-04 · Checkpoint 3: protected laboratory API and database-backed catalogue
- Goal and authorization: Implement only checkpoint 3, including a measured Python coverage gate and a safe manual AC-48 procedure. The student authorized coverage installation in .venv. Existing local changes were recorded before edits and preserved; no subsequent slice, CI change, commit or push is authorized by this step.
- Student observations: The student confirmed the login page and error message, signed-in access to Laboratoires, the anonymous redirect to /login?next=/labs, and keyboard sign-in/sign-out with visible focus. The prior foundation observations remain user-reported. The 380-pixel check is explicitly postponed at the student's request, not performed or passed, and does not block this implementation. No personal understanding or mobile conformity is inferred.
- Delegated: Codex authored the API/data/service modules, fetch catalogue, demonstration helpers, coverage runner, tests and guide. The student's requirements and already recorded assisted specification remain the source of behavior; generated code and automated assertions are not personal student authorship or manual approval.
- Implementation: GET /api/labs follows route → shared authenticated-actor service → data → ORM. Active sessions receive only id/name ordered by id; missing, invalid, expired or inactive sessions receive JSON 401 without a list or HTML redirect. The page retains its redirect behavior. The client uses the existing same-origin Django session, textContent, loading/list/empty/error states, explicit 401 handling and retry. No catalogue is embedded or substituted when a request fails. Authentication semantics and the existing login/logout flow are preserved; the service User type import was simplified without changing authentication behavior.
- Demonstration safety: The new demo_labs command separates list, backup, withdraw and restore. A durable, exclusively created snapshot must exist before withdrawing one canonical fictitious row; restoration preserves id/name and refuses to overwrite a divergent row. Helpers require the configured disposable SQLite target and marker, and refuse an evolved laboratory schema. Tests use isolated accounts/databases and temporary snapshots. None of these commands was executed against the student's demo database; accounts, passwords, roles and the three laboratories were not manipulated. CHECKPOINT3.md gives individual PowerShell commands for the student's later trial.
- Verification: The final measured run reported 103 pytest tests passed and nine unchanged TP1 unittest tests passed. Seven Node tests of the actual client module passed with simulated DOM/network; these do not verify browser layout or keyboard interaction. AC-46/47/48/49 cover page versus API access, valid/invalid/inactive credentials, expired sessions, read-only catalogue responses, removal/restoration/empty data, logout and replay of the old cookie. Foundation/migration tests remain included. Django check with tests.settings found no issue; makemigrations --check --dry-run found no change; JavaScript syntax and pip check passed. The new Node subprocess test initially hit sandbox spawn EPERM and passed unchanged outside that restriction.
- Coverage: coverage.py 7.17.1 was installed only in .venv. The real combined report is .local/coverage/45df6bbef57b420088ba7e907e8488cc/coverage.json. Services: 25/25 lines and 4/4 branches (both 100%). Global Python: 585/640 lines (91.41%), including 91/106 executed lines in the TP1 server; global branches 151/172 (87.79%, informative). The combined line/branch display is 90.64%, distinct from the line gate. Scope includes src, configuration, migrations, demo commands, manage.py, tools and the TP1 server. Only test code, the venv and third-party/generated metadata are outside production measurement; no production pragma/TYPE_CHECKING exclusion was added. Unexecuted local settings, manage.py and WSGI remain in the denominator. The unittest parent emits No data was collected because test code is excluded; instrumented TP1 subprocesses do contribute the reported executed lines. Raw files are retained in an ignored directory. No existing secret was read to improve coverage; tests use separate settings. This is not JavaScript or whole-project multilangage coverage, and CI is unchanged.
- Documentary status: node checks/ex2.mjs passed 32/32 (exit 0). Spec vs result now records executed automated evidence, earlier user observations and pending checkpoint-3 browser checks separately, as requested. It does not declare those manual checks successful. Complete browser verification, the deferred 380-pixel check, Codespaces and CI alignment remain unverified. No provider call, Gemini experiment, new key, billing operation or MCP-server change occurred.
- Preservation checks: git diff --check passed (exit 0). The initial migration retains SHA-256 DB3A8FE7A120260B3338A8ABE7B2E91BA1C90FF150EA01F340BC3230861A1D1B. No diff exists in mcp-server/ or .github/. Git ignore rules cover .venv, data/demo.sqlite3, the planned snapshot, .local reports/key and .gemini/.env; none is tracked. Checking those paths did not open secret contents. The local changes from earlier checkpoints remain uncommitted.
- Independent review: The exact custom reviewer was invoked once, read-only, after implementation and tests. No blocking or significant functional defect was found. Its actionable documentation finding was retained: the plan's final paragraph still described all project commands as provisional. It now distinguishes executed Windows commands from untried Codespaces/CI work. The optional suggestion to expand compact structures in the coverage-runner and Node tests was not applied in this step: it is a readability refinement, with no identified behavior or verification defect, and is not needed to complete the authorized checkpoint. No production-code correction followed review, so the measured test/coverage evidence remains applicable. Browser checks, real demonstration withdrawal/restoration, the postponed 380-pixel check and CI alignment remain unverified.

## 2026-11-04 · Checkpoint 3 correction: browser rejects the module MIME type
- Goal and provenance: Fix only the missing catalogue display reported by the student. Initial Git status was recorded; earlier dirty/untracked work was preserved. The student reported successful login, page identity/title/logout, no list or status text after a full reload, and all three id/name records when opening the authenticated API directly. Those are user observations, not proof of a working fetch interface. Codex authored this diagnosis, minimal correction, regression test and documentation.
- Demonstrated cause before edits: curl against the existing port-8000 server received HTTP 200 for both scripts, but labs.mjs had Content-Type text/plain while logout.js had application/javascript. The delivered module body was present. Python's MIME lookup likewise returned text/plain for .mjs. Using the computer-use skill and the available Edge window, Codex observed the existing connected page and the Console error explicitly rejecting labs.mjs because module scripts require a JavaScript MIME type. No user password, cookie value or existing secret was read. Source inspection found matching selectors, payload.laboratories and the expected hidden-until-loaded behavior; the module rejection prevents initialization, messages and fetch.
- Minimal correction: src/config/base.py imports mimetypes and calls add_type("text/javascript", ".mjs") at startup, with an explanatory Windows comment. This changes only the process MIME mapping, not the Windows registry or browser security. Client code, CSS, API/service/data rules, sessions and CSRF are unchanged. tests/test_access.py now asserts the exact module script tag in rendered HTML. tests/test_static_assets.py starts a fresh test-settings subprocess after installing the wrong MIME association, then checks the real static handler's status, Content-Type and original file content.
- Regression evidence: The new test failed before correction with AssertionError: text/plain (one failed test; separate sandbox cache-write warnings). After correction, the selected static/access/labs/auth/logout suite passed 56/56 in 34.52 seconds. The full coverage runner then passed 104 pytest tests in 37.08 seconds and nine unchanged TP1 tests in 5.515 seconds. The seven unchanged Node tests passed. Django check with tests.settings reported no issues. A separate ephemeral loopback HTTP server using the corrected settings returned 200 and text/javascript for the exact original module body. No tests were weakened.
- Coverage evidence: Actual report .local/coverage/d51d9bd3f3a04cd18c4cbaf39c002ac6/coverage.json; services 25/25 lines and 4/4 branches; global 587/666 lines (88.14%) and 151/174 branches (86.78%, informative), combined display 87.86%. The unchanged source configuration additionally discovered the temporary .local/mime-browser-check.py fixture (24 uncovered lines, two uncovered branches); it was not removed from the denominator or masked to improve coverage. The prior 585/640 figure remains historical. The unittest parent still emits the documented No data was collected warning, while TP1 child execution is included. No coverage threshold, exclusion or CI change was made.
- Browser limit: An isolated server was prepared on port 8765 with SQLite in memory, a fictitious test account, public test settings and cookie names distinct from the user's session. The user stopped Computer Use with the physical Escape key before its browser trial. No further computer-use action was issued; the temporary server was stopped, discarding its in-memory data. The ephemeral fixture remains ignored locally. No corrected rendering or user confirmation is claimed. The existing port-8000 server and demonstration data were preserved; the guide instructs Ctrl+C then the exact --noreload restart command.
- Preserved scope: No migration edit (initial SHA-256 still DB3A8FE7A120260B3338A8ABE7B2E91BA1C90FF150EA01F340BC3230861A1D1B), demonstration mutation, secret access, new dependency, supplier call, MCP edit, CI change, commit or push. The 380-pixel check remains postponed and unvalidated. SPEC records the failed display, the observed direct API result and the remaining post-fix browser check separately.
- Documentary verification: node checks/ex2.mjs passed 32/32 with exit 0 after these updates; git diff --check passed with exit 0. These structural checks and the prior passing unit tests do not establish a successful browser catalogue. The prepared temporary server was stopped with Ctrl+C; its KeyboardInterrupt is the expected manual shutdown, not a failed application test.
- Independent review and response: The exact custom reviewer was invoked once, read-only, after implementation and tests. It found no significant defect in the MIME correction or regression test. Its single actionable finding was retained: the temporary ignored Python fixture was being discovered by coverage.py despite being outside the production inventory. Its content was preserved without deletion as .local/mime-browser-check.py.txt, with source/destination checked within the repository's .local directory. No application source, threshold or coverage configuration was removed/changed. The full measurement was then rerun: 104 pytest tests passed in 36.63 seconds, nine TP1 tests in 5.198 seconds; final report .local/coverage/185585b069ee429f98c008ca65e24136/coverage.json, exit 0, 587/642 global lines (91.43%), 151/172 branches (87.79%), combined display 90.66%, services still 25/25 lines and 4/4 branches. Earlier reports are retained as historical evidence. No finding was rejected; browser rendering after restart and the deferred 380-pixel check remain unverified.

## 2026-11-04 · Checkpoint 3: actual-instance cache diagnosis and visible catalogue
- Goal and attribution: The student reported another empty catalogue after the MIME correction and explicitly authorized identification/restart of only the development server on 8000, plus real-browser diagnosis. Initial Git status and applicable instructions were read; earlier modifications were preserved. Codex authored the additional diagnosis, one template URL change, regression test and evidence notes. No new student confirmation or assessment of understanding is inferred.
- Process identification: Windows CIM access was sandbox-blocked, then the scoped metadata read succeeded with approval. Listener PID 5544 belonged to the repository's .venv Python launch (parent 42360), command manage.py runserver 127.0.0.1:8000 --insecure --noreload. A full HTTP GET on this real instance already returned text/javascript for labs.mjs. Its response body and logout.js matched the repository; neither script contains imports. No process environment dump, key file, password or cookie value was inspected.
- Demonstrated remaining cause: In the actual connected Edge tab, an ordinary reload captured four requests: the page, CSS, logout.js and labs.mjs. The latter returned 304 Not Modified; the Console still rejected its cached text/plain MIME type, and no fetch to /api/labs occurred. A separate conditional HTTP request reproduced the 304 without Content-Type. Updating only the MIME mapping left the module's Last-Modified unchanged, allowing the old response metadata to survive revalidation.
- Correction and regression: src/templates/labs.html now requests /static/js/labs.mjs?v=2, with a comment explaining the cache version. No client logic, imports, API/data/service behavior, CSS or security protection changed. tests/test_access.py extracts the script URL from real rendered HTML and models conditional revalidation of the old URL through Django's static handler. Before the template change it failed on 304 != 200; afterwards the nine access/static tests passed, including the strengthened script-tag assertion. The broader targeted first-slice suite then passed 57 tests in 54.02 seconds. All accounts/databases in these automated tests are isolated. Python production and JavaScript were unchanged, so the previous full coverage and Node results are reused rather than claimed rerun.
- Authorized restart: The port owner and command were rechecked immediately before stopping only PID 5544. A new background launch used the repository working directory, its .venv and explicit --settings=src.config.settings. Verified listener PID 19816, parent launcher 17820. No other Python process was stopped. Django loaded its normal local configuration during startup; Codex did not inspect or disclose any secret value. The existing session and all demonstration rows were preserved. Ignored logs: .local/server-5358eca71a844e0dbbbee0a566ac12a1.out.log and .local/server-5358eca71a844e0dbbbee0a566ac12a1.err.log. The server remains running; future process IDs must be reidentified rather than copied blindly.
- Real browser evidence: In the same Edge tab at http://127.0.0.1:8000/labs, an ordinary reload, without disabling the cache, produced 200 for labs.mjs?v=2 followed by a 200 fetch to /api/labs, initiated at module line 23 (155 response bytes). The page accessibility tree contained the status "3 laboratoire(s) affiché(s)." and Alpha/Beta/Gamma as list items. After closing DevTools, a tool screenshot visibly confirmed all three laboratory names. A direct verification of the versioned module, logout.js and CSS returned 200 with text/javascript, application/javascript and text/css respectively, and byte-for-byte repository content. This is Codex's actual-browser observation, not an isolated HTTP test substituted for rendering and not an invented student report.
- Limits and preservation: The browser's successful display does not complete the manual withdrawal/restoration or API-after-logout demonstrations. The 380-pixel check remains postponed. No demonstration row/account/password/migration was changed, no new dependency or CI/MCP edit, no supplier call, billing operation, commit or push occurred. No broader slice was started.
- Documentary checks: node checks/ex2.mjs passed 32/32 (exit 0), and git diff --check passed (exit 0). README, AGENTS, SPEC and the plan/guide now distinguish the observed real-browser list from the still-pending manual scenarios. The migration SHA-256 remains DB3A8FE7A120260B3338A8ABE7B2E91BA1C90FF150EA01F340BC3230861A1D1B, with no diff in mcp-server/ or .github/.
- Independent review: The exact custom reviewer was invoked once, read-only, after the correction, targeted tests and real-browser observation. No blocking or important finding was returned. Its only maintenance suggestion was retained in CHECKPOINT3.md: ?v=2 is a deliberate one-time cache invalidation, and a later change requiring invalidation must update that version. No further production change was necessary, no finding was rejected, and no asset-build system was added. Remaining uncertainties are the already named manual scenarios and deferred 380-pixel check, not the now-observed initial catalogue display.

## 2026-11-04 · AC-48: authorized demonstration withdrawal and exact restoration
- Goal and attribution: The student explicitly authorized temporary withdrawal of only DEMO - Laboratory Beta from the local demonstration database, followed by exact restoration using the existing guide. Applicable instructions, the procedure and initial dirty/untracked Git status were read; pre-existing work was preserved. Codex performed the browser observations and authored these evidence notes, not the student. The student's separate new observation is that /api/labs after logout displayed {"error": "Connexion requise."} without laboratories; this did not supply an HTTP status and is not presented as manual proof of 401.
- Before mutation: The real connected Edge tab at http://127.0.0.1:8000/labs visibly showed all three names in Alpha/Beta/Gamma order. demo_labs list confirmed the repository's data/demo.sqlite3 and rows 1/2/3. The existing guards validated the marked disposable database, exact model fields and absence of model relations. The backup command created data/demo-lab-2-ac48-20261104.json exclusively and reported Snapshot saved. No database change. A read-only SQLite inspection confirmed the backup matches every column of Beta (id 2, name DEMO - Laboratory Beta), with no incoming foreign keys or table triggers. git check-ignore confirmed that both database and backup are ignored.
- Browser evidence: The documented withdraw command removed only the saved Beta row and reported One demo laboratory withdrawn; snapshot preserved. Reloading the same connected /labs tab visibly showed 2 laboratoire(s) affiché(s). with Alpha and Gamma only. The documented restore command was run immediately afterwards and reported Laboratory restored. Reloading visibly showed 3 laboratoire(s) affiché(s). with Alpha, Beta and Gamma in the original order. The result is an observed 3 → 2 → 3 in the real browser, not a simulated DOM or isolated HTTP result. No screenshot file was archived in the repository.
- Final database state: demo_labs list again returned the original ids/names 1/2/3. A read-only comparison asserted equality between all Beta columns and the pre-withdrawal JSON snapshot, and equality of the complete ordered catalogue to its original three rows. Both assertions passed. Beta is restored identically; the backup remains available. No account/password/role/session preparation or migration was run; the existing authenticated browser session remained usable. Normal management-command startup used Django's configured runtime; no secret value, password or cookie was inspected or disclosed.
- Scope and limits: Only CHECKPOINT3.md, SPEC.md and this journal were edited, besides the explicitly authorized temporary demo-row mutation and ignored backup creation. No application code, TP1 server, dependency or CI change, provider call, billing action, commit or push occurred. The 380-pixel check remains deferred. Previous isolated tests for empty lists and read-only catalogue consultation are retained as previous evidence, not claimed rerun. No independent reviewer was triggered for this execution of an existing demonstration procedure and documentation-only update; no architecture or behavior was changed. This does not certify the student's understanding or complete the final project.
- Documentary verification: node checks/ex2.mjs first stopped with EPERM while scanning an existing pytest-cache-files directory in the sandbox; the authorized rerun passed 32/32, exit 0. git diff --check passed, exit 0. The three documentation edits were reviewed. No functional tests or coverage measurement were rerun because no application or test code changed in this step.

## 2026-11-04 · TP2 local finalization and CI preparation, before publication
- Goal and attribution: The student authorized local workflow/command alignment and documentation, explicitly forbidding commit/push, another slice, provider calls, secret inspection or demo-data changes. Codex recorded initial Git status, read applicable instructions and inspected the relevant workflow, dependency/coverage configuration and guides only. Existing dirty/untracked slice work was preserved. Specification choices and wording retain their disclosed ChatGPT/Codex assistance; neither personal authorship nor professor approval is invented.
- CI adaptation: .github/workflows/ci.yml retains test, coverage, mcp and spec on push/pull_request, with read-only repository permissions. Python 3.13 is selected explicitly in Python jobs, Node remains 22.x, and the existing checkout/setup action versions are preserved. Both declared requirements files are installed in CI; no new dependency or local installation was introduced. The test job checks pip/Django/migration drift with tests.settings, runs pytest, preserves npm test for TP1 and explicitly runs the seven Node tests. The coverage job calls the unchanged tools/check_coverage.py/.coveragerc, enforcing 100% Python service lines and branches and 80% global Python lines including TP1 subprocesses. The meaningless Node service-path pass over non-JavaScript services is replaced by the real Python service gate; the separate existing 80% Node line threshold remains. The original MCP checker, spec check and conditional future Docker build remain, without continue-on-error or weakened tests. Missing application setup no longer produces a successful No project yet notice.
- Documentation: README now gives the actual Windows startup/test path and separates slice 1 from future functionality. AGENTS and the plan distinguish implemented HTTP/service behavior from future MCP/model work and update the observed AC-48 status. Checkpoint guides retain historical results with explicit links to current evidence. SPEC contains only factual results; the student-reported API error body is not treated as proof of its HTTP status. USAGE adds the previously omitted AC-48 session and this finalization, with unavailable usage figures rather than invented tokens/costs. docs/TP2_FINALIZATION.md records commands, coverage scope, CI limits, proposed publication files and commit message.
- Executed locally: Python 3.13.7, Node 22.12.0, existing Django 5.2.18/coverage.py 7.17.1. pip check found no conflict; Django check found no issues and makemigrations --check --dry-run with tests.settings found no change. The coverage runner passed 105 pytest tests in 61.35 seconds and nine unchanged TP1 tests in 8.603 seconds, exit 0. Its report is .local/coverage/8fe5122df5804a579d21ff74c2228c64/coverage.json: services 25/25 lines, 4/4 branches; global 587/642 lines (91.43%), 151/172 branches (87.79%), combined display 90.66%; TP1 91/106 lines (85.85%). No source or exclusion was removed to obtain these figures.
- Node/MCP evidence and initial restrictions: The seven existing JavaScript tests passed with the 80% line gate; labs.mjs measured 97.26% lines, 95.65% branches, 100% functions. This does not cover unloaded login/logout scripts or all frontend assets. The original MCP verifier passed 12/12 using the local venv Python. Initial sandbox runs failed: Python had 88 passes/17 fixture setup errors due to Windows temporary-directory permissions, and Node spawn calls hit EPERM. Authorized reruns succeeded unchanged. The documented unittest-parent No data was collected warning and Node experimental glob warning remain visible; subprocess coverage is present in the combined report.
- Preservation and limits: Metadata-only Git checks confirm the Gemini env file, local Django key, demo database, Beta backup and venv are ignored and untracked; no secret contents are accessed. No Beta manipulation, account/password/session/migration change, TP1 source edit, billing activation or provider request occurred. The real browser and AC-48 evidence are reused, not claimed replayed. The 380-pixel check remains deferred. Ubuntu dependency installation, GitHub Actions and Codespaces have not been executed; remote success cannot be claimed before future authorized publication. Official GitHub Python Actions documentation informed the explicit interpreter/dependency setup; no technical exercise or further slice was started.
- Documentary verification: node checks/ex2.mjs passed 32/32, exit 0, using the authorized unrestricted invocation because of the already established temporary-directory scan restriction. git diff --check passed, exit 0. Metadata-only checks confirmed that each protected local file exists, is ignored and untracked, with no tracked file anywhere under .venv/, .local/ or data/. The shareable .gemini/settings.json and .env.example remain tracked. Initial migration SHA-256 is unchanged: DB3A8FE7A120260B3338A8ABE7B2E91BA1C90FF150EA01F340BC3230861A1D1B. The TP1 directory has no diff.
- Independent review: The exact custom reviewer was invoked once after workflow adaptation and tests, in read-only mode without subagents. It compared this turn against the saved initial documentation/workflow copies and found no blocking or important problem. No finding was rejected and no additional correction was required. It confirmed the existing jobs/checks, dependency reuse, real Python service/global gates and honest evidence distinctions. Remaining uncertainties are the first remote GitHub/Ubuntu execution, untested Codespaces, deferred 380-pixel display and Node coverage limited to labs.mjs. The proposed publication manifest contains exactly 71 existing non-ignored files; local Markdown links resolve and nothing is staged. Publication awaits a separate instruction.

## 2026-11-04 · Authorized TP2 publication and remote verification
- Authorization and preparation: The student explicitly authorized staging the proposed TP2 files, the requested commit and a normal push to origin/main, including targeted CI corrections if necessary. Initial status was recorded; the manifest contains exactly 71 changed/untracked files and there is no change outside it. The origin URL is the existing phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus repository. A fresh fetch confirmed local main and origin/main both at c2300cfaf273b2cdf4d84476980e99aff4039a85, with zero commits ahead/behind. No destructive reset, forced push or history replacement is planned.
- Evidence reuse: Application, test, dependency, coverage and workflow files are unchanged since the successful local coverage run recorded above; their modification times precede that report. The 105 pytest, nine TP1, seven Node tests, coverage gates and MCP checks are reused as local evidence, not called remote results. The publication will be checked against its exact SHA in GitHub Actions. The existing browser evidence, restored Beta, deferred 380-pixel test and assistant attribution are preserved. No demonstration mutation, provider call or applied migration edit is part of this operation.
- Pre-commit verification: Staging was restricted to the exact 71 manifest paths. The staged whitespace check exposed one pre-existing extra blank line at the end of tests/test_static_assets.py, previously untracked; only that blank line was removed. Its targeted test passed (1 test; a sandbox pytest-cache write warning remained), with no assertion or production change. The staged whitespace check then passed; ex2 passed 32/32. Metadata-only checks excluded secrets, venv, demo data, backups and temporary files. The exact custom reviewer ran once, read-only, on the staged diff and found no blocking or important issue. No finding was rejected and no further correction was required.
- Delivery and remote evidence: Commit 4243d717716142b45ab8304abf21c2056f28fdb7, titled feat(lab-booking): deliver TP2 first slice with tests and CI, was pushed normally to origin/main. Workflow https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/41758283141 is a push run for that exact SHA. All four jobs passed: test 126339503831, coverage 126339503494, mcp 126339503907, spec 126339503816. Test logs show 105 pytest passes (17.93 s), nine TP1 tests and seven Node passes, with successful dependency/Django/migration checks. MCP reports 12/12 and spec 32/32. Only Docker image builds was conditionally skipped because no Dockerfile exists; no required job failed or was disabled. No CI correction was needed.
- Measured in CI, not inferred from local results: Ubuntu used CPython 3.13.17 and Node 22.23.4. The coverage job independently ran 105 pytest tests (12.79 s) and nine TP1 tests, then reported global lines 587/642 (91.43%), global branches 151/172 (87.79%), services 25/25 lines and 4/4 branches, TP1 91/106 lines; combined display 90.66%. Node measured labs.mjs at 97.26% lines, 95.65% branches and 100% functions. The existing scope and exclusions were unchanged. Job logs were read through the GitHub connector; the public Actions API identified the push run because the connector's run-list tool only lists pull-request events. No token or local secret was inspected. A documentation-only follow-up records these observed results and will itself be checked on its exact published SHA; it does not change the tested code or CI.
## 2026-11-11 · TP3 checkpoint 1A — corrected plan and authorized autonomy

- Student review: PostgreSQL becomes active for the future booking slice; SQLite
  remains TP2. No portability of future PostgreSQL constraints is requested.
  Personnel booking restrictions are undecided and must not be added.
- Corrected sequence: 1A driver/configuration/dedicated PostgreSQL databases and
  existing migrations; later explicit checkpoint for Workstation/Booking and
  constraints; then services/refusals/concurrency, HTTP permissions and browser.
  Slice 2 criteria, final refusal contracts and the personal architecture note
  remain student work to review before their corresponding construction steps.
- Autonomy: checkpoint 1A only; local .venv installation and new local profiles
  authorized. No pre-existing secret, SQLite write/transfer, demo passwords,
  business model/migration, btree_gist, CI/npm change, provider, commit or push.
- Initial Git: clean main at b4c4cc6a38e2fc39e8528eb8481923454076d2c9.
- Initial SHA-256: data/demo.sqlite3
  983e3847e7495dff0652b1cf7cb7928c02d0c075db19f113f1dba04f4dcbdcaa;
  data/demo.marker bc4f39968f679287f482976d8afa45ae7e4d28443882f5ddaaa031859d26182e;
  src/data/migrations/0001_initial.py
  db3a8fe7a120260b3338a8abe7b2e91ba1c90ff150ea01f340bc3230861a1d1b.
- Installed Psycopg/psycopg-binary 3.3.8 in project .venv only; pip check passes.
  Existing Python 3.13.7 / Django 5.2.18 preserved. New profiles are under the
  already ignored .local directory. No pre-existing key was read or reused.
- Administrative authentication is deliberately left to the student's masked
  local terminal. Provisioning, PostgreSQL migration and PostgreSQL test results
  are pending, not reported as successful. See docs/POSTGRES_1A.md.
- Initial synthetic configuration test attempt: 1 pass, 1 explicit PostgreSQL
  skip and 8 temporary-directory permission errors in the sandbox. A unique
  temporary directory and an authorized rerun are used without weakening tests.
- Assistance: Codex proposed and implemented the technical preparation and this
  log; it does not claim student authorship of criteria, understanding or
  professor acceptance. The 380-pixel check remains deferred.
- Authorized rerun on isolated SQLite test settings: **114 passed, 1 skipped**
  in 66.37 s; the skip is the explicit live PostgreSQL identity test. Django check
  reports no issue; makemigrations --check --dry-run detects no change. SQLite,
  its marker and migration 0001 retain their initial SHA-256 values. No existing
  business assertion was modified. PostgreSQL tests/migrations remain pending.
- One read-only custom reviewer ran as required for a dependency/security change.
  Both important findings retained: chmod is not a private Windows ACL; existing
  PostgreSQL object preflight needed explicit tests. New empty profiles now have
  inherited ACLs removed and current-user access granted before credentials are
  written. Added existing-role/database refusal tests, a synthetic ACL test and
  a native empty-file ACL check. No finding rejected. Targeted rerun: 13 passed,
  1 skipped in 0.77 s. No provider, database provisioning or demo mutation occurred.
- Local masked provisioning command sent to the student. Administrative input,
  real PostgreSQL migrations/tests and role inspection are still pending. The
  checkpoint is prepared, not declared operational or completed.

## 2026-11-11 ? Jalon 1A completed on an independent local instance

- Initial state: previous authorized 1A files were already modified/untracked;
  they were preserved. The student authorized the independent cluster and its
  new bootstrap credential [REDACTED], random distinct application credentials,
  private local storage and exact cleanup of this operation's temporary files.
  No pre-existing secret or 5432 authentication configuration was consulted.
- PostgreSQL 16.4 binaries reused; no installation, cloud, service registration,
  provider call, CI change, npm change, business model/migration, commit or push.
- New cluster under LOCALAPPDATA/LabBooking/PostgreSQL16, owned by current user;
  only 127.0.0.1:5433, cluster_name=lab_booking_1a, UTF8 and SCRAM-SHA-256.
  Initialization refused existing paths/profiles and checked the dedicated port.
  ACLs were applied before secret writes, including the temporary initdb pwfile;
  finally removed that exact file. Bootstrap/dev/test passwords are distinct.
- Private ignored profiles: .local/postgres-1a-bootstrap.json (cluster admin),
  .local/postgres-1a-dev.json and .local/postgres-1a-test.json. Their contents are
  never logged. The bootstrap account is separate from Django roles.
- Created lab_booking_1a owned by lab_booking_1a_dev, and test_lab_booking_1a owned
  by lab_booking_1a_test. Both application roles lack SUPERUSER, CREATEDB,
  CREATEROLE, REPLICATION and BYPASSRLS. PUBLIC access revoked for these DBs;
  own-base connections succeeded and cross-base connections were refused.
- All 16 existing migrations applied on empty PostgreSQL development; all [X].
  Django checks and migration drift checks passed. Development data_user,
  data_laboratory and django_session remain empty. No SQLite seed was redirected.
- Incident: pg_ctl startup succeeded but captured inherited Windows pipe handles
  kept the initializer waiting. Interrupting that process also stopped this new
  cluster. Changed run_pg output to DEVNULL, then restarted and provisioned the
  identified cluster without reinitialization. A regression test protects this.
- Full PostgreSQL run: 118 passed, 1 failed in 75.76 s. Existing test
  test_guard_refuses_unmarked_or_wrong_database assumes SQLite and expects its
  marked-path acceptance. PostgreSQL correctly refuses this SQLite seed. Its
  assertions were preserved. Applicable PostgreSQL rerun: 121 passed, 1 deselected
  in 98.30 s. Full isolated SQLite rerun: 121 passed, 1 skipped in 97.77 s; only
  the explicit PostgreSQL identity proof skips on SQLite.
- Read-only independent custom reviewer ran once for this new task. Both findings
  retained: direct provisioner also needs the exact data_directory check, and
  previous pending log status needs an explicit final entry. Both corrected.
  No finding rejected. Post-review targeted PostgreSQL tests: 18 passed in 1.60 s.
- Dedicated stop/start/status verified successfully; cluster left running.
  Windows reboot itself not performed; manual restart instructions are in
  docs/POSTGRES_1A.md. Existing service postgresql-x64-16 still running at PID 5832.
- SQLite demo SHA-256 remains
  983e3847e7495dff0652b1cf7cb7928c02d0c075db19f113f1dba04f4dcbdcaa;
  migration 0001 remains
  db3a8fe7a120260b3338a8abe7b2e91ba1c90ff150ea01f340bc3230861a1d1b.
  No account/hash/session/laboratory transfer or demonstration mutation.
- No new secret found in Git candidates or the dedicated server log; local
  profiles ignored and untracked. Coverage not remeasured; thresholds and scope
  untouched. This checkpoint proves PostgreSQL infrastructure, not future
  booking/concurrency rules. The 380-pixel check remains deferred.
- Codex authored the infrastructure and documentation; no student criteria or
  personal architecture note were invented. Stop before the next checkpoint.

## 2026-11-11 ? Local commit closure of PostgreSQL checkpoint 1A

- Explicit scope: final checks and a local commit only; no push, CI change,
  provisioning replay, data transfer, new feature/criterion or reservation model.
  Initial Git state comprised the previous 1A files; no unrelated changes found.
- Existing coverage runner first passed at 711/840 global lines, 175/216 global
  branches, services 25/25 lines and 4/4 branches. Added twelve useful synthetic
  safety cases in tests/test_postgres_tools_safety.py; 12/12 passed on both
  explicit SQLite and PostgreSQL settings. No real DDL/lifecycle call in them.
- Final unchanged runner: 134 pytest passed, 1 skipped in 90.48 s on SQLite test
  settings, then 9 TP1 unittest passed in 7.021 s. Global lines 767/840 (91.31%),
  branches 189/216 (87.50%); services 25/25 lines and 4/4 branches (100% each).
  TP1 91/106 lines. Production inventory: 38 files, none missing, all existing
  thresholds/exclusions preserved. Report .local/coverage/f1d8b962758c46b4bd6ca35169b1c908/coverage.json.
- This is SQLite-based coverage, not measured PostgreSQL coverage. The previously
  observed real PostgreSQL regressions are reused honestly: full run 118 pass/1
  SQLite-guard failure; applicable rerun 121 pass/1 deselected; post-review
  targeted PostgreSQL 18 pass. No concurrency or booking behavior tested.
- The sole PostgreSQL deselection is
  tests/test_demo_data.py::test_guard_refuses_unmarked_or_wrong_database. Its
  vendor/path/marker acceptance specifically targets SQLite. The unchanged test
  is executed in the complete SQLite run. The sole SQLite skip is the explicit
  PostgreSQL identity/schema check, not a business refusal test.
- One independent read-only reviewer ran for this closure. No blocker. Its
  missing-negative-test finding was evaluated and rejected: existing
  tests/test_postgres_config.py::test_same_named_cluster_in_other_directory_is_refused
  already asserts RuntimeError, no profile directory and only the identity SELECT
  for a different data directory despite matching port/name. No duplicate test
  or production change was needed. Existing tests and assertions preserved.
- New profiles remain ignored/untracked with private ACLs. Data directory remains
  outside the repository. Exact temporary initdb file remains absent. New secrets
  checked without display against Git candidate files. SQLite demo and migration
  0001 SHA-256 values remain those recorded above. Coverage runner, .coveragerc,
  CI, npm command and TP1 code remain unchanged.
- Warnings retained: the TP1 parent process reports no collected data because its
  tests are excluded, while actual server subprocesses are present and measured;
  Git reports LF/CRLF normalization. Neither warning is hidden or treated as a
  remote result. The 380-pixel check remains deferred. Codex assisted this work.

## 2026-11-11 ? TP3 checkpoint 1B ? PostgreSQL models and schema

- Initial Git clean at local commit 7b3c375c151aa03bddd7c51466be34ed099ef794.
  User authorized models, new PG migrations, dedicated verification database,
  btree_gist and tests, then a local commit only. No service/HTTP/UI/MCP/AI,
  dependency, CI change, seed/transfer, push or existing migration edit.
- Explicit student decisions recorded in SPEC.md: student-only creation and
  repeated cancellation of one's own already-cancelled booking returns 200 with
  current state and no new mutation. These remain future service/HTTP rules;
  no student criteria or personal architecture note were invented by Codex.
- Workstation: Laboratory PROTECT, name, operational boolean, per-lab uniqueness.
  Booking: owner/post PROTECT, aware start/end/created/cancelled timestamps.
  Constraints: positive exactly-one-hour interval; immediate GiST exclusions
  for non-cancelled workstation/owner TSTZRANGE intervals with [) bounds.
- Added only numbered 0002_btree_gist and 0003_workstation_booking. Existing
  0001 SHA256 remains db3a8fe7a120260b3338a8abe7b2e91ba1c90ff150ea01f340bc3230861a1d1b.
  btree_gist is trusted: non-admin owners applied it without added role privilege.
- Bootstrap used only to create fresh lab_booking_1b_verify, owned by the existing
  dev role and with PUBLIC privileges revoked. Full 18-migration chain applied
  there successfully; all business/session tables empty. Development and test
  dedicated databases also migrated; no development seed or data transfer.
- Tests cover valid row, invalid intervals, exact and partial conflicts for post
  and owner, consecutive slots, cancelled row retention/conflict release,
  workstation name uniqueness, aware PG columns and non-admin role, ORM PROTECT
  and raw SQL FK refusal. Test titles name partial AC-14/15/16/17/18/19/25/28.
  No role/quota/current-time/hours/owner-service/HTTP/concurrency proof is claimed.
- Initial full run before test adaptation: 138 passed, 14 failed, 1 deselected.
  Failures exposed historical assumptions that current schema has only User/Lab,
  the old demo guard permits snapshots, and the new CLI parser consumed pytest
  argv. Initial-migration test now inspects historical migration state; current
  schema identity expects new tables. Snapshot unit fixture isolates the full
  guard; an added real guard test refuses new relations before mutation. Existing
  snapshot/refusal assertions and SQLite vendor guard remain intact. CLI main
  accepts explicit argv in unit tests; its exit-status assertions are unchanged.
- Targeted adaptation run: 67 passed. Final runner --postgresql: 155 pytest passed,
  1 SQLite-specific test deselected, no skipped tests in 54.16 s; 9 TP1 unittest
  passed in 8.881 s. Last schema-only run: 19 passed; JS regression: 7 passed.
- Only deselection: test_guard_refuses_unmarked_or_wrong_database, whose SQLite
  vendor/path acceptance is not a PostgreSQL regression. No other test excluded.
  No SQLite suite/migration executed for 1B; SQLite is preserved as TP2 data.
- Measured PostgreSQL coverage: services 25/25 lines, 4/4 branches; global
  808/885 lines (91.30%), 188/218 branches (86.24%). Production inventory has
  41 files and no missing file. Thresholds and exclusions unchanged, TP1 included.
  Report .local/coverage/2f42e953a1ab4854a38829bb823764e6/coverage.json.
- Django check and migration drift pass. SQLite demo hash remains
  983e3847e7495dff0652b1cf7cb7928c02d0c075db19f113f1dba04f4dcbdcaa;
  marker unchanged. No action targeted the existing 5432 instance or old secrets.
- One independent read-only reviewer: no blocking/important issue. Its requests
  for final journal and explicit historical CI incompatibility were retained.
  More precise Catalogue typing applied to new tests. Existing helper dict typing
  left outside this task. No architectural extension made after review.
- CI remains unchanged and uses historical SQLite commands: it is not declared
  ready for publishing PostgreSQL 1B. Future CI alignment needs separate approval.
  Slice 2 criteria/status contracts and personal architecture note remain open.
  The 380-pixel check is deferred. Stop before business services. Codex assisted
  the implementation, test adaptation and documentation; no acceptance inferred.

## 2026-11-11 ? TP3 checkpoint 2A ? read-only availability and personal history

- Initial Git clean at 76c23c2c48efd4a09919ad165ff46e238335a643, ahead two local
  commits. Scope/partial AC-13, AC-14 and AC-28 recorded in READ_SERVICES_2A before
  implementation. Filtering also partially supports AC-11/17/18/19/20/21/25.
  No approved AC rewritten, renumbered or invented. Slice 2 grouping remains open.
- Tests written first: initial AC-13/14 case failed with missing service module.
  Implemented src/data/booking_reads.py eager ORM projections and
  src/services/booking_reads.py transport-independent immutable read results.
  No ORM in services; no creation/cancellation/HTTP/UI/MCP/AI built.
- Availability: weekdays 08-18 Europe/Sofia, UTC aware one-hour [) slots, strictly
  future and operational posts only, uncancelled occupation and own cross-lab
  conflicts removed. Global future quota includes offline posts, excludes cancelled,
  current and past rows. Staff get no reservable proposals; authenticated personal
  history remains available. Reads offer no transactional creation guarantee.
- History owner comes exclusively from trusted actor.user_id, never a client
  owner ID. Descending start then descending booking ID, all past/current/future/
  cancelled rows and current workstation state. Explicit domain/auth errors.
- Initial 13 tests passed. First full run had 175 passed, 1 failed, 1 deselected:
  the default-clock test's foreign-history fixture also occupied today's slot,
  producing 17 rather than expected 18 candidates. Moved that fixture to tomorrow
  while preserving its foreign-owner detection and original assertion. No service
  rule or business assertion changed to ignore an occupied slot. Final direct run
  21 passed in 2.39 s; invalid/absent/empty and clock cases included.
- Final unchanged runner --postgresql: 176 pytest passed, 1 deselected, no skipped
  tests in 221.64 s, followed by 9 TP1 unittest passed in 24.045 s. Only deselection
  is historical SQLite guard test_guard_refuses_unmarked_or_wrong_database.
  PostgreSQL coverage: services 103/103 lines and 34/34 branches; new service
  78/78 and 30/30. Global lines 901/978 (92.13%); branches 218/248 (87.90%).
  Inventory 43 production files, no missing file. Thresholds/exclusions unchanged.
  Report .local/coverage/056ed6d01e43403f9d62846fec47dcaf/coverage.json.
- Django check and migration drift pass. No migration applied or added; no seed,
  development data transfer, 5432 operation, dependency or CI change. SQLite and
  the original migration are checked against prior hashes before local commit.
- One independent read-only reviewer found no blocking/important code issue;
  requested current documentation, partial traceability and factual results, all
  retained. Tuple annotations refined; ordinary eager ORM projections remain
  dictionaries to avoid speculative duplicated data types. No architecture change.
- Documentation and code are Codex-assisted, not the student's personal architecture
  note. No provider call, new criteria, browser/mobile acceptance or concurrency
  success claimed. 380-pixel test remains deferred; CI unchanged/unverified here.
  Stop before creation service. Local commit authorized, no push.

## 2026-11-11 — TP3 checkpoint 2B — transactional student creation

- Initial Git clean at 470a7ef0d9fad59a16179089eaae7bdf6611eae4, main ahead three
  local commits. User authorized 2B only, including a local commit, not a push.
  Scope recorded in docs/CREATION_2B.md before implementation. Approved AC-11,
  AC-13 through AC-21 unchanged; evidence remains partial without HTTP/UI.
- The student's decisions remain student-only creation, canonical Sofia slots,
  half-open intervals and global future quota. Codex proposed the service contract,
  code, tests and documentation, not the student's personal architecture note.
- First refusal test failed because booking_creation did not exist. Implemented
  create_booking(actor, workstation_id, starts_at, ends_at, clock=None), returning
  immutable UTC CreatedBooking. Owner exclusively from the trusted actor, then
  authoritative account reloaded in the transaction. No client owner parameter.
- Data layer owns atomic block, ORM, user then workstation row locks, conflict
  queries and insert. Service reads clock after locks, checks active student,
  station, canonical hours/duration/future, conflicts and quota. Reuses 2A eager
  personal interval and future-count data queries, never a previous offer.
- Known constraint names plus SQLSTATE are translated only after atomic rollback.
  Unrelated integrity errors propagate. Real PostgreSQL insert failures test both
  exclusions and one_hour; positive_interval diagnostic is explicitly simulated
  because zero duration triggers one_hour first with both constraints installed.
- Initial 30 tests passed; extended run had 51 passed and 2 fixture failures:
  constraint-order assumption and create_user's pre-insert full_clean. Fixed the
  test mechanisms, preserving domain assertions and installed constraints.
  Final direct suite: 55 passed in 2.14 s. Refusals compare all business rows;
  checks include stale roles, missing users, clock ordering, quota exclusions,
  offline future quota, cross-lab/partial overlaps and consecutive slots.
- Unchanged coverage runner --postgresql: 231 pytest passed, 1 deselected,
  no skipped tests, 184.09 s; 9 TP1 unittest passed in 17.942 s. Sole deselection:
  test_guard_refuses_unmarked_or_wrong_database, whose SQLite-specific acceptance
  assertion remains unchanged and ran in the historical 1A SQLite suite.
- PostgreSQL coverage: services 168/168 lines, 56/56 branches; new service 65/65,
  22/22; new data access 43/43, 6/6. Global 1009/1086 lines (92.91%) and 246/276
  branches (89.13%). Inventory 45 production files, none missing; thresholds,
  runner and exclusions unchanged, TP1 included. No SQLite 2B measurement.
  Report .local/coverage/a2fa736a234645a98a8e35d58fadad6a/coverage.json.
- Django check and migration drift pass; no migration applied. ex2: 32/32 after
  authorized unsandboxed retry of EPERM on an old local pytest cache folder.
  SQLite/marker/initial migration hashes match previous checkpoint. No operation
  on 5432, seed, new dependency, CI, provider or existing secret. Dedicated new
  profiles remain ignored/untracked, no authorized secret in Git candidates.
- No concurrency claim: only sequential direct tests and lock-order observation,
  not separate simultaneous connections. AC-22/23/24 and final Slice 2 grouping
  remain open; no cancellation, HTTP, UI, MCP or AI added. 380-pixel check deferred.
  One independent read-only custom reviewer found no blocking/important issue.
  Retained its request for final measurements and explicit 2C limits, recorded
  here and in CREATION_2B. No finding rejected, no code correction requested.
  Staged-diff and authorized-secret checks precede the local commit; no push.

## 2026-11-11 — TP3 checkpoint 2C — real PostgreSQL creation concurrency

- Initial Git clean at c2f2673164622dc8e1d01fea7e80841d9c07c4c3, main ahead four
  local commits. User authorized only concurrent AC-22/23/24 service tests and
  a local commit, no push. No approved AC rewritten. Codex wrote the tests and
  guide, not the student's personal architecture note or professor approval.
- Added real transaction=True tests using committed fixtures, independent
  thread-local connections, explicit test DB/5433 guard and distinct backend
  PIDs. Leader holds a real row lock, observer confirms peer's pg_blocking_pids
  and Lock/FOR UPDATE state before releasing leader. User lock for AC-23/24,
  workstation lock for AC-22. All instrumentation is confined to tests.
- Initial run: 3 passed in 4.18 s. AC-22: creation/WorkstationConflict, final 1;
  AC-23: creation/PersonalConflict, final 1; AC-24: creation/QuotaExceeded,
  final 3, including two unchanged initial rows. Four quota intervals disjoint.
  Both worker futures retrieved, SQL/event waits bounded and connections closed.
- Temporarily changed only quota condition 3 to 3000. Real AC-24 then produced
  two creations and four final rows: expected failure assert 4 == 3, 2.36 s.
  PIDs 39972/30392 and actual lock wait observed. Original service bytes restored
  in finally and SHA256 checked; no mutation retained. Ignored raw record:
  .local/quota-mutation-2c.txt. No production correction or schema change needed.
- After exact restoration, all 3 concurrent tests passed in 3.77 s. PIDs:
  AC-22 35268/42832, AC-23 37340/33196, AC-24 10104/35704. Same expected domain
  outcomes and final counts 1/1/3; initial quota rows unchanged. Independent
  observer backend also checked distinct in each case. Raw ignored record:
  .local/concurrency-2c-final.txt. No worker SQL error/timeout accepted as refusal.
- ex2 passes 32/32; diff check clean. Preserved SQLite/marker/initial migration
  hashes and restored creation service hash. No production, CI, dependency,
  coverage policy or migration change retained. Full PostgreSQL regression and
  coverage are measured again, not inferred from 2B. No SQLite measurement here.
- One independent read-only custom reviewer examined synchronization, real
  PostgreSQL wait-chain proof, cleanup, mutation and outcomes. No blocking or
  important finding, no code correction requested, no finding rejected. Scope
  remains these three schedules, not all interleavings, HTTP or cancellation.
  No existing secret read for reporting; local profiles, logs, database and venv
  confirmed ignored and untracked. Stop before 2D, local commit only, no push.
- Final unchanged coverage runner --postgresql passed: 234 pytest passed,
  1 deselected, no skipped tests, in 220.34 s; 9 TP1 unittest passed in 13.697 s.
  Sole deselection remains the unchanged historical SQLite target guard
  test_guard_refuses_unmarked_or_wrong_database, exercised on SQLite in 1A.
  Services 168/168 lines and 56/56 branches (100%); global Python including TP1
  1009/1086 lines (92.91%) and 246/276 branches (89.13%). Production inventory
  unchanged at 45 files, none absent, exclusions/thresholds unchanged. Actual
  PostgreSQL report: .local/coverage/c363ddc75c094bb5bf5b09acafba30ab/coverage.json.
  Ignored raw output .local/coverage-2c-final.txt. No remote CI claim, and the
  380-pixel check remains deferred. Final staged scope: tests and documentation.

## 2026-11-11 — TP3 checkpoint 2D — owner-only idempotent cancellation

- Initial Git clean at 13fd34c01c3f06ef353ddf0fe353cedd701b870e, ahead five local
  commits. User authorized cancellation service/tests and local commit, no push.
  Scope recorded before implementation in CANCELLATION_2D. AC-25/26/27/28 remain
  partial without HTTP/UI. No approved criterion rewritten or renumbered.
- Codex proposed contract/code/tests/docs using the student's validated rules;
  no personal architecture note or final Slice 2 grouping written for them.
- TDD: initial refusal failed with missing booking_cancellation module. First
  implementation passed 19 direct tests in 2.34 s. Extended targeted suite then
  passed 35 tests in 8.69 s (27 direct, 5 concurrent 2D, 3 old 2C scenarios).
- cancel_booking(actor, booking_id, clock=None) returns immutable UTC stored
  cancellation state. Active actor reloaded under user lock, preliminary station
  hint, station lock, booking lock, authoritative owner/state recheck. A changed
  routing key aborts, never takes another lock out of order. Clock is read only
  for a first cancellation and after all locks. Strictly before starts_at only.
- Owner/auth checks precede idempotence. Repetition preserves timestamp, even
  after slot start; offline station does not prevent owner cancellation. Historic
  rows remain; existing read/create services prove slot and quota release.
  No role-only restriction on an active owner whose role changed to personnel.
- Data layer owns ORM/atomic block. Reuses existing user/station locks and
  BookingError/InvalidBookingInput/AuthenticationRequired semantics; new explicit
  errors BookingNotFound, NotBookingOwner, CancellationTooLate, BookingChanged.
  Unrelated write failures roll back and propagate. No HTTP status implemented.
- Extracted existing 2C wait/cleanup protocol to test-only concurrency_helpers;
  checks initial visibility, test DB/5433/autocommit, three distinct backend PIDs,
  pg_blocking_pids + Lock/FOR UPDATE before releasing leader, bounded waits and
  future exceptions/connection cleanup. No production-only test synchronization.
- Observed two cancellations -> one UPDATE and identical result; cancellation
  before quota creation -> both succeed, 4 rows/3 active; creation first ->
  QuotaExceeded then cancellation, 3 rows/2 active. Same station, different owners:
  cancellation first -> 2 rows/1 active; creation first -> WorkstationConflict
  then cancellation, 1 cancelled row. Controlled UTC clocks, no automatic retry.
  PIDs and raw result reference in CANCELLATION_2D/.local/cancellation-2d-tests.txt.
- No migration, dependency, seed, development data, SQLite/5432 operation, CI,
  endpoint, UI, MCP or AI. Regression PostgreSQL coverage and independent review
  follow; no concurrency claim beyond the schedules actually executed.
- One independent custom reviewer examined the current service/data/test changes
  read-only, without another agent or database access. No blocking/important
  finding, no correction requested, no finding rejected. It confirmed ownership
  and active checks before repeat, fresh clock after locks, atomic rollback and
  the five controlled schedules. No universal concurrency or HTTP claim added.
- Final unchanged runner --postgresql: 266 pytest passed, 1 deselected, no skips,
  243.03 s; 9 TP1 unittest passed in 11.495 s. Sole deselection remains historical
  SQLite-specific test_guard_refuses_unmarked_or_wrong_database, unchanged and
  previously exercised on SQLite in 1A. Both added availability assertions pass.
- Actual PostgreSQL coverage: services 220/220 lines, 74/74 branches; cancellation
  service 52/52, 18/18; cancellation data 28/28, 2/2. Global 1089/1166 lines
  (93.40%), 266/296 branches (89.86%). Inventory 47 production files, none absent.
  Existing scope/exclusions/thresholds preserved, TP1 included; no SQLite measure.
  Ignored report .local/coverage/b9b69e05ff13468a949d09869f47d11f/coverage.json.
- Django check tests.settings_postgres: no issues. ex2: 32/32; diff check clean.
  Hashes of SQLite, marker, initial migration and creation service unchanged;
  no migration applied, no 5432/development data intervention. Profiles, local
  reports, database and venv ignored/untracked; no secret read for reporting.
  380-pixel check remains deferred. No remote CI claim. Stop before API HTTP.

## 2026-11-11 — TP3 checkpoint 3 — session/CSRF HTTP booking APIs

- Initial Git clean at 39bb68f3255f75a2713b79b988873050798be4e7, main ahead six
  local commits. Read user's attached scope and applicable instructions. Contracts
  documented before code in HTTP_API_3: four HTTP contracts through three views,
  no application UI, model/migration/dependency/CI/MCP/AI or demonstration seed.
- New routes/bookings calls existing availability/history/create/cancel services
  unchanged. Session is the only actor source; strict JSON shapes reject client
  owner fields, no route ORM. Explicit UTC serializers select only allowed fields.
  Existing HTTP session forms remain unchanged except targeted CSRF JSON handling
  for the new URL names; HTML form failures remain HTML when requested.
- HTTP adapters map known errors to 401/403/404/409/422; malformed JSON 400,
  unsupported media 415, unsupported method JSON 405 with Allow. Unexpected
  exceptions remain generic JSON 500 and log class only, not SQL/messages/trace.
  Middleware CSRF remains active and can return 403 before authentication; tests
  separately prove anonymous POST 401 with valid CSRF and 403 without valid token.
- First integration: 46 passed, one fixture failure because Django test client
  omitted Content-Type for an empty body, obtaining 415 instead of malformed JSON
  400. Set the actual WSGI header in the test; preserved status expectations.
  Completed direct HTTP suite: 50 passed in 1.17 s with real PostgreSQL services,
  session backend and enforced CSRF. Only faults injected are DatabaseError for
  safe 500 and an actual post-routing change for real BookingChanged rollback.
- Tests cover final row owner/count, create/conflicts/quota/personnel, history
  privacy/empty reads, owner cancellation/repeat timestamp/offline station,
  invalid payload/media/date/methods, winter/summer input UTC, expired/inactive/
  missing sessions and old cookie after logout. Refusals compare all business rows.
  No acceptance of SQL exception or mocked domain decision as correct behavior.
- SPEC records technical Slice 2 scope using existing ACs, without rewriting or
  inventing criteria. Personal final grouping is not presumed validated; the
  student's architecture section stays blank. Guide lists paths for their note.
  Code/contracts/tests/docs assisted by Codex, not student personal prose or
  professor approval. Stop before interface, authorized local commit only, no push.
- Final unchanged runner --postgresql: 316 pytest passed, 1 deselected, no skips,
  121.28 s; 9 TP1 unittest passed in 13.323 s, including prior TP2/2C/2D regressions.
  Services 220/220 lines and 74/74 branches (100%); new booking_http 83/83 and
  20/20, new bookings 32/32 and 4/4. Global 1206/1283 lines (94.00%), 290/320
  branches (90.625%). Inventory 49 production files, none absent; unchanged scope,
  exclusions and thresholds, TP1 included. No SQLite measurement. Sole unchanged
  deselection remains SQLite-specific test_guard_refuses_unmarked_or_wrong_database.
  Report .local/coverage/f46e825e705047a2853571099f8f6381/coverage.json.
- One independent read-only custom reviewer found no blocking/important issue.
  Initial missing-cache CSRF concern withdrawn after checking existing
  @never_cache on csrf_failure and passing tests. No production correction
  requested, no valid finding ignored. README now distinguishes historical TP2
  SQLite launch from current PostgreSQL booking APIs; no migration run by this task.
- Django check tests.settings_postgres passed, ex2 32/32, diff check clean.
  SQLite/marker/initial migration hashes unchanged; all services/data, CI,
  dependencies, TP1 and coverage policy unchanged. No existing secret read for
  reporting; private profiles, local logs/reports/database and venv ignored and
  untracked. No remote CI result, provider call or browser claim; 380-pixel check
  remains deferred. Staged scope is limited to HTTP adapters, tests and docs.

## 2026-11-11 — TP3 checkpoint 4 — student booking/cancellation journey

- Initial Git clean at 514b8ad618756c54d97eb31ec52d8cea865bd22c, ahead seven local
  commits. Read attached request, AGENTS, SPEC, UI checklist and prior guides.
  Announced short plan: catalogue, availability and personal history on /labs,
  existing HTML/CSS tokens and fetch/session/CSRF APIs; no business rule duplication.
- Added booking.mjs controller, catalogue selection callback, explicit confirmation,
  safe text nodes, Europe/Sofia display, statuses/retries, own history/cancellation,
  no reload after success. Global mutation guard prevents double submissions;
  network/invalid successful response keeps outcome uncertain and blocks mutations
  until explicit state consultation. No automatic POST retry or login redirect.
- API, services, ORM, schema, migrations and provider logic unchanged. No Google,
  AI, MCP, CI, dependency or deployment added. Existing MIME correction and v2
  root module URL preserved; imported module also tested as text/javascript.
- Tests: first 19 Node passed; extended final suite 22 passed. First process launch
  blocked by sandbox spawn EPERM, authorized rerun worked. Initial JS coverage
  failed at 57.34% because versioned/unversioned imports created two instances
  reported as the same file by Node. Matched tests to browser's ?v=1 import,
  without excluding production or reducing threshold. Final loaded-module lines
  98.18% (booking100%, labs93.02%); simulated DOM/network, not whole frontend/UI.
- Django targeted tests: 11 passed in 5.74 s, real protected HTML/labels/CSRF and
  MIME principal/import, preserving previous cache regression. Full unchanged
  PostgreSQL runner: 319 pytest passed, 1 deselected, no skips, 97.49 s; 9 TP1
  unittest passed in 6.488 s. Services 220/220 lines and 74/74 branches; global
  1206/1283 lines (94.00%), 290/320 branches (90.625%), TP1 included. Inventory
  unchanged49 production Python files; thresholds/exclusions unchanged. Sole
  deselection remains historical SQLite target guard, unchanged and tested1A.
  Report .local/coverage/ae6753610bc846d49bd53f3789b65ff4/coverage.json.
- One independent custom reviewer, read-only, found no blocking/important defect.
  Retained minor improvement: disable history refresh after 401 and return early;
  extended session test proves no repeated GET. Retained grouping nuance: final
  delivery scope AC11/13-28 per user's explicit instruction, not a claim every AC
  or personal writing was validated. No valid finding ignored, no second review.
- Computer-use skill used only for inventory so far: Edge accessible. Initially
  no implicit demonstration preparation. User then explicitly authorized dedicated
  PostgreSQL development demo on5433, preserving all existing data/passwords.
  Verified current_database/port/current_user, transactionally created one DEMO UI
  laboratory, two operational workstations and student-ui@demo.example (active
  student, not staff/superuser), initially with unusable password. Existing rows,
  roles/passwords not modified; existing user query omits password field. No SQLite
  transfer, no5432 intervention. Interactive masked changepassword command and
  explicit PostgreSQL runserver command supplied to user, never requested password.
- User has not yet confirmed Edge login; requested commands again and received
  them. Browser journey remains pending; 380 pixels explicitly deferred. No
  browser outcome attributed to user or Codex. Data prep is observed by Codex;
  password entry/login are user actions not assumed completed. UI checklist boxes
  stay unticked. Guide STUDENT_UI_4 lists remaining manual steps and three
  architecture questions for later; student's personal Architecture stays blank.
- Docs/code/tests assisted by Codex, not wholly personal student work. Local
  commit authorized after checks; no push. Finalization continues while awaiting
  user confirmation required before browser trials.
- Final pre-browser checks: Node syntax and Django check passed; ex2 32/32;
  git diff --check clean. Latest protected-template/MIME targeted repeat:
  11 passed in 7.33 s. SQLite/marker/initial migration hashes unchanged; no
  Python application, services/API, dependency, CI, coverage-policy or TP1 change.
  Private profiles/local databases/venv untracked. Local commit not yet created:
  awaiting user's explicit Edge-login confirmation, then real observations and
  final documentation before the already authorized local commit. No push.

### 2026-11-12 — checkpoint 4, real Edge journey

- User confirmed personal password entry and login as student-ui@demo.example;
  no password requested, read or entered by Codex. Then explicitly authorized
  availability, creation, own history and cancellation on dedicated demo data.
- Computer-use skill: direct tab host unavailable; native Edge window used after
  user brought /labs to foreground. Calendar selected 2026-11-13; native date
  text automation was ineffective, not interpreted as an application defect.
- Codex observed the dedicated laboratory and empty history, then 20 slots.
  Selected Poste A 08:00–09:00 Europe/Sofia; explicit confirmation appeared
  before creation. Confirmed once: success, one future history entry, 18 slots.
  Cancelled once: cancellation success, same history entry now Annulée, 20 slots.
  No manual reload. Personal overlap explains the two unavailable candidates
  after creation; this interpretation is separate from the visible counts.
- No browser HTTP status or Console evidence collected for these mutations.
  Screenshots displayed by the tool were not archived. No claim of browser
  testing for refusals, errors, keyboard journey, contrast or widths; 380 pixels
  explicitly deferred. Automated results above reused: code/config unchanged.
- SPEC, guide, README, UI evidence and agent instructions updated by Codex with
  observed facts, student actions and limits distinguished. Student architecture
  note and comprehension remain personal, not supplied or validated here.
- User granted future TP3 normal publication and PostgreSQL CI alignment after
  final checks, preserving controls and history. Current checkpoint concludes
  locally; no CI modification, push, provider call, new dependency or migration.
- Final documentary rerun initially hit sandbox EPERM on a pytest temporary
  directory; authorized rerun passed ex2 32/32. git diff --check passed. SQLite
  SHA256 still matches the pre-checkpoint value; .venv, demo DB and local reports
  ignored, none tracked under .local/data/.venv. No new production code change
  after the previously measured tests/coverage and independent review.

### 2026-11-12 — reservation Slice 2 finalization and publication

- Initial state clean at 64bc12a1f0c0ee8b6a5af44111fceaa6afe74e07, main eight
  commits ahead of origin/main; fetch confirmed 8 ahead, 0 behind. User explicitly
  authorized browser/error/keyboard/contrast checks, CI PostgreSQL alignment,
  targeted fixes, commits and normal pushes, preserving existing history/data.
  No new IA/MCP feature, provider call, deployment or 380-pixel check authorized.
- Plan: record browser facts, source current TP3/project requirements, finalize
  existing-AC grouping and personal-note pointers, align ephemeral PostgreSQL CI
  and complete npm launcher, run tests/gates, one read-only custom reviewer,
  commit/push and inspect Actions on the exact published SHA. Personal note and
  comprehension are not delegated; a green delivery CI does not close TP3.
- Computer-use skill used in native Edge. User interaction interrupted keyboard
  input; stopped and resumed after explicit AVAILABLE confirmation. Observed
  visible skip-link/focus and keyboard creation/cancellation for demo Poste A,
  2026-11-13 08:00–09:00 Europe/Sofia. History 1 cancelled -> 2 entries with one
  future -> 2 cancelled; slots 20 -> 18 -> 20. Existing entry preserved, new one
  retained cancelled. This is the core action at keyboard, not a fresh combined
  sign-in/action/sign-out test; previous TP2 user keyboard reports stay separate.
- DevTools Offline made availability fetch fail with a readable network message.
  Restored No throttling; explicit retry showed HTTP200 and 20 slots. Closed
  DevTools. Actual backend was not stopped; no claim of manual 201/409/401/403.
  CSS overview observed actual palette; Python WCAG luminance ratios range
  7.463:1 to 15.520:1 for application text pairs. Detailed values/tool/limits in
  docs/SLICE2_FINALIZATION.md. No screenshots archived, widths still unverified,
  380 explicitly deferred. No demonstrated application defect or production fix.
- Official TP3 and project pages reconsulted by curl after Web/sandbox failure,
  dated 2026-11-12. Sources and requirement matrix recorded in the guide. Important
  ambiguity: conditional model/MCP prose versus unconditional ex3 checks; no
  automatic acceptance inferred. Google, model, project MCP, personal architecture
  and remaining project UI/deploy requirements remain outstanding.
- Complete npm test now runs PostgreSQL application/concurrency, the unchanged
  SQLite guard on its own original migration/schema in memory, TP1 and all Node
  tests. tools/run_tests.mjs selects the local venv or CI Python, propagates the
  first failure. A direct launcher test proves command selection and fail-fast.
  No production Python inventory/coverage-policy change or booking migration edit.
- CI test/coverage each get isolated postgres:16 service and fresh restricted test
  role/database, verify empty public schema, apply migrations, check model drift,
  run application/concurrent tests and real Python coverage. .local CI profile
  created exclusively with mode0600. Public ci-only fixture credentials belong
  only to disposable services, not the user's profiles. MCP/spec and conditional
  Docker steps retained. Empty-schema CI proof awaits actual remote run.
- Pre-publication inspection caught the container-port distinction: a host mapping
  5433:5432 would leave inet_server_port() at5432 and fail the unchanged concurrency
  identity guard. Services now set server PGPORT5433, map5433:5433 and healthcheck
  that port, consistent with PostgreSQL16 official postgres documentation.
- Local final npm test: 319 PostgreSQL pytest passed, 1 deselected in45.64s;
  that exact SQLite-specific test passed separately in0.17s; 9 TP1 tests passed
  in0.747s; 23 Node tests passed. No pertinent test silently skipped.
- PostgreSQL Python coverage rerun: 319 passed, 1 deselected in62.09s and 9 TP1
  in7.473s; services220/220 lines74/74 branches100%; global1206/1283 lines94.00%,
  branches290/32090.625%. Existing49-file production inventory/exclusions and
  thresholds preserved. Report .local/coverage/af6059615acd4319bbe4eda12f280239/coverage.json.
  No fresh SQLite application coverage claim. Separate Node coverage98.18% lines,
  90.91% branches for loaded src modules, not visual/whole frontend coverage.
- MCP12/12, Django check/model drift and pip check passed. ex2 initially31/32
  because line-wrapped grouping prose was treated as extra criteria; fixed the
  metadata paragraph format, without changing criteria/checks; final32/32.
  git diff --check passed. Sandbox Node spawn/scandir EPERM required authorized
  reruns. No threshold or check weakened.
- ex3 unchanged:11/18, exit1; Windows npm ENOENT inside its shell:false helper,
  future ACs absent, model fallback/project MCP/architecture genuinely absent.
  IA positives are heuristic false positives. Strict collected-title comparison
  also finds AC1/2/4 absent despite substring successes. Full list/limitations in
  guide. It is not replaced, made green or silently treated as TP3 acceptance.
- SQLite hash unchanged; sensitive/local profiles, demo DB/backup and .venv
  ignored and untracked, no secret contents read for audit. Existing 5432 and
  business data untouched except the explicitly authorized demo booking cycle.
  Docs and formulations assisted by Codex, not student-authored architecture.

### What the agent did that I did not ask for — assistant inventory for student review

This is Codex's comparison aid, not a claim that the student personally read and
approved the whole feature diff. User must supply their own assessment.

- Supporting files beyond the named workflow: local composite action and npm
  launcher/test, needed to run real PostgreSQL tests consistently in both jobs.
- Test-only SQLite settings/migration alias added to keep the original guard's
  assertion running without adapting PostgreSQL booking constraints to SQLite.
- Extra test edits during checkpoint4 included the exact versioned JS import to
  avoid duplicate Node coverage instances, and a 401-history-refresh assertion
  after reviewer feedback. Logged in that checkpoint, no rule assertion weakened.
- No dependency, application feature, existing migration, model/provider/MCP
  implementation or user's architecture text added during finalization.
- One custom read-only reviewer completed after tests: no blocking/important
  finding. Retained optional improvement: explicit synthetic test proving the
  local Windows .venv Python is preferred by the npm launcher. Targeted Node
  rerun passed1/1 after that assertion; no production change or second review.
  No finding rejected. Remote ephemeral PostgreSQL/CI remains to observe.
- Normal push completed to2011d95d6d711dd0ee84d60af7eb2135801ae9de, preserving all
  eight checkpoint commits. Actions run43262915943 completed all four jobs
  successfully. GitHub connector fetched job results and decoded logs, rather
  than inferring success from local checks. Public curl listed push runs because
  the available connector listing is limited to pull-request-triggered runs.
- Both test/coverage logs prove zero public tables, dedicated test identity on
  serverport5433, role flags allfalse, all migrations including0001/0002/0003
  applied, no model drift; PostgreSQL16.15. test job:319PG passed/1deselected,
  separate1SQLite,9TP1,23Node. coverage:319PG/1deselected,9TP1; services220/220
  lines74/74branches100%, global1207/1283lines94.08%,291/320branches90.9375%;
  loaded JS lines98.18%. These Linux values are distinct from Windows94.00%.
  Docker build step skipped by existing condition; no other job skipped/failed.
  Expected constraint errors in server logs correspond to negative tests.
- Recorded publication proof in docs/README/SPEC. No post-push code/config fix
  needed. The documentation-only follow-up must get its own remote CI check;
  no success inferred in advance. TP3 remains incomplete for the listed personal,
  manual and future-project/model/MCP requirements; 380 pixels still deferred.

### 2026-11-12 — real HTTP observations, preparation

- User explicitly deferred personal architecture coaching/writing/review and
  authorized the four real HTTP scenarios, a second nonprivileged demonstration
  student if needed, documentation and later normal publication. No claim of
  personal understanding or TP3 closure. No IA/MCP/Google/staff/deployment work.
- Initial Git clean on 8910a6c454e91d321d9d0e9ddc8236f8908974b0. Read applicable
  AGENTS, finalization guide and only session/API/model fragments needed here.
  No full audit, test rerun or CI change.
- Read-only process identification initially denied by sandbox; authorized rerun
  confirmed port 8000 listener PID 40884, launched through this repository's .venv
  Python wrapper PID 24124 with src.config.postgres, --insecure and --noreload.
  Windows venv wrapper's child uses the base Python executable; command line
  remains the project venv invocation. PostgreSQL identity read explicitly:
  lab_booking_1a / lab_booking_1a_dev / 5433. No process stopped or restarted.
- Only dedicated student-ui account existed. Created student-http@demo.example,
  id 2, active student, no staff/superuser privileges, no usable initial password.
  Existing user query selected only non-secret identity/role/status fields; no
  existing password read or modified. Lab/stations and two historical bookings
  preserved. Masked changepassword command and separate InPrivate sign-in supplied
  to user; waiting for that authentication intervention, no credentials requested
  in conversation. No cookie/CSRF/profile values printed or recorded.
- Real unauthenticated GET http://127.0.0.1:8000/api/bookings via standard-library
  urllib, outside pytest/Django Client/mocks: 401, application/json, only the
  Connexion requise error. All Booking fields compared from actual PostgreSQL
  before/after: two rows, identical. Safe report .local/http-manual-401-20261112.json.
  No 201/409/403 observation claimed yet. Guide/SPEC updated with pending states.
- SQLite SHA256 remains 983e3847e7495dff0652b1cf7cb7928c02d0c075db19f113f1dba04f4dcbdcaa.
  No 5432 intervention, migration, new dependency or provider call. Codex-assisted
  documentation; personal Architecture section remains untouched. No publication
  of this incomplete observation batch yet.
- Preparation documentation checks: ex2 passed 32/32, git diff --check clean.
  Application code unchanged, so no full test/coverage rerun. No independent
  reviewer triggered for this incomplete documentation-only preparation.

### 2026-11-12 — real HTTP observations, execution after authentication handoff

- User confirmed second student logged into Edge InPrivate, original session
  still open. Initial Git has only the five documentation changes from the
  preceding preparation turn; preserved and completed them. No application edit.
  Personal note/coaching/review remain deferred, no understanding validated.
- Computer-use skill, native Edge windows. Codex independently observed /labs
  as student-http in InPrivate and student-ui in the normal window. No login or
  password entry automated. No credential, cookie, CSRF or profile value printed,
  copied or saved. No session manufactured through Django Client or database.
- In the private Console, real GET availability for lab 1 on 2026-11-13 returned
  200, 20 slots; picked its first actual candidate: Poste A id 1, 06:00–07:00 UTC,
  08:00–09:00 Europe/Sofia. Real POST /api/bookings JSON with those three fields,
  same-origin session and CSRF from that page's hidden field returned 201.
  JSON: booking id 3, created_at 2026-11-12T17:39:04.082188Z, cancelled_at null.
  Separate PostgreSQL 5433 read: 2 -> 3 rows, owner id 2, exactly one added, all previous
  row fields unchanged. Snapshot .local/http-manual-after-create.json.
- Explicit duplicate POST from same session/body/CSRF: 409, message Ce poste est
  deja reserve sur ce creneau (actual accented body in guide). 3 -> 3, every Booking
  field equal before/after. No raw SQL failure, timeout or false success.
- In normal window as student-ui id 1, real POST /api/bookings/3/cancel with {}
  and that session's own CSRF: 403, Tu ne peux annuler que tes propres reservations.
  Actual accented response in guide. Message is NotBookingOwner, distinct from
  csrf_failure security message. DB confirms 3 -> 3, all fields identical, row 3
  owned by id 2 and still not cancelled. No security control bypassed.
- Final eligible cancellation from owner student-http, same endpoint/{} and its
  own CSRF: 200, row 3 retained, cancelled_at 2026-11-12T17:44:39.439591Z. Only this
  field changed; old rows 1/2 and all other row 3 fields unchanged, total 3. After
  explicit page reload, Codex observed one historical row Annulee/Poste en service
  in private UI. Console requests bypass the UI controller, so no automatic UI
  refresh claimed. Native clicks attempted did not show an observable effect in
  the tool; reload used, no demonstrated application defect inferred. DevTools
  closed, both authenticated sessions retained. Tool images not archived.
- Supplementary anonymous POST checks: fresh in-memory urllib CookieJar, real
  GET /login CSRF, no authenticated session; POST creation and POST cancel each
  returned 401/Connexion requise. All three Booking rows identical before/after.
  Cookies/CSRF existed only in process memory, never printed/persisted. Safe
  results .local/http-manual-anonymous-posts.json. This completes the requested
  live HTTP statuses; not substituted automated pytest results or mocks.
- No API defect demonstrated; five docs only, no new app/helper/CI code, test
  weakening, dependency, migration, provider call, data transfer or 5432 action.
  SQLite SHA256 still matches the pre-task value. No booking deleted. Note and
  personal diff review, UI widths/accessibility remainder, absent IA/MCP/Google
  and professor ambiguities remain explicitly open. Codex-assisted evidence,
  not student-written architecture or whole TP3 acceptance.
- Final documentary checks: ex2 passed 32/32; git diff --check clean; no app,
  dependency, migration or CI diff. Existing local profiles, snapshots and demo
  database remain ignored and untracked; SQLite hash unchanged.
- One independent read-only custom reviewer before the milestone evidence
  commit: no blocking/important finding, snapshots confirm stated DB effects.
  Retained optional readability improvement: separate routes/status codes and
  adjacent numbers in the new evidence paragraphs. No finding rejected. No
  full local test rerun for documentation alone; verify CI after normal push.

## 2026-11-17 · Project MCP integration plan (not implemented)

- User requested only the next MCP integration plan, superseding the previous
  stop-before-MCP instruction for planning alone. Authentication and construction
  remain subject to review; no implementation, installation, commit or push.
- Initial Git state: clean main at 5d830b1c15c60775c548dae81dc89c76c9fc2fb9.
  Read AGENTS, relevant SPEC sections, shared service contracts, TP1 dispatch,
  HTTP serialization, Django's installed session/auth code and finalization guide.
- Web reader failed; curl succeeded for the current TP3 and project guides.
  Sections and source links are recorded in docs/MCP_PROJECT_PLAN.md.
- Codex proposed ordinary session delivery through a masked local launcher and
  inherited environment, per-call Django validation, an opt-in six-tool mode,
  direct reuse of shared services and three testable substeps. These are assistant
  proposals, not student-authored architecture or already approved mechanisms.
- No existing cookie, credential or secret file read; no database query/mutation,
  provider call, migration, dependency or CI change. No repeated HTTP evidence.
  Personal note/review, deferred UI checks and other outstanding requirements
  remain outstanding. AGENTS updated only to reflect the planning authorization.
- Documentary checks: ex2 32/32 after sandbox EPERM on an existing pytest cache
  directory and authorized rerun; git diff --check clean after spacing correction.
  No application/DB test rerun for this planning-only change; historical ex3
  diagnostic retained, not rerun or represented as passing.
- One independent read-only custom reviewer examined the authentication proposal.
  Retained finding: specify the user's manual local transfer of their own cookie
  into the masked launcher; plan now makes that handoff and clipboard clearing
  explicit. No finding rejected. Client-specific launcher compatibility remains
  to verify during construction; no functional proof is claimed by this review.

## 2026-11-17 · MCP substep 1 — Django session authentication and project mode

- User approved the plan and authorized only bootstrap/authentication, tests,
  documentation and one local commit. No tools, real-token handoff, new dependency,
  provider call, CI change or push. Preserved the preexisting plan/AGENTS/log edits;
  those relevant documents are included with the checkpoint, not discarded.
- Initial HEAD 5d830b1c15c60775c548dae81dc89c76c9fc2fb9; initial changes limited to
  AGENTS.md, AGENT_LOG.md and untracked docs/MCP_PROJECT_PLAN.md.
- Tests first: after resolving a stopped dedicated cluster, the absent-session
  test failed with ModuleNotFoundError for the missing service. Implemented
  Django get_user with a session-only context and read-only SessionStore. Genuine
  sessions then exposed a subclass signing-salt mismatch; preserve Django's
  original backend salt. Targeted rerun: 28/28. No test weakened for this correction.
- Per-call session lookup verifies Django signatures, expiry, allowed backend,
  current user/activity and session auth hash. Reject privileged sessions and
  flush/cycle attempts, including secret fallback rotation. No actor cache,
  silent renewal or owner selected from tool arguments. Runtime adapter exists
  but no project RPC dispatch/tool is delivered yet; AC-37/38 only partial.
- Real stdio tests: --project with explicit PostgreSQL test settings, no inherited
  session; unchanged two-tool catalogue, handshake/notification/course call.
  Default Python -S works despite an invalid Django settings module. Invalid
  project configuration and CLI arguments return safe diagnostics without traces.
- Test infrastructure initially timed out; pg_ctl status reported no dedicated
  server. Started only the existing cluster on 5433 with local_postgres.py start,
  no init/provision operation or 5432 intervention. Runtime tests use the existing
  test-profile loader, never a manual profile dump or a real browser cookie.
- Incident: pytest's initial long database-failure traceback exposed the local
  PostgreSQL test-role password. Its value is not repeated in tracked documents;
  subsequent commands use short tracebacks. No password rotation performed or
  falsely claimed; this separate follow-up must be considered with the user.
- Coverage runner --postgresql: 347 passed/1 SQLite-specific deselection, 9 TP1
  passed; services 227/227 lines and 76/76 branches, global 1282/1360 lines
  (94.26%), 304/336 branches (90.48%). New production modules/TP1 included,
  inventory and exclusions/thresholds unchanged. The -S autonomy subprocess
  emits a coverage no-data warning by design; other TP1 processes are measured.
- Other checks: 23 Node tests, MCP 12/12, ex2 32/32, Django check clean. Node
  sandbox spawn EPERM resolved by authorized rerun. No new CI/deployment proof.
  Personal note/review, deferred UI checks, four MCP tools and client handoff
  remain open; no student understanding or completed TP3 claimed.
- The one PostgreSQL deselection is still asserted separately with
  tests.settings_sqlite_legacy: 1 passed (after a sandbox temp-directory refusal
  and authorized rerun). Demo SQLite SHA256 unchanged between the recorded
  pre-final checks and final check. Ignore checks confirm local profiles,
  .venv, Gemini env and demo database remain ignored; no values printed.
- One read-only custom reviewer retained two findings: convert raw DB errors
  at the MCP authentication boundary to a dedicated safe technical exception
  (without displayed chaining), and clarify that settings override is for test
  processes. Both addressed; no finding rejected. Added a regression checking
  that an injected synthetic driver detail cannot appear in rendered exception
  output. Final targeted tests and coverage rerun after this correction.
- Final post-review PostgreSQL coverage: 348 passed/1 SQLite-specific deselection,
  9 TP1 passed; services remain 227/227 lines and 76/76 branches. Global Python
  1287/1365 lines (94.29%), branches 304/336 (90.48%), all production included.
  Report .local/coverage/7be6fdc11fd446d3991a98ccd735bd84/coverage.json.
  No repeated reviewer or CI change; ex2 32/32 and diff whitespace check clean.
- Final targeted run after review: 29 passed. Staged exactly the 13 related
  files, including the preserved approved plan and earlier planning log entry;
  no unrelated change or ignored local profile/database added. Local commit
  only, no remote publication authorized for this substep.

## 2026-11-17 · MCP substep 2 — authenticated reads and credential incident closure

- Initial HEAD aa536364f779091855bfaa43cbf2d5af206467b3, clean working tree,
  main one commit ahead of its tracking reference. User authorized rotation of
  only the exposed local test-role password if not previously completed, then
  two read tools, tests/docs/review/local commit. No push or mutation tools.
- Checked existing evidence: no password rotation had been performed. Ran the
  targeted tool once against 127.0.0.1:5433 as lab_booking_1a_test itself, no
  bootstrap/dev credential read. Verified cluster/base/role and SQL logging
  settings, generated a random replacement, sent a client-side SCRAM verifier
  and updated only the protected test profile in place. New connection accepted,
  previous password explicitly rejected; Windows SDDL unchanged before/after.
  No password in arguments/output/logs. Ignored non-secret receipt:
  .local/postgres-test-password-rotation.json; tool now refuses to repeat.
- pytest.ini now defaults to short tracebacks without disabling a test/check.
  Synthetic failing-connection subprocess confirms no credential argument in
  default output; fake driver errors are not printed by the rotation CLI or
  MCP boundary. Four incident-safety tests passed without another real rotation.
- Tests first: real stdio catalogue expected four tools and failed on the two
  absent reads. Added project_tools.py, dispatched only in --project. Each call
  uses current_actor then exactly booking_reads.list_available_slots or
  list_personal_bookings. No ORM/data-layer/HTTP imports in the tools, no actor
  from user/owner arguments, no project create/cancel tool.
- Real subprocess tests use committed isolated PostgreSQL fixtures and Django
  sessions, fixed January 2030 clocks, bounded reply queues and guaranteed child
  cleanup. Cover catalogue/schemas, owner-only history, auth absence/invalidity,
  revocation within one process, invalid inputs, missing lab, empty results,
  retained cancelled/offline state, coherent text/structured output, parity
  against HTTP/direct services and no Booking/Session mutation (digest snapshots).
  Initial targeted run 46 passed, then added direct-service and error cases.
- Full PostgreSQL coverage: 368 passed/1 historical SQLite deselection, 9 TP1
  passed. Services 227/227 lines + 76/76 branches, global 1403/1489 lines (94.22%)
  + 324/360 branches (90.00%). project_tools.py 55/55 lines,12/12 branches.
  All production including TP1 and the rotation tool remains inventoried;
  exclusions/thresholds unchanged. Report 9bd86211b24e45888159b852f05f30d6.
- Other checks: historical SQLite guard 1 passed on its isolated test settings;
  23 Node tests, MCP12/12, ex2 32/32, Django check and whitespace diff clean.
  No CI changes or new remote results. No demo data/SQLite migration, 5432 access,
  dependency, provider call or real user session. No user architecture note
  written, deferred UI checks not upgraded. AC-37/38/39 remain partial reads;
  final-client handoff and both mutating project tools remain future work.
- Required independent read-only custom reviewer ran once. Retained important
  finding: generic RuntimeError was insufficient to reproduce the original
  psycopg traceback leak. Replaced it with actual psycopg.connect to a reserved
  non-listening loopback port and synthetic credentials. Default pytest output
  hides the fake value; forcing --tb=long reproduces it in captured memory only.
  No active database or real secret used. Retained improvement: reject an unknown
  adapter name explicitly, with a test proving no read service is called.
  No finding rejected. Post-review targeted suite: 50 passed; full PostgreSQL
  coverage rerun. Rotation was not repeated, remaining client/UI limits unchanged.
- Post-review final coverage: 369 PostgreSQL tests passed, 1 historical SQLite
  guard deselected, 9 TP1 passed; services 227/227 lines and 76/76 branches (100%).
  Global 1405/1491 lines (94.23%), 326/362 branches (90.06%); new read adapter
  57/57 lines and 14/14 branches. All production and existing exclusions kept.
  Report .local/coverage/f33f2ba1e98247a7af487d4abe214cac/coverage.json.
  Demo SQLite SHA256 unchanged from task start; local profiles, receipt, .venv
  and Gemini env remain ignored and untracked. No real session/client validated.

## 2026-11-17 · MCP substep 3 — booking and cancellation adapters

- Initial HEAD 4bbbfd5a1ee2afe6cb642c5ca3f17cb7feb9c339, clean working tree,
  main two commits ahead of its tracking reference. User explicitly authorized
  adding book_slot/cancel_booking, tests/docs/review and one local commit only.
  Existing test-password incident was already treated; no rotation repeated.
- Read applicable AGENTS, relevant SPEC contracts/AC-37/38/39, approved plan,
  auth/read guides and creation/cancellation services. Business services, data
  layer, dependencies, migrations and CI remain unchanged. No real-token handoff,
  browser cookie, provider call, deployment or demo preparation.
- Tests first: real stdio catalogue failed with four tools instead of six.
  Added only the project adapter's two mutations. Every call reauthenticates;
  exact argument shapes/positive IDs/aware timestamp syntax are checked there,
  then existing create_booking/cancel_booking functions decide and transact.
  No application ORM/SQL/data-layer/HTTP imports in the tool handlers.
- Results use identical structuredContent and JSON text, no owner ID in the
  success DTO. Explicit known business errors become safe tool errors, unknown
  failures generic InternalError. No exception text or private driver detail.
- Descriptions request confirmation; annotations mark creation non-idempotent,
  cancellation idempotent after first transition and destructive. These are
  hints, not proof of human consent. No automatic transport retry implemented;
  read personal history before any fresh decision after a lost response.
- Targeted tests: first 61 passed, then strengthened boundary, timestamp and
  direct write-count assertions; final targeted command 92 passed. Real stdio
  tests cover 14 creation and 8 cancellation parity cases against HTTP with
  actual CSRF checks and equivalent initial rows on the dedicated PG test DB.
  Generated creation IDs normalized only for comparison; each MCP ID/owner is
  independently checked in persisted rows. Refusals compare Booking/Session
  digests; cancellation retains its row and only changes cancelled_at.
- Repeated cancellation is tested twice in one stdio process, and after the
  slot start for an already cancelled row. A separate direct adapter test wraps
  data.mark_cancelled and observes one write across two calls (not claimed as
  stdio SQL instrumentation). Foreign cancelled row still refuses its non-owner;
  offline station cancellation allowed. Missing/invalid/revoked sessions refuse
  both mutations without state changes; extra user_id/owner_id are refused.
- Full PostgreSQL regression/coverage launched, including existing concurrency
  tests; no new concurrent ordering through MCP claimed. Other checks already
  observed: 23 Node passed, TP1 MCP12/12, isolated historical SQLite guard1 passed,
  Django check clean, ex2 32/32 and whitespace diff clean. Results are local;
  no remote run or complete TP3 acceptance inferred.
- Current guide docs/MCP_MUTATIONS_3.md prepares only the future final-client
  procedure. No launcher built or client/provider run; personal note/review and
  deferred UI checks stay pending. All draft wording/code assisted by Codex,
  not represented as student-authored architecture or validated understanding.
- Full run completed: 411 PostgreSQL passed, 1 historical SQLite-only guard
  deselected, 9 TP1 passed. Coverage services227/227 lines +76/76 branches (100%),
  global1438/1524 lines (94.36%) +342/378 branches (90.48%), project adapter90/90
  lines +30/30 branches. Scope/inventory/thresholds/exclusions unchanged.
  Report .local/coverage/083c4a5190894e708dc38a20957320df/coverage.json.
- Collected test titles now carry exact AC-37/38/39 and relevant business AC IDs
  via parameter ids, not only underscored Python names. No AC added, renumbered
  or rewritten. Assertions preserved/strengthened with retained cancelled history;
  read test catalogue expectations updated to six only in project mode.
- One independent read-only custom reviewer: no functional/security blocker.
  Retained requirement to finish the final targeted rerun: it completed 92/92;
  strengthened catalogue/schema assertion then passed 1/1. Retained obsolete
  runtime docstring finding: corrected module/current_actor and bootstrap-test
  docstrings only. No finding rejected. Production behavior unchanged since
  the full coverage run; test assertions/titles were strengthened, not weakened.

## 2026-11-17 · MCP finalization — client launch and publication

- Initial HEAD 524370db1f0b4e7b89d6c291d3ecda2fcc37851a, clean main, three MCP
  commits ahead. Fetch confirmed origin/main is an ancestor (0/3 divergence).
  User authorized MCP finalization, scoped CI changes and normal publication;
  no provider, Google, deployment or unrelated feature. Rotation not repeated.
- Identified installed Gemini CLI package0.65.0. Read its bundled CLI mcp/list
  implementation and MCP configuration/environment docs, not auth credentials.
  Existing repo config still launched TP1; updated only its command/args/cwd/env
  to direct Windows .venv/server.py --project, explicit src.config.postgres and
  a LAB_BOOKING_MCP_SESSION placeholder. Context AGENTS.md preserved.
- Actual Gemini CLI entrypoint ran mcp list with isolated home/settings, empty
  diagnostic dotenv and a generated fake token in child environment only. Node
  guard denied external networking; embedded data URLs allowed. Final receipt:
  exit0, Connected, right venv/cwd/profile, fake-token forwarding true, protocol
  stdout only, server stderr empty, no token leak, no personal dotenv read and
  zero external network attempts. Methods initialize/initialized/ping only.
- Diagnostic failures retained: preload Windows path corrected, new fake folder
  initially untrusted, overly strict guard blocked a data URL. Wrapper prototypes
  using exec replacement / child relay timed out; direct venv command succeeded.
  Prototypes and test text preserved only as ignored operational artifacts in
  .local/mcp-client-probe, not production or publication files. No app Python,
  rule, dependency, migration, coverage inventory/exclusion/threshold changed.
- This is a real Gemini launch/healthcheck, not proof it discovers/calls all six
  tools. No direct non-model invocation command identified. Provider-based agent
  tool use stopped at this boundary; no real token requested, cookie read, demo
  consultation or mutation performed. A masked client launcher is not needed
  for healthcheck and remains pending for an authorized usable call path.
- Rechecked real AC-37/38/39: automated stdio schemas/auth + HTTP/service parity
  remain evidence for their tested scenarios; client healthcheck does not replace
  tools/list/call, personal session, human consent or whole-project acceptance.
- CI already runs every Python test on ephemeral PG with migrations from empty
  schema, SQLite guard, TP1, Node and coverage gates. Added only -rA reporting in
  test job so executed AC titles are visible; preserved mcp TP1 job and all gates.
- Intermediate local run415 passed during prototype; its coverage included
  operational artifacts, so not used as publication-scope metric. Final run on
  retained scope:411PGpassed1SQLiteguarddeselected+9TP1; services227/227+76/76=100%,
  global1438/1524 lines94.36% +342/378 branches90.48%, projectadapter90/90+30/30.
  Report03682cbfb4df40b4a35085dc211c8d00. Node23, MCP12/12 and ex2 32/32 passed.
- SQLite SHA256 identical to task start. Metadata checks keep local profiles,
  rotation receipt, demo database, .venv and Gemini dotenv ignored/untracked.
  No real value copied into tracked files. docs/MCP_FINALIZATION.md distinguishes
  automated tests, actual launch, untried final tool use and remaining Lab03 work.
  Assistance remains attributed; no personal architecture note written.
- Final independent custom reviewer ran once, read-only: no significant finding,
  no retained/rejected issue and no correction requested. JSON launch settings,
  ignored secrets, reporting-only CI change and separation of client/test proof
  were confirmed. Ready for normal publication; verify all four remote jobs on
  the actual pushed SHA rather than infer CI from local tests.
- Separate historical SQLite guard passed1 and Django check reported no issues.
  Final local ex2 32/32 and diff check clean. Only configuration/reporting/docs
  in the finalization commit; the three existing MCP commits remain intact.
- Normal push published 365b52b4ff12aad7a725e84b025ae763707a3d57. Local/remote
  refs equal, clean worktree. Verified Actions run44080856587 for that exact SHA:
  test134030755944, coverage134030755170, mcp134030758257, spec134030755621 all
  success. Test logs show real six-tool catalogue/quota/owner/revocation test
  titles,411PGpassed1deselected+1isolatedSQLite+9TP1+23Node. Both PG jobs start
  with zero public tables and apply all three migrations as restricted test role.
- CI coverage actual: services227/227 lines+76/76branches100%, global1439/1524
  lines94.42% and343/378branches90.74%, TP1 included; loaded JS modules98.18%
  lines90.91%branches. MCP12/12 andspec32/32. No job skipped; Docker step alone
  skipped by existing no-Dockerfile condition. No CI fix/gate weakening needed.
- Recording these remote facts is documentation-only; no full local rerun needed.
  Verify CI independently on the follow-up published SHA. Client actual tool
  use/real-session handoff, personal note/review, deferred UI and remaining
  project features remain pending; no Lab03 closure or next IA plan implemented.

## 2026-11-17 · AI suggestion planning only

- User authorized preparation of the AI plan, superseding the previous stop
  before AI only for this documentation task. Initial HEAD was published
  19820723c5babd14d0425ee8b2d0e0abd882ddbb; working tree was clean.
- Read applicable instructions, SPEC's model feature and actual AC-29–36,
  availability/creation services, data projections, session/API helpers and
  existing booking UI. No repeat HTTP/MCP audit, provisioning or secret rotation.
- Codex proposed docs/AI_SUGGESTION_PLAN.md, with three review checkpoints:
  service/fake client, provider adapter/protected API, existing-screen integration.
  The user's established choices are distinguished from assistant recommendations
  (1,000-character input, selected lab/date, deterministic first ten, isolated
  REST worker, status contracts). These are not approved implementation results.
- Web tool failed for course pages; read current Lab03 and project requirements
  through curl after the restricted-network failure and approved read-only retry.
  Google official model, deprecation, structured-output, REST, SDK retry/timeout,
  pricing, quotas and terms documentation were consulted. Model is documented
  stable with structured output and standard free-tier pricing; actual account
  access remains untested. Terms require clarification for API clients offered
  to EEA users: a free tariff alone is not authorization for this use. No billing
  or provider account was accessed. No silent model replacement.
- Plan preserves bounded candidates, no call when empty, output membership and
  fresh availability checks, explicit confirmation through create_booking,
  manual fallback, no retry or input/output logging. Five seconds requires an
  end-to-end deadline and cancellation proof, not only a socket timeout. No DB
  transaction/lock during the provider wait. No dependency/migration proposed.
- No application code, tests, CI, settings, secrets or data changed; no model API
  call, installation, commit or push. SPEC/AC remain unchanged. Personal note,
  Gemini tool use and deferred UI checks remain pending. User review is required
  before construction; this entry does not assert student understanding.
- Documentation checks: initial ex2 run stopped with EPERM while scanning the
  pre-existing pytest-cache-files-kzcco4xh directory under the sandbox. Retried
  the unchanged command outside that restriction: 32/32 passed. git diff --check
  passed. No application suite or coverage rerun: documentation only, no new
  functional evidence or coverage result claimed.
- Required read-only custom reviewer ran once for this architectural plan. No
  blocker; retained its important finding that worker cleanup after the deadline
  could extend the wait. Clarified the recommendation: reserve cleanup inside
  the same five-second budget (proposed 500 ms), never append a blocking wait,
  and require a wall-time test including slow cleanup before delivery. No finding
  rejected. Feasibility and plan approval remain open, not an executed guarantee.

## 2026-11-17 · AI substep 1 — injectable read-only suggestion service

- User approved substep 1 only: trimmed 1–1,000-character need, selected lab/date,
  up to ten distinct candidates in existing order, no call without candidates,
  and no booking creation. Local commit authorized; no push, real provider,
  transport worker, API, UI, migration, dependency, billing or key access.
- Initial HEAD19820723; pre-existing AGENT_LOG.md edits and untracked
  docs/AI_SUGGESTION_PLAN.md from the preceding planning turn were preserved,
  updated rather than replaced, and belong to this AI checkpoint. No other
  pre-existing worktree changes. AGENTS.md authorization now matches this scope.
- Codex wrote direct refusal tests first. Initial command on dedicated
  PostgreSQL test settings failed AC-29-access-anonymous with ModuleNotFoundError
  for src.services.ai_suggestion. Implemented the service and account-state
  projection in data/users.py; no ORM/SQL in the service or duplicated booking
  rules. The first full target run exposed a test-data hour error (two future
  slots at13UTC instead of expected three); changed the test clock to12UTC,
  preserving the three-slot assertion and production temporal rules.
- Targeted tests then passed51. Fake clients inspect bounded/minimal payloads,
  shape/type/membership validation, current application values, rechecks after
  occupation/quota/personal conflict/time/offline/account changes, explicit safe
  failures, no retry and no creation/cancellation. A real PostgreSQL autocommit
  test checks no transaction is held during the fake invocation.
- Contract supplies a monotonic five-second deadline and rejects late answers;
  it cannot interrupt a blocking function. No future network/process deadline
  claimed proved. The adapter must reject duplicate JSON keys before decoding.
  Free text may itself contain personal data; no identity/session/history added
  and no need/raw response logging. Google EEA conditions remain unresolved.
- SPEC records only partial service evidence for AC29–33/35–36; AC34 AI
  confirmation, provider identity/credentials, UI warning and manual fallback
  integration remain unbuilt. Existing MCP/client and personal/UI limits remain.
- Node regressions23, MCP checker12/12 and the isolated historical SQLite
  guard1 passed after unchanged reruns outside sandbox (initial spawn EPERM /
  temporary-directory permission refusal). Django check reported no issues.
- First full coverage run stopped425pass37setup errors1deselected due to
  inaccessible pytest temp directory; no assertion failure and no measurement
  accepted from that run. Unchanged rerun outside sandbox passed462PG tests,
  1deselected (only test_guard_refuses_unmarked_or_wrong_database, passed1
  separately under isolated historical SQLite settings), then9TP1 tests.
  PostgreSQL concurrency and all project stdio/parity regressions included.
- Final measured coverage: services319/319lines+108/108branches100%; new
  suggestion service92/92+32/32. Global1532/1618lines94.68%,374/410branches91.22%,
  includingTP1. Inventory/exclusions/gates unchanged. Ignored local report:
  .local/coverage/b2c0c78297e145d59aefee34ab9ec312/coverage.json. Parent unittest
  emitted no-data-collected warning; actual server subprocess data is included.
- Read-only custom reviewer ran exactly once for this implementation. No
  blocking/important finding; retained and fixed its README status ambiguity
  (full AI integration future, injectable service delivered). No finding rejected.
  No production changes after the successful test version. ex232/32 and diff
  check clean. Existing SQLite SHA256 remains identical to the pre-task value;
  .venv/.local/demo.sqlite3/Gemini.env remain ignored and untracked. No demo write,
  5432 operation, applied migration, CI change, key read or provider call.

## 2026-11-17 · AI substep 2 — bounded provider adapter and protected API

- User authorized only REST adapter, bounded execution, protected API, offline
  tests/docs and a local commit; no push/UI/install/migration/provider call,
  real key/billing/Google OIDC/MCP change/deployment. Initial HEAD3fa6ecb and clean
  worktree. No prior changes to preserve beyond that commit.
- Codex reread instructions, SPEC/actual AC29–36 and AI guides. Official Google
  model/REST/schema/errors/terms reread. Model unchanged. AI_TRANSPORT_2 cites
  the EEA Paid Services restriction verbatim and separates interpretation for
  a university website from account access, which remains untested. No billing
  or real provider authorization inferred from a free tariff.
- Tests first: initial REST test failed with missing src.integrations. Added
  stdlib-only REST module, isolated worker, supervising adapter and thin session/
  CSRF route. Factory defaults off and reads no key until explicit enablement;
  test configurations are supplied synthetic mappings, never CLI dotenv data.
- Private stdin packet (key never argv/env/log), minimal child environment,
  16KiB request/64KiB response bounds, fixed endpoint/model/schema, one attempt,
  no redirect/auth/proxy/retry handlers. JSON duplicates, blocked, truncated,
  empty, unknown or invalid outputs refused. ClientInvalidOutput maps to an
  explicit service result, with direct-test coverage added.
- First target run found excessive child stdout still waiting for natural exit;
  moved size refusal before process.wait. Fixed the anonymous API test setup
  by obtaining a fresh CSRF token after logout (not changing authentication).
  A temporary Mock environment in a test broke pytest's terminal code; replaced
  it with explicit mapping injection. No real environment key read in this fix.
- Dedicated oversized-request regression failed with Django RequestDataTooBig
  instead of our input refusal; added Content-Length check before request.body,
  then test passed. Changed only optional bounded parsing, not other routes'
  existing body limits. Malformed/nested JSON is safely refused.
- Targeted service/adapter/API tests passed126; additional oversized-body test
  passed1. JUnit timing .local/ai-transport-2.xml ignored. Controlled process
  measurements (seconds): normal0.180582, blocked4.518268, unread-stdin4.517513,
  excessive0.151316, crash0.239979, closed-stdout/slow-exit4.505264,
  delayed-cleanup250ms4.758038. All children reaped/pipes closed. Tolerance350ms
  is for scheduling/instrumentation, not an extension of the five-second budget.
  No browser latency, Google access or universal real-time OS guarantee claimed.
- API uses real sessions/CSRF/services and PostgreSQL test rows; no owner supplied
  by client, no business mutation, no transaction during wait (even with request
  atomicity enabled in a test). Safe typed failures keep manual availability API
  working. Test suite forces ambient AI off; API forbids real adapter calls,
  HTTP tests block sockets and simulate responses, child tests use local fixtures.
- Required read-only reviewer launched once after implementation/targeted tests.
  Its HTTPError point was clarified: current HTTPSHandler-only opener has no
  HTTPErrorProcessor, so non200 responses normally retain response.status.
  Nevertheless retained the robustness improvement for injected/evolved openers:
  HTTPError429 classified as quota and error bodies closed unread; tests red2
  then green2, no retry or sensitive message exposed.
- Preliminary full run537PGpass1deselected+9TP1 passed before final parser/HTTPError
  changes; not used as the final coverage claim. A fresh full measurement is
  required on the frozen source. Node regressions23, MCP checker12/12, isolated
  SQLite guard1 and Django check passed. No CI/remote success inferred locally.
- Frozen final version:129targeted passed, then540PGpassed1deselected and9TP1
  passed via unchanged coverage launcher. Only the historical SQLite guard
  deselected on PostgreSQL; separately passed1 under tests.settings_sqlite_legacy.
  Services322/322lines+108/108branches100%; global1765/1865lines94.64%,
  445/488branches91.19%, TP1 included. All new production files inventoried,
  no threshold/exclusion change. Actual local report:
  .local/coverage/6b37ecda75914bd59dc49b85ec9da0cb/coverage.json.
- Final timing JUnit refreshed: normal0.262753s, blocked4.512714, unread-stdin
  4.517720, excessive0.187992, crash0.192865, slow-exit4.510447,
  delayed-cleanup4.763058. Remaining six error IPC cases0.150987–0.235163s.
  All13 child scenarios reaped/closed. Local Windows only; no Google or Linux
  execution inferred. Parent unittest no-data-collected warning is expected;
  TP1 server subprocess lines are present in the measured combined report.
- Reviewer final: no blocking/important finding, retained HTTPError robustness
  improvement already fixed and tested; no finding rejected. Final tests ran
  after production fixes. Only documentary evidence updated afterwards.
  Node23/MCP12/ex232/SQLiteguard1/Django checks pass; final diff clean.
  SQLite demo hash unchanged; secrets/profiles/.venv/bases/timing/coverage remain
  ignored/untracked. Existing demo/5432/MCP/migrations preserved. No new
  functional/visual proof for UI, AC34 or the personal architecture note.

## IA sous-étape 3 — interface hors fournisseur, 17 novembre 2026

- Départ aeba6daa3e375412767b9904224d13128b5287a1, main propre. Périmètre
  utilisateur : UI seulement, tests et simulation isolée, commit local sans push.
  Choix de l'utilisateur ; formulation, code et tests préparés par Codex.
- Lecture AGENTS/SPEC/plan/guide transport/UI. AGENTS actualisé pour cette
  autorisation limitée ; aucun secret lu, fournisseur activé, changement CI,
  dépendance, migration, règle métier ou serveur MCP modifié.
- 19 tests DOM ajoutés et observés rouges avant code (handlers absents), puis
  verts. Trim 1–1 000, demande volontaire, double clic bloqué, CSRF/session,
  statuts, erreurs fixes, texte sûr, réponse obsolète et invalidation du besoin,
  date/labo ; confirmation existante, zéro retry. Helper DOM partagé sans
  retrait d'assertion historique. Cache modules labs v3/booking v2.
- 5 tests HTTP PostgreSQL avec faux client : suggestion sans mutation, puis
  confirmation valide ou refus poste occupé/hors service/quota/conflit personnel.
  Ciblage confirmation/page/accès : 16 réussis ; Node complet : 42 réussis.
- Couverture existante PostgreSQL : 545 réussis, 1 garde SQLite désélectionné,
  puis 9 TP1. Services 322/322 lignes + 108/108 branches, global 1765/1865 lignes
  (94,64 %), branches 445/488 ; aucun seuil, inventaire ou exclusion modifié.
  JS 41 tests et 97,71 % lignes / 95,59 % branches des modules chargés seulement.
- L'utilisateur a confirmé serveur lancé et session Edge prête. Avec le skill
  computer-use, Codex a observé le repli désactivé sur 8000, 20 créneaux manuels
  le 18 novembre puis la confirmation sélectionnée sans cliquer pour créer.
  Les deux anciennes entrées annulées sont restées visibles ; aucune mutation
  de réservation de démonstration effectuée pendant cette étape.
- Serveur de simulation explicite sur 8011 : identité vérifiée test_lab_booking_1a,
  rôle test, port 5433 ; cookies distincts, compte isolé inutilisable par mot de
  passe, faux client uniquement. Edge : succès identifié, vide avant clic puis
  une réservation À venir après confirmation ; délai, sortie invalide, quota
  simulés ; samedi sans candidat et session test révoquée. Le mode change via
  fichier non sensible ignoré ; bannière au chargement. Pas de capture archivée.
  Serveur arrêté par fichier dédié : nettoyage de ses seules lignes confirmé.
- Outils navigateur directs indisponibles ; fenêtre native Edge accessible.
  Les saisies de date par API d'accessibilité n'ont pas abouti ; sélection au
  calendrier observée ensuite. Aucun échec de produit déduit de cette limite.
- SQLite SHA256 inchangé. Instance 5432 et données conservées préservées.
  Google réel/conditions d'usage, note personnelle, client Gemini complet et
  contrôles UI reportés dont 380 pixels restent ouverts. Lab03 non clos.
  Guide détaillé : docs/AI_UI_3.md. Contrôles finaux et revue consignés ci-dessous.
- Contrôles complémentaires : garde SQLite historique
  test_guard_refuses_unmarked_or_wrong_database exécutée à part et réussie1,
  Django check sans problème, MCP12/12 et ex2 32/32. Aucun autre test pertinent
  ignoré. git diff --check a d'abord signalé une ligne vide finale du journal,
  corrigée ; ses avertissements LF/CRLF ne sont pas des erreurs de contenu.
- Reviewer personnalisé déclenché une fois, lecture seule : aucun défaut
  fonctionnel bloquant ; corruption d'accents dans deux ajouts documentaires
  et ligne vide EOF retenues puis corrigées. Recherche des séquences corrompues
  et diff --check relancés, sans erreur. Aucun constat écarté. Tests déjà
  exécutés sur le même code de production ; aucune CI distante déduite.
- Après revue : 42 Node et 16 tests PostgreSQL ciblés relancés, tous réussis.
  Présentation PEP8 des nouveaux tests finalisée ; lecture UTF-8/BOM du fichier
  de scénario vérifiée sans base ni réseau. .local, .venv et data/demo.sqlite3
  confirmés ignorés, aucun profil/base suivi. Aucun push.

## Finalisation et publication IA — 17 novembre 2026

- État initial propre, main devant origin/main de trois commits : 3fa6ecb,
  aeba6da et e1474e1. Fetch origin/main effectué : zéro commit distant à intégrer,
  trois commits locaux conservés. Aucun rebase, reset ou force push.
- Autorisation utilisateur : finalisation, ajustements CI nécessaires, revue,
  commits et push normal ; aucun Lab04, fournisseur, clé réelle, installation
  locale, facturation ou déploiement. Pas de nouvel essai Edge ou mutation démo.
- Lecture AGENTS, guides IA, MCP et Slice2 ; AGENTS actualisé sans élargir les
  autorisations fonctionnelles. Un seul changement CI : ajout des tests IA
  existants à la commande de couverture JS. Les suites automatisées test_*.py
  et *.test.mjs sont découvertes par les lanceurs existants ; fixtures/dispositifs
  manuels ne sont pas collectés. Aucun seuil/exclusion modifié.
- ex3 actuel exécuté sans changement : 15/18, sortie1. Échecs : npm ENOENT
  Windows (shell:false/npm.cmd), traçabilité de dix AC futurs/UI, note personnelle
  absente. Collecte réelle : 546 tests Python ; aucun AC1–10, tous AC29–36 présents.
  Les sous-chaînes du vérificateur ne prouvent pas les critères Google.
  Catégories et exigences ouvertes : docs/AI_FINALIZATION.md. Aucun test factice
  ni note personnelle écrite pour rendre ex3 vert.
- npm test direct : 545 PostgreSQL réussis/1 garde SQLite désélectionné, garde
  séparé réussi1, TP1 réussi9, Node réussi42. Durée PG observée206,01s.
  Commande couverture JS CI réussie41 : lignes97,71%, branches95,59%.
  Python production/tests inchangés : mesure locale récente1765/1865lignes,
  services322/322+108/108 conservée avec sa provenance ; CI doit mesurer Linux.
- ex2 32/32 et diff --check réussis ; .local/.venv/data ignorés, aucun fichier
  suivi sensible/base. SQLite SHA256 initial préservé. Ni secrets ni profils lus.
- Documentation préparée par Codex sur décisions utilisateur. Faux fournisseur,
  désactivé réel Edge, Google absent, client MCP final non validé, note/revue
  personnelles et UI reportées distingués explicitement ; Lab03 reste ouvert.
- Revue indépendante unique, lecture seule : constat de traçabilité retenu.
  Remplacement de « tous les tests Python » par les suites test_*.py collectées ;
  browser_ai_demo.py nommé dispositif manuel non collecté, non compilé/exécuté
  en CI et hors couverture, avec preuve locale distincte. Aucun défaut
  fonctionnel détecté, aucun constat écarté, aucun code/tests modifié après revue.
- Publication normale réalisée : da875b9fa25f56880bbc5e144285455dd60d6219,
  SHA local et origin/main comparés identiques, arbre propre. GitHub Actions
  44138036352 : quatre jobs success, aucune correction requise. test545PG+
  gardeSQLite1+TP1 9+Node42 ; MCP12/ex232. coverage Linux1766/1865lignes94,69%,
  branches446/48891,39%, services322/322+108/108100%, JS97,71%/95,59%.
  Zéro table publique avant migrations, 0001/0002/0003 appliquées. Seule étape
  Docker skipped par condition initiale, aucun job skipped. Preuves/liens dans
  AI_FINALIZATION.md. Ce complément documentaire sera publié puis sa propre CI
  vérifiée séparément ; aucune réussite présumée pour son futur SHA. Lab03 ouvert.

## Préparation documentaire de clôture Lab 03 — 17 novembre 2026

- Départ c96aa2ecebcc5821c11d61928fc2d194102f0592, main synchronisé/propre.
  L'utilisateur autorise uniquement analyse, traçabilité et préparation de la
  note, sans la rédiger ; aucun commit/push, code ou Lab04 à cette étape.
- Lecture AGENTS, ex3/lib et bilan IA ; Web des consignes en échec, curl réussi
  pour Lab03 et projet. Textes actuels lus : Goal, Steps, What you build,
  Working with the agent, What the assistant checks ; projet Requirements,
  Documents, Tests et When you build which part. Sources et limites dans
  docs/LAB03_CLOSURE.md ; distinction tranche/projet sans dispense inventée.
- ex3 officiel inchangé, nouvel essai Windows : 15/18, sortie1. Conditions npm,
  recherche textuelle des AC et note décrites exactement. Pas de wrapper,
  changement des contrôles ni fichier feature factice pour les rendre verts.
- WSL list initialement refusé par le bac à sable ; relance en lecture seule
  autorisée réussie, seule docker-desktop listée. Pas de distribution de travail
  préparée, pas de lancement/installation improvisé. Commande npm test Linux
  vérifiée dans les logs existants du SHA publié : run44138794766, job134235547443,
  Ubuntu,545PG+gardeSQLite1+TP1 9+Node42, étape environ85s. Pas d'ex3 Linux déduit.
- Collecte actuelle546cas Python, aucun AC1–10/12/43–45 ; tous les AC implémentés
  identifiés avec bornes exactes. Node42 réellement réexécutés, tous réussis.
  Pas de relance complète PostgreSQL pour des changements exclusivement doc.
- SPEC Traceability : une ligne pour chacun des49AC existants,46 références de
  fonctions Python vérifiées automatiquement. Critères approuvés identiques à
  HEAD, aucun identifiant ni test modifié. AC42 explicitement non prouvé par
  le titre de son test HTML ; Google/personnel/UI complets non revendiqués.
- Guide de note : fichiers/questions/points seulement, aucun texte personnel
  rédigé ni compréhension validée. Revue approfondie et entretiens reportés.
  Pas de reviewer indépendant supplémentaire : documentation seule, aucune
  décision d'architecture ou modification de code selon la règle AGENTS.
- Aucun fournisseur, secret, facturation, donnée ou migration touché. Vérificateur
  et helper comparés à HEAD, inchangés ; aucune CI modifiée ou déclenchée.
- Vérifications finales : ex2 32/32 ; ex3 15/18, sortie1 (trois échecs conservés) ;
  diff --check réussi. Note détectée :0 ligne, document feature:null. Six documents
  seulement, non indexés ; HEAD c96aa2e inchangé, aucun commit/push. Empreinte
  data/demo.sqlite3 identique à celle de départ. Mesure de couverture antérieure
  non présentée comme une nouvelle exécution ; aucun code/test modifié.

## Vérifications UI Lab 03 — 19 novembre 2026

- Départ c96aa2e avec les six documents du 17 novembre déjà modifiés ou créés.
  Consignes lues et changements antérieurs conservés. Ex3 laissé à son relevé.
- Codex a testé les deux écrans à 380, 768 et 1280 px CSS dans Edge. Le cluster
  local 5433 n'a pas démarré avec la commande prévue. Banc local jetable sur
  8011 avec base en mémoire, session et données synthétiques, fournisseur
  désactivé. Aucun parcours attribué à l'utilisateur. Aucune réservation
  soumise. Seul POST navigateur, la suggestion désactivée, a répondu 503.
- Défaut reproduit à 380 avec réponses retardées de 600 ms. Arrivées catalogue,
  historique et créneaux déplaçaient respectivement les ancres de 163, 167
  et 2 080 px. Modification du template labs.html et de app.css pour réserver
  l'espace dans trois zones nommées avec défilement vertical et focus visible.
  Après correction, déplacements de 0 px sur les trois largeurs mesurées.
- À 380, libellés et actions lisibles, historique accessible et choix manuel
  après repli IA. Captures dans la session et chiffres dans docs/UI.md.
  AC-42 reste partiel. Serveur arrêté et base en mémoire relâchée.
- 41 tests JS réussis. Exécution Django groupée sur SQLite historique :
  42 réussis et 2 échecs de fermeture de connexion aux tests MIME. Tests
  du template, de l'accès et de la connexion rejoués ensemble : 42 réussis.
  Deux tests MIME isolés sous tests.settings : 2 réussis. Port 5433 devenu
  disponible après les essais Edge. Page et accès rejoués sous PostgreSQL
  de test : 11 réussis, dont les deux tests MIME. Suite entière non relancée.
  Ex2 32/32, diff --check réussi. Empreinte SQLite démo identique au relevé
  antérieur. Ni appel fournisseur ni commit/push.
- Revue indépendante déclenchée une fois. Aucun défaut bloquant ou important.
  Suggestion d'assertions supplémentaires sur les régions différée. La preuve
  de stabilité et de focus est la mesure Edge et non la forme du HTML seule.

## Finalisation du correctif UI et de la traçabilité — 19 novembre 2026

- L'utilisateur a autorisé la vérification ciblée, la séparation des commits
  UI/tests et documentation, puis le push normal après réussite des contrôles.
  Codex a conservé les six documents de clôture préparés depuis c96aa2e.
- Codex a observé le refus 401 dans Edge à 380 px CSS sur le banc local isolé.
  Message lisible, adresse conservée, mot de passe vidé, deux champs corrigés
  au clavier et contour visible sur le bouton de connexion. Largeur mesurée
  380/380/380 pour viewport, client et scroll. Captures dans la conversation,
  aucun essai attribué à l'étudiant. Les mesures antérieures restent limitées
  aux trois déplacements observés. AC-42 reste partiel.
- Échec MIME reproduit (42 réussites et 2 échecs au nettoyage sous SQLite
  historique). Rappel de nettoyage isolé dans le test, assertions conservées.
  Même combinaison après correction : 44 réussites. Cas MIME isolés : 2.
  Node : 41 tests UI, 42 avec le test du lanceur. Voir les commandes et les
  preuves dans [LAB03_CLOSURE.md](docs/LAB03_CLOSURE.md).
- Revue indépendante unique pour cette publication. Aucun blocage relevé.
  Constat retenu et corrigé : vérifier dans le test Django que les trois zones
  réservées entourent leurs listes et restent nommées et accessibles au clavier.
  Les anciennes mentions du report à 380 px sont conservées dans les bilans
  historiques datés ; le bilan actuel précise la reprise du contrôle.
- Suite officielle `npm.cmd test` réussie hors du bac à sable : 545 PostgreSQL,
  garde SQLite exécutée à part (1), 9 TP1 et 42 Node. Tentative initiale dans
  le bac à sable bloquée par les permissions du dossier temporaire de pytest.
  Contrôles ex2 32/32, MCP TP1 12/12, Django check et diff --check réussis.
  Couverture JavaScript locale : 97,71 % des lignes sur les modules mesurés.

## Consultation des réservations du personnel — 19 novembre 2026

- Demande utilisateur depuis `2919829` : page et GET dédiés à AC-9, lecture
  seule, sécurité par le rôle actif `personnel`, validation isolée et commit local.
- Codex a ajouté la projection de données, le service et les deux routes.
  Les deux historiques partagent le calcul d'état. La route personnelle reste
  filtrée par son propriétaire. L'API du personnel expose seulement les champs
  de consultation, dont l'identifiant numérique du propriétaire. Le lien est
  dans l'en-tête du personnel et l'écran maintient les états de consultation.
- Codex a observé Edge à 380, 768 et 1 280 px CSS avec deux lignes synthétiques,
  un focus visible et aucun débordement horizontal mesuré. À 380, un 503
  simulé a été suivi d'un réessai clavier et d'un 200. Le banc en mémoire a été
  arrêté. Les preuves navigateur et PostgreSQL sont distinguées dans
  [STAFF_BOOKINGS.md](docs/STAFF_BOOKINGS.md). AC-5, AC-40 et AC-42 restent partiels.
- ex2 : 32/32. ex3 : 15/18. AC-9 n'est plus signalé, les autres écarts restent
  consignés. Aucun compte étudiant persistant modifié ni fournisseur sollicité.
- Couverture locale PostgreSQL : 552 cas et 9 tests Python TP1 réussis, garde
  SQLite réussi séparément. Services à 347/347 lignes et 110/110 branches.
  Global à 1 826/2 074 lignes (88,04 %), bancs ignorés `.local/` inclus.
  Node : 51 réussites et 97,76 % des lignes sur les modules mesurés localement.
  Contrôles Django et MCP TP1 réussis. Configuration et seuils conservés.
- Revue indépendante unique sans blocage. Ajout d'un cas prouvant la priorité
  du début sur l'identifiant au tri. 8 cas PostgreSQL AC-9 et 9 cas DOM rejoués
  avec succès. Le point mineur sur les paramètres d'URL a été écarté : l'API
  expose une vue fixe et l'ajout de filtres ou d'un contrat de recherche sort
  du périmètre de cet écran.

## Catalogue du personnel — 20 novembre 2026

- Demande utilisateur depuis le commit local `1f2c023` pour AC-6 à AC-8.
  Codex a ajouté le catalogue, les quatre écritures et la lecture protégée.
  Le contrôle du rôle `personnel` est partagé avec les réservations. La session
  Django, le CSRF et la contrainte PostgreSQL existante protègent les écritures.
- Les tests ciblés PostgreSQL ont réussi, dont les refus d'un étudiant avec
  CSRF valide, le refus d'un doublon dans son laboratoire, l'acceptation du même
  nom dans un autre et la stabilité des identifiants et du rattachement.
- Codex a exécuté les quatre actions au clavier et F5 dans Edge à 380, 768 et
  1 280 px CSS. Les créations ont répondu 201, les renommages 200. Les trois
  paires d'identifiants et les noms révisés sont revenus dans le même ordre et
  sans débordement horizontal mesuré. Le banc synthétique en mémoire a été
  arrêté. Les bases de démonstration ont été préservées.
- Le guide [STAFF_CATALOGUE.md](docs/STAFF_CATALOGUE.md) sépare les preuves Edge,
  PostgreSQL et DOM. AC-5, AC-40 et AC-42 restent partiels. Le changement d'état
  des postes reste pour la tranche suivante.
- Revue indépendante unique. Le test contrôle désormais l'ordre des deux
  laboratoires et des postes, avec des noms qui donneraient un autre ordre
  alphabétique. La liste de fichiers du job de couverture JS devra être étendue
  pour mesurer le catalogue lors d'une publication. La mesure locale inclut
  les deux écrans du personnel avec le seuil existant.
- Couverture locale : 568 cas PostgreSQL et 9 TP1 réussis. Services 394/394
  lignes et 120/120 branches. Global 1 963/2 211 lignes (88,78 %), incluant
  les anciens bancs Python ignorés. 60 tests Node réussis, couverture UI locale
  à 97,80 % des lignes. Django, ex2 (32/32), MCP (12/12) et garde SQLite réussis.
- Les 23 cas ciblés PostgreSQL repassent après la revue. Ex3 reste à 15/18 et
  reconnaît AC-6 à AC-8. Le vérificateur, les migrations et la CI restent intacts.

## État des postes du personnel — 20 novembre 2026

- Demande AC-10 à AC-12 depuis `551a200`, avec conservation des deux commits
  du personnel. Catalogue et API appliquent un état booléen explicite sous
  la session `personnel` et le CSRF. Une seule colonne est écrite sous le même
  verrou de ligne que la création des réservations. Les deux historiques
  montrent l'état courant du poste et gardent le statut de la réservation.
- Sur PostgreSQL de test, le cycle conserve tous les champs de la réservation,
  refuse en 409 le créneau autrement valide tant que le poste est hors service
  et retrouve la liste initiale en service. Deux ordres concurrents vérifient
  l'attente effective du verrou, le refus après désactivation et la conservation
  d'une réservation validée avant désactivation. Les refus rôle et CSRF restent distincts.
- Le premier passage a détecté une session de test expirée en avançant l'horloge
  après sa création. Les deux sessions du scénario démarrent maintenant avec la
  même horloge figée. Les 28 cas PostgreSQL ciblés et les 64 tests Node passent.
- Codex a observé le cycle au clavier dans Edge à 380 × 424 px CSS sur un seul
  poste synthétique. La réservation de 9 h à 10 h reste visible et le créneau
  de 10 h revient après remise en service. Le banc en mémoire a vérifié la ligne
  conservée et a été arrêté. Les bases de démonstration sont préservées.
- La revue indépendante a demandé deux refus supplémentaires pour l'endpoint
  d'état, sans session et avec un membre du personnel désactivé, et une
  précision sur les quatre écritures historiques du catalogue. Les deux
  améliorations ont été retenues.
- La couverture complète réussit 573 cas PostgreSQL et 9 tests TP1. Services
  à 404/404 lignes et 124/124 branches. Global à 1 995/2 243 lignes (88,94 %),
  avec les anciens bancs Python ignorés. Le garde SQLite a réussi séparément.
  Couverture UI locale 97,97 % des lignes. Django, ex2 (32/32) et MCP (12/12) passent.
- Les 28 cas ciblés repassent après la revue. Ex3 reconnaît AC-10 à AC-12 et
  reste à 15/18 pour les écarts Windows, UI et note personnelle.

## Publication de l'espace du personnel — 20 novembre 2026

- `git fetch` confirme `2919829` sur `origin/main`. Les commits `1f2c023`,
  `551a200` et `c3cc0aa` le suivent dans l'ordre, sans divergence. La publication
  conserve ces commits et ajoute les ajustements de couverture et du guide.
- La commande locale identique à celle configurée pour le job de couverture
  exécute 63 cas UI, avec 97,97 % des lignes sur Node 22.12.0 sous Windows.
  Les deux modules `staff_bookings.mjs`
  et `staff_catalogue.mjs` figurent dans le rapport avec `labs.mjs` et
  `booking.mjs`, qui contient la logique de suggestion IA. Le 64e cas de
  `npm test` vérifie le lanceur lui-même.
- Les deux bancs Edge de `.local/` sont présents sur la machine d'essai,
  ignorés et absents de l'arbre Git. Le guide pointe vers les tests PostgreSQL
  versionnés pour rejouer le cycle, sans utiliser la base de démonstration.
- L'inventaire de couverture Python est conservé. Le rapport local précédent
  inclut 148 lignes non exécutées de deux fichiers Python ignorés. L'ancienne
  CI a mesuré le code de `2919829` depuis un clone propre avec un inventaire
  différent.
- Ex2 donne 32/32. Ex3 reste à 15/18 sous Windows, avec `spawnSync npm ENOENT`,
  l'absence de titres de test pour AC-43 à AC-45 et la note personnelle
  encore attendue. Le vérificateur officiel est conservé. Le job `spec` lance ex2.
- La revue indépendante a demandé de préciser la provenance locale du rapport
  JavaScript avant le push. Le guide et le journal l'indiquent explicitement.

## Réexamen de clôture Lab 03 — 23 novembre 2026

- Au réexamen précédent, HEAD `464cbeb` et arbre alors propre. Pages Lab 03 et projet relues via curl HTTP
  200 après échec du lecteur Web. Seule distribution WSL : `docker-desktop` ;
  moteur Docker indisponible. Aucun ex3 Linux local déclaré.
- AC-43 et AC-44 ont des preuves partielles de clavier, libellés, contraste,
  titre et langue. Le parcours complet et l'audit de tous les écrans restent à
  faire. Pour AC-45, un test de jetons a d'abord échoué sur `h2` à `1.25rem`.
  La taille utilise maintenant `--text-section`. Le test ciblé repasse.
- Suite Node complète : 65/65. Ex2 : 32/32. Ex3 officiel inchangé : 15/18,
  sortie 1 sous Windows pour `npm` ENOENT, AC-43/44 et note personnelle.
  `git diff --check` passe. Aucun test PostgreSQL nécessaire pour la seule
  correction CSS. Note et revue personnelle demeurent à la charge de l'étudiant.

## Complément UI Lab 03 — 23 novembre 2026

- Cette reprise a trouvé `AGENT_LOG.md`, `SPEC.md`,
  `docs/LAB03_CLOSURE.md`, `docs/UI.md`, `src/static/css/app.css` et
  `tests/test_booking_page.py` modifiés, ainsi que
  `tests/style_tokens.test.mjs` non suivi. Ces travaux locaux préexistants ont
  été préservés et complétés sans remise à zéro.
- Sur autorisation de l'étudiant, Codex a exécuté dans Edge un parcours continu
  au clavier avec une instance Django isolée reliée à PostgreSQL de test sur
  5433. Compte et laboratoire synthétiques ; aucun compte ou réservation de
  démonstration modifié. Connexion, date, créneau, confirmation, historique,
  annulation et déconnexion observés. La liste de créneaux a fait 10 → 9 → 10 ;
  la ligne est passée de « À venir » à « Annulée ». Focus et libellés observés.
- Edge DevTools Responsive : connexion mesurée à 380/768/1280 px CSS, sans
  débordement horizontal mesuré. Edge CSS Overview et le calcul WCAG du test
  Node ont contrôlé les associations principales de couleurs. Les quatre
  éléments interactifs mesurés sur la connexion font au moins 44 px. Les autres écrans
  reprennent les preuves Edge antérieures, avec leurs lacunes consignées dans
  docs/UI.md ; AC-44 reste partiel.
- AC-45 : `app.css` seul CSS applicatif, inspection complète des règles,
  `--text-section` vérifié et titres revus dans Edge. `tests/style_tokens.test.mjs`
  vérifie aussi contraste et cibles CSS. Le test de template porte AC-43 pour
  ses assertions sémantiques ; l'essai clavier reste une preuve distincte.
- Vérifications : `tests/test_booking_page.py` sous PostgreSQL, 3 réussites ;
  suite Node complète 66/66 ; couverture JavaScript 63/63, 97,97 % lignes et
  94,69 % branches ; ex2 32/32 ; ex3 16/18 sous Windows (`npm` ENOENT et note
  personnelle manquante) ; `git diff --check` réussi. Le premier lancement
  Node dans le bac à sable a échoué avec EPERM ; relancé hors bac à sable.
  Aucun test Python global ni appel fournisseur pour ce changement UI.
- La note et la revue personnelles de l'étudiant restent en attente. Aucune
  compréhension personnelle ni approbation professorale revendiquée.

## Complément AC-44 et préparation de publication — 23 novembre 2026

- À la demande de l'étudiant, Codex a repris l'audit Edge des écrans livrés,
  sans refaire le parcours AC-43. Un banc local non suivi a utilisé uniquement
  PostgreSQL de test sur 5433, des comptes synthétiques et des réponses GET
  vides, retardées ou 503 simulées. Aucun fournisseur ni donnée de démonstration.
- Zoom navigateur Edge réellement réglé à 200 %, émulation désactivée :
  `innerWidth/clientWidth/scrollWidth = 379/372/372` CSS pour la connexion,
  l'étudiant, les réservations du personnel et le catalogue. Aucune petite
  cible visible parmi les liens, boutons et champs mesurés ; aucun débordement
  horizontal observé. Les états de lecture succès/vide/erreur/chargement et
  leurs limites sont détaillés dans `docs/UI.md`. AC-44 reste partiel.
- La couverture JavaScript lancée hors du bac à sable local a réussi : 63/63,
  97,97 % des lignes et 94,69 % des branches des modules UI mesurés. Le premier
  essai restreint avait échoué sur `spawn EPERM` ; aucune assertion modifiée.
- Les lignes du banc UI ont perturbé le premier `npm test` avec `--reuse-db`.
  `--create-db` a refusé la création, faute de privilège pour le rôle de test.
  Après arrêt du serveur, Codex a vérifié le nom `test_lab_booking_1a` et le
  port 5433, puis vidé seulement cette base de test ; migrations conservées.
  La relance de `npm test` a réussi : 573 PostgreSQL, 1 garde SQLite, 9 TP1 et
  66 Node. Ex2 : 32/32. Ex3 officiel : 16/18 sous Windows/Node 22.12.0,
  échecs `npm` ENOENT et note personnelle absente. La CI du nouveau commit
  reste à vérifier après publication.
- Une revue indépendante en lecture seule a relevé que la liste des fichiers
  préexistants omettait `docs/UI.md` et `tests/test_booking_page.py` ; la
  provenance a été corrigée. Aucun défaut fonctionnel supplémentaire retenu.
## Lab 04 — préparation locale du déploiement, 23 novembre 2026

- Demande de l'étudiant : commencer uniquement la préparation locale du Lab 04 et fournir un brouillon d'architecture explicitement attribué à Codex. La note personnelle, la revue personnelle et les exigences ouvertes du Lab 03 ne sont pas déclarées terminées. Aucun commit, push, déploiement, accès à une clé réelle ou appel fournisseur.
- Codex a relu les sections « Steps » et « What you build » de l'Exercise 04 et « The requirements, exactly » du guide projet. Les sources actuelles Render/Neon ont servi à distinguer service Render gratuit, base Neon et impossibilité d'utiliser un pré-déploiement ou shell sur la formule gratuite. Aucune affirmation de compatibilité distante testée.
- Réalisation : Dockerfile, contexte filtré, Gunicorn sans journal d'accès contenant les URL, WhiteNoise et collecte statique, réglages PostgreSQL/TLS/HTTPS/cookies/CSRF, erreurs publiques courtes et `GET /health` avec `SELECT 1` en couche de données. Le démarrage exécute les migrations avant Gunicorn. `/health` contourne seulement la redirection HTTPS de Django afin qu'une sonde Render ne considère pas une simple réponse 301 comme preuve de base disponible ; l'edge Render redirige le HTTP public.
- Vérifications : 22 tests ciblés PostgreSQL réussis après les dernières corrections, dont le contrôle du journal `django.request`, le port Gunicorn et le service d'un module JavaScript collecté par WhiteNoise avec MIME `text/javascript`. Le test statique a révélé un fichier maintenu ouvert par la réponse en flux ; la réponse est désormais fermée avant le nettoyage de son dossier temporaire, et le test utilise explicitement la base pytest nécessaire à la fermeture des connexions. `collectstatic` : 7 fichiers copiés et 21 traités au premier passage ; second passage 0 copié, 7 inchangés, 17 traités. `manage.py check --deploy` avec valeurs factices : deux avertissements HSTS sur sous-domaines et preload, non activés volontairement pour le domaine partagé `onrender.com`. `pip check` : aucune dépendance cassée. Ex2 : 32/32 hors sandbox. Ex4 : 21/29 ; preuves UI et publiques manquantes, coût fournisseur non mesuré, et vérificateur structural ne reconnaissant pas la porte Python de couverture.
- La couverture complète PostgreSQL hors sandbox a exécuté 591 tests applicatifs (1 garde SQLite désélectionné) et 9 tests TP1, puis réussi les seuils : services 407/407 lignes et 124/124 branches ; global Python 2066/2463 lignes (83,88 % en lignes) et 488/598 branches, rapport combiné 83,44 %. Le rapport global inclut aussi plusieurs scripts Python locaux ignorés sous `.local`, sans changement de seuil ou d'exclusion. Cette mesure a commencé avant les derniers ajouts de test et l'exemption `/health` ; les tests ciblés ont été relancés ensuite, mais la couverture complète n'a pas été répétée pour ces seules lignes de configuration. La première exécution de couverture dans le sandbox a échoué sur 37 créations de `tmp_path` dues aux ACL Windows, avec 552 tests réussis ; la relance hors sandbox a réussi.
- Docker CLI 27.4.0 est présent, mais le moteur `dockerDesktopLinuxEngine` était inaccessible dans le sandbox et hors sandbox : aucune image construite ni conteneur démarré. La CI distante et la mise en ligne ne sont pas vérifiées. Les données SQLite/démonstration, les profils sensibles et PostgreSQL 5432 n'ont pas été modifiés. Une revue indépendante en lecture seule n'a relevé aucun blocage ; son point sur l'absence de preuve du journal 500 a été traité par un test `caplog` réussi. Le risque des migrations au démarrage pour une évolution de schéma incompatible reste documenté et à revoir avant cette évolution.
- Aucun énoncé de déploiement de l'assistant n'a été démontré faux lors de cette étape ; les affirmations non vérifiées sont marquées comme telles dans `READINESS.md`.

## Lab 04 — validation Docker locale, 23 novembre 2026

- L'étudiant a autorisé une validation isolée, sans ressource distante, donnée de démonstration ni changement de secret existant. Le moteur Linux Docker était initialement indisponible (tube nommé absent), puis Docker Desktop a démarré et le moteur 27.4.0 a répondu. L'image a été construite localement.
- Un banc temporaire ignoré par Git a créé un réseau, un volume et des conteneurs propres à l'essai : PostgreSQL 16 sur réseau interne, application Gunicorn et proxy HTTPS Caddy avec certificat autosigné. Identifiants et clé Django éphémères ont été générés en mémoire. Le premier essai du banc s'est arrêté sur une course pendant l'initialisation interne de PostgreSQL ; après attente d'une vraie connexion TCP, l'essai final a réussi. Le banc temporaire et les ressources nommées ont été supprimés.
- Sur la base neuve : zéro table applicative avant démarrage, 18 migrations appliquées, connexion applicative PostgreSQL chiffrée confirmée par `pg_stat_ssl`, puis travailleurs Gunicorn démarrés. `/health` a rendu 200, puis 503 générique pendant l'arrêt de la base, puis 200 après son retour. Derrière HTTPS local, `/login`, CSS et module JS ont répondu 200 avec MIME attendu ; URL inconnue 404 générique. Une exception synthétique a produit un 500 générique par le client Django dans le conteneur, sans essai réseau externe de ce 500.
- Un laboratoire synthétique dans cette seule base a conservé identifiant et nom après recréation du conteneur applicatif. Ce résultat ne démontre pas la persistance sur Neon ou après redéploiement Render. Le certificat public et les cookies sécurisés en navigateur restent non vérifiés. Le test TLS local utilisait `sslmode=require` et ne prouve pas l'authentification du serveur ; `verify-full` reste à vérifier avec Neon.
- Suite officielle `npm test` sur l'état applicatif courant : 595 tests PostgreSQL réussis, un test SQLite spécifique désélectionné sous PostgreSQL mais exécuté séparément avec succès, 9 tests TP1 et 66 tests Node réussis. Le premier passage de couverture a échoué sur une attente MCP stdio de 15 s sous instrumentation (594 réussites, 1 échec, 1 désélectionné), alors que ce même cas ciblé a réussi sous couverture en 7,61 s. Sans modification de seuil ni d'assertion, la seconde mesure officielle a réussi : 595 tests PostgreSQL, 9 TP1 ; services 407/407 lignes et 124/124 branches ; global Python 2074/2463 lignes et 490/598 branches, rapport combiné 83,76 %. L'inventaire de production du lanceur est resté inchangé ; le rapport global compte aussi des scripts locaux ignorés dans `.local`. La couverture UI séparée a réussi : 63 tests, 97,97 % lignes et 94,69 % branches.
- Ex2 a réussi 32/32 hors bac à sable Windows après un `EPERM` sur un dossier temporaire pytest dans le bac. Ex4 officiel a rendu 21/29 : URL publique et preuves de déploiement/UI absentes, coût fournisseur non mesuré, et contrôles structuraux ne reconnaissant pas certaines formulations de la couverture Python et du repli IA. Aucun vérificateur modifié. `git diff --check` a réussi. Les ressources Docker de l'essai ont été vérifiées absentes après nettoyage.

## Lab 04 — préparation de publication, 24 novembre 2026

- L'étudiant a autorisé le commit et le push normal de la préparation locale du Lab 04, après ajout d'une construction Docker bloquante en CI. Le déploiement et la création de ressources Neon/Render ne sont pas autorisés. Le brouillon d'architecture garde l'attribution explicite à Codex ; la note personnelle du Lab 03 reste ouverte.
- L'étape Docker conditionnelle du job `test` a été rendue inconditionnelle. Le Dockerfile exécute `collectstatic` avec `src.config.static_build`, fondé uniquement sur les réglages partagés ; les variables et secrets de production ne sont exigés qu'au démarrage. La construction locale exacte de la CI, puis une construction sans cache, ont réussi sans base ni identifiants transmis au build. La seconde a exécuté l'installation des dépendances et copié 7 fichiers statiques, avec 21 traitements. L'inspection des seuls noms de variables de l'image n'a trouvé ni `DATABASE_URL`, ni `DJANGO_SECRET_KEY`, ni `GEMINI_API_KEY` ; aucune valeur n'a été affichée.
- Tests PostgreSQL ciblés de santé, réglages de production et erreurs : 22/22. Ex2 : 32/32. La suite complète et la couverture de l'état applicatif inchangé ont réussi le 23 novembre : 595 tests PostgreSQL, 1 garde SQLite séparée, 9 TP1, 66 Node ; services 407/407 lignes et 124/124 branches, global Python 2074/2463 lignes et 490/598 branches.
- Revue indépendante en lecture seule : aucun défaut bloquant pour cette préparation locale. Constat retenu : le validateur de `DATABASE_URL` n'accepte pas encore un éventuel paramètre `sslrootcert` nécessaire à une vérification de certificat Neon ; la source de confiance réelle dans l'image reste à établir avant tout déploiement. L'exemple `.env.example` et le guide signalent désormais que `sslmode=require` seul ne valide pas l'identité du serveur. Aucun changement spéculatif du profil de production sans essai Neon. La CI du commit publié reste à vérifier.

## Lab 04 — préparation du contrôle TLS Neon, 24 novembre 2026

- L'étudiant a signalé la création du projet Neon `lab-booking`, base `lab_booking`, PostgreSQL 16, région AWS Frankfurt, offre Free. Le formulaire Render est ouvert ; aucun déploiement n'a été demandé ni lancé.
- Codex a vérifié la documentation PostgreSQL et Neon : `sslmode=verify-full` avec `sslrootcert=system` utilise l'autorité de confiance du conteneur et vérifie le nom de l'hôte. Le profil Django accepte désormais cette combinaison et la transmet à Psycopg ; il rejette les chemins de CA arbitraires et la combinaison `require` avec `sslrootcert=system`.
- Une image Docker locale a été construite sans accès à Neon ni secret. Un script local ignoré par Git effectue le contrôle de la chaîne directe avec saisie masquée, conteneur éphémère et requêtes SQL uniquement en lecture. Les premiers diagnostics ont isolé la différence entre le magasin CA de Python et celui de libpq ; le Dockerfile fournit maintenant explicitement le bundle CA Linux via `SSL_CERT_FILE`, tout en conservant `verify-full`.
- Le profil de production peut déduire le domaine Render initial et son origine HTTPS de `RENDER_EXTERNAL_HOSTNAME`, si les deux variables Django explicites sont absentes. Le démarrage et les cookies sur Render restent non vérifiés.
- Les 26 tests ciblés de configuration ont réussi sur PostgreSQL de test après une première tentative bloquée par l'ACL Windows du répertoire temporaire dans le bac à sable ; le même test a réussi hors de cette restriction.
- L'étudiant a exécuté le contrôle final depuis l'image corrigée et transmis uniquement : « Connexion Neon vérifiée : Django, verify-full, CA de l'image, lecture seule, PostgreSQL 16. » Le script et l'image ont été inspectés par Codex ; la saisie et la console de l'étudiant n'ont pas été observées directement. Aucune migration ni écriture Neon, aucun déploiement Render.
- Suite locale après les changements Python : `npm test` a réussi (604 tests PostgreSQL, une garde SQLite séparée, 9 TP1 et 66 Node). Couverture PostgreSQL officielle : services 407/407 lignes, 124/124 branches ; global Python 2082/2513 lignes et 496/616 branches, avec le script local ignoré compté à 0 %. Ex2 : 32/32. La construction de l'image finale et le contrôle de présence du bundle CA ont réussi.
- Revue indépendante en lecture seule : constat retenu, le profil acceptait encore l'URL Neon par défaut en `sslmode=require`. Le validateur refuse désormais pour les hôtes Neon toute combinaison autre que `verify-full`, `sslrootcert=system` et `channel_binding=require`, avec des tests de refus. Le `require` du banc local autosigné reste utilisable pour les autres hôtes. La revue a également relevé une phrase documentaire obsolète sur les hôtes Render et l'espacement de la commande locale ; les deux ont été corrigés. Les 29 tests ciblés ont réussi après cette correction, et l'image finale a été reconstruite sans secret ni base au build.
- Couverture officielle relancée sur le code final : 607 tests PostgreSQL réussis, 1 garde SQLite désélectionnée dans ce lot, 9 tests TP1 réussis ; services 407/407 lignes et 124/124 branches, global Python 2082/2513 lignes et 496/616 branches (82,39 % combiné). Le script local ignoré figure toujours dans le dénominateur à 0 %, sans exclusion nouvelle. `npm test` complet avait réussi avant le dernier durcissement ciblé de l'URL Neon ; les 29 tests de configuration concernés ont été rejoués après.
## Lab 04 — première mise en ligne et correction ciblée, 24 novembre 2026

- Observations de l'étudiant : Render a déployé `dafa3ec` après remplacement de
  `DJANGO_SECRET_KEY` ; `/` affichait « Page introuvable », `/labs` conduisait à
  une connexion mise en forme, `/health` rendait `{"status":"ok","db":"ok"}` ;
  les journaux contenaient `Control server error` avec permission refusée sur
  `/home/appuser`. Aucun secret ni journal complet n'a été reçu.
- Observations de Codex avant correction publique : HTTPS `/` 404, `/labs` 302,
  `/login` 200, `/api/labs` 401 JSON, CSS et module JS 200 avec MIME correct.
  Le routeur manquait `/`. Le conteneur tourne comme UID 10001 sans répertoire
  personnel ; le socket de contrôle facultatif de Gunicorn le cherchait sous
  `/home/appuser`. Une redirection `/` vers `/labs` et la désactivation du socket
  corrigent ces causes sans élargir les permissions.
- Le préparateur de démonstration publique a été écrit pour deux nouveaux
  comptes ordinaires et un petit catalogue sur la base Neon existante. Sa
  transaction est relançable, ne modifie pas les mots de passe existants et ne
  transfère aucune donnée locale. Il n'a pas été exécuté sur Neon ; l'étudiant
  doit saisir localement l'URL directe et deux mots de passe masqués.
- Les vérifications de connexion, réservation, annulation, cookie de session
  HTTPS, disparition du message Gunicorn sur Render et persistance après
  redéploiement restent distinctes des tests locaux. L'IA reste désactivée.
- Tests locaux du correctif : 71 ciblés PostgreSQL, `npm test` avec 616
  PostgreSQL, 1 garde SQLite, 9 TP1 et 66 Node ; couverture PostgreSQL/TP1
  services 407/407 lignes et 124/124 branches, global 2156/2601 lignes et
  520/648 branches (82,36 % combiné) ; ex2 32/32. Ex4 avant redéploiement :
  25/34, dont le 404 public attendu avant publication. L'image locale a lancé
  Gunicorn 27.0.1 et deux workers sans erreur de socket, puis a été arrêtée
  volontairement. Revue indépendante : aucun blocage ; la recommandation
  d'essai Gunicorn réel a été suivie. Les journaux Render restent à confirmer.
- Publication et observation : `449bf7b` poussé normalement sur `origin/main` ;
  [CI 45309644035](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/45309644035)
  verte (`test`, `coverage`, `mcp`, `spec`). La CI a mesuré services 407/407
  lignes, 124/124 branches ; global Python 2157/2274 lignes, 521/572 branches
  (94,10 % combiné). Après le déploiement automatique, Codex a observé `/`
  à 302 vers `/labs`, `/health` à 200 et `/api/labs` sans session à 401 JSON
  sans liste. Ex4 officiel : 27/34 ; les deux contrôles de page passent
  désormais, les sept autres restent décrits dans le guide. Aucun compte ou
  catalogue public n'a encore été préparé par Codex.
