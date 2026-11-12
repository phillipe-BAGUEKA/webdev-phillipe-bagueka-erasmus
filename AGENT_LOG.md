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
