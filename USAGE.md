# Usage

One row per agent session. In Gemini CLI, type `/stats` before you quit and copy the input and output tokens. Copilot shows credits instead of tokens: write those in the credits column. The free tier charges nothing, so record what the session **would cost at the provider's published list price**, and note once below the table which price list you used. Leave the cost empty for rows that only show credits.

| Date | Tool | Input tokens | Output tokens | Credits (if no tokens) | List-price cost |
|---|---|---|---|---|---|
| 2026-11-17 | Codex, MCP plan and substep 1 session authentication/project bootstrap | non disponible | non disponible | sans objet (no provider call) | non calculable |
| 2026-10-20 | Codex | non disponible | non disponible | non disponible | non disponible |
| 2026-10-20 | Gemini CLI, trial 1 (`gemini-2.5-flash` and `gemini-3.8-flash`) | 25,287 | 59 |  | ≈ US$0.02036, estimate |
| 2026-10-21 | Gemini CLI, trial 2 (`gemini-3.8-flash`) | non relevé | non relevé | sans objet | non calculable |
| 2026-10-21 | Codex, TP1 documentation and checks | non disponible | non disponible | sans objet | non calculable |
| 2026-11-03 | Codex, TP2 topic and specification preparation | non disponible | non disponible | sans objet | non calculable |
| 2026-11-03 | Codex, checkpoint 1 Django structure and data | non disponible | non disponible | sans objet | non calculable |
| 2026-11-04 | Codex, checkpoint 2 local sign-in, protected page and sign-out | non disponible | non disponible | sans objet | non calculable |
| 2026-11-04 | Codex, checkpoint 3 laboratory API/list and Python coverage | non disponible | non disponible | sans objet | non calculable |
| 2026-11-04 | Codex, checkpoint 3 module MIME diagnosis and correction | non disponible | non disponible | sans objet | non calculable |
| 2026-11-04 | Codex, actual port-8000 browser diagnosis and module cache correction | non disponible | non disponible | sans objet | non calculable |
| 2026-11-04 | Codex, AC-48 browser withdrawal/restoration verification (entry added during finalization) | non disponible | non disponible | sans objet | non calculable |
| 2026-11-12 | Codex, checkpoint 4 Edge availability/confirmation/history/cancellation and evidence documentation | non disponible | non disponible | sans objet (no provider call) | non calculable |
| 2026-11-12 | Codex, Slice 2 browser/contrast checks, sourced TP3 audit, PostgreSQL CI and publication | non disponible | non disponible | sans objet (no provider call) | non calculable |
| 2026-11-12 | Codex, real HTTP observation preparation and second demo student | non disponible | non disponible | sans objet (no provider call) | non calculable |
| 2026-11-12 | Codex, real Edge HTTP 201/409/403, anonymous 401 and retained demo cancellation | non disponible | non disponible | sans objet (no provider call) | non calculable |
| 2026-11-04 | Codex, TP2 documentation and local CI/publication preparation | non disponible | non disponible | sans objet | non calculable |
| 2026-11-04 | Codex, authorized TP2 publication and GitHub Actions verification | non disponible | non disponible | sans objet | non calculable |
| 2026-11-11 | Codex, checkpoint 2B transactional creation and direct PostgreSQL tests | non disponible | non disponible | sans objet | non calculable |
| 2026-11-11 | Codex, checkpoint 2C real PostgreSQL concurrency and quota mutation test | non disponible | non disponible | sans objet | non calculable |
| 2026-11-11 | Codex, checkpoint 2D owner-only cancellation and PostgreSQL tests | non disponible | non disponible | sans objet | non calculable |
| 2026-11-11 | Codex, checkpoint 3 HTTP booking APIs, CSRF and PostgreSQL integration | non disponible | non disponible | sans objet | non calculable |
| 2026-11-11 | Codex, checkpoint 4 student booking UI, tests and authorized PostgreSQL demo preparation | non disponible | non disponible | sans objet | non calculable |

These are statistics reported by the student from Gemini CLI, not measurements
of the single lecture lookup. In trial 1, `/stats model` showed:

- `gemini-2.5-flash`: 1 request, 1 error, 866 ms average latency, 0 tokens.
- `gemini-3.8-flash`: 15 requests, 13 errors, 52.6 s average latency;
  displayed total 25,659 tokens, input 25,287, thoughts 313, output 59.

The displayed total and categories are preserved as reported. `/stats tools`
showed `find_lecture`: 1 call, 100% success, 21.0 s displayed average
duration; 1 authorization accepted, 0 rejected, 0 modified. The session also
displayed `API Error: exception TypeError: fetch failed sending request`.

The list-price estimate in the table applies the [Google Gemini 3.8 Flash
standard rate valid through 2026](https://ai.google.dev/gemini-api/docs/pricing)
of US$0.75 per million input tokens and US$3.75 per million output tokens,
including thinking tokens: 25,287 × 0.75 / 1,000,000 + (59 + 313) × 3.75 /
1,000,000 ≈ US$0.02036. This is a hypothetical estimate for the reported
session totals, not an exact charge or the cost of the single tool call. The
free tier, API errors and billing status were not independently audited.

In trial 2, `find_lecture` returned lecture 5 before Gemini CLI displayed
`Usage limit reached for gemini-3.8-flash`. No final model answer or complete
token statistics were confirmed, so no cost is calculated and trial 1's
numbers are not reused. Codex token counts and a comparable cost were not
available. The student's screenshots were described but not attached to this
repository.
