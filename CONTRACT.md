# CONTRACT — the behavior the learning system requires

This file defines **what the learning system expects**, independent of the pi
version, the extension packages, or how any of them speak. It is the thing the
update gate protects. Pi may churn; this contract must not change by accident.

Machine-readable form: [`contracts/learning-core.json`](contracts/learning-core.json).
Every invariant there carries an ID, a severity, and the test-name substrings
that must have at least one passing test. `scripts/learn-check` fails if an
active invariant has no passing test, or if a listed test name matches nothing.

## The two doors

| | **Update door** — `harness/pi-safe-update update` | **Revise door** — deliberate change |
|---|---|---|
| Trigger | a newer pi / extension package exists | **you** decide behavior should change |
| This contract | **frozen** | edited first, in the same commit as its tests and implementation |
| Tests | immutable | updated to match the new contract |
| Who reviews | the gate promotes only if every invariant still passes | you approve the contract diff |

The update door may **never** touch `contracts/`, `CONTRACT.md`, or `test/`.
That is what stops an automated repair from silently weakening verification.
Changing behavior is ordinary, deliberate work: edit the invariant, add/adjust
its tagged test, change the implementation, all in one reviewed commit.

## Invariants

### Gate (turn verification)

- **G-grade-requires-agreeing-audit** *(hard)* — a grade turn renders only with
  an agreeing `grade-audit` receipt; a verifier disagreement is rejected and its
  `correct_verdict` is surfaced (`GRADE_MISMATCH`). One batched `items[]`
  envelope may carry several learner answers from a single reply (one entry per
  answer); a mismatch surfaces the per-item corrections.
- **G-receipts-consumed-per-message** *(hard)* — a receipt is consumed by the
  message it verified; the same receipt cannot authorize a later turn.
- **G-partial-ungated** *(hard)* — an unfinished generation
  (`stopReason` error/aborted/length) passes through with its tag stripped and
  consumes no receipt.
- **G-ingest-requires-review** *(hard)* — an ingest summary renders only with a
  valid review verdict; a Clerk-completed ingest is not held hostage.
- **G-ingest-clerk-relay-flagged** *(policy)* — a verdict relayed by the Clerk
  (not an independent `review-gate` run) surfaces `⚠️ INGEST GATE`.
- **G-review-evidence-required** *(policy)* — a review verdict with no `evidence`
  list is unsubstantiated and flagged.
- **G-scout-banner-not-withhold** *(policy)* — a partial/missing Scout digest
  banners (`SOURCES INCOMPLETE` / `SCOUT DIGEST UNVERIFIED`), never withholds.
- **G-provider-fallback** *(policy)* — after two consecutive provider failures,
  offer (never force) a one-shot alternate-model re-dispatch.
- **G-no-duplicate-factcheck** *(hard)* — re-verifying an already-verified draft
  is blocked; a materially corrected post-ISSUES draft is allowed.
- **G-async-notify-mints** *(hard)* — async completion notifications mint
  content-bound receipts from the dispatch envelope; failures clear pending.
- **G-infer-claims-from-bound** *(hard)* — a dropped `claims` tag is recovered
  only from a content-bound passing fact-check (100% coverage with a judge, ≥85%
  on the legacy path).
- **G-infer-grade-quiz** *(hard)* — a dropped `grade`/`quiz` tag is inferred
  from a bound receipt or the single valid pending receipt; ambiguity withholds.
- **G-claims-requires-factcheck** *(hard)* — claims render only with a
  content-matched passing fact-check; a pending one withholds with a wait hint.
- **G-none-evasion-guard** *(hard)* — `[[TURN:none]]` over a verified or
  in-flight fact-check draft is withheld (`TURN_TAG_MISMATCH` /
  `FACT_CHECK_PENDING`).
- **G-non-learning-not-gated** *(hard)* — a session with no `[[FLOW:...]]`
  marker is never gated; messages pass through untouched.
- **G-tutor-audit-required** *(hard)* — after a Learning System write in
  teach/resume, a summary turn needs a passing `tutor-audit` over the files
  written; quiz/grade turns are not held hostage.
- **G-review-session-audit** *(hard)* — after the review flow writes its session
  note (or the delegated `review-clerk` run returns), a summary turn needs a
  `review-session-audit` receipt.
- **G-review-context-required** *(hard)* — a review's first claims/quiz turn is
  withheld (`NO_REVIEW_CONTEXT`) until a `review-scout` run has happened; a
  partial review digest banners, never withholds.
- **G-scout-required** *(hard)* — a new lesson's teaching claims are withheld
  (`NO_SCOUT_CONTEXT`) until a scout run has happened.
- **G-retry-cap** *(hard)* — repeated withheld turns are capped; beyond the cap
  the turn surfaces with `⛔ UNVERIFIED` rather than looping.
- **G-out-of-scope-demoted** *(policy)* — review findings that are all
  out-of-scope state bookkeeping are demoted to flags, so a clean target page is
  not re-reviewed forever.
- **A-subagent-result-shape** *(hard)* — the dispatch envelope is recovered from
  `tool_call` when pi-subagents redacts `task` on a foreground result.
- **G-receipt-shape-binds** *(hard)* — a receipt minted from a
  present-but-wrong-shape envelope must not satisfy its gate. A quiz/grade
  receipt with no bound text (a quiz-audit sent with `items[]` instead of
  `questions_json`, or a grade envelope with no question/answer/verdict)
  authorizes no emission; a write-gate receipt with no artifact list
  (tutor-audit `files`, review-session `written_files`, review-gate
  `target_files`) releases no summary. Only an envelope-less async completion
  notification falls back to unbound. One wrong-shape receipt must not bind every
  later turn.
- **G-quiz-binds-full-batch** *(hard)* — a `quiz-audit` receipt binds the whole
  emitted batch: the envelope's `rendered_content` (the full batch text) is the
  bound text the judge sees, and without it the derived bound text includes each
  item's `options`. A questions-only binding cannot strand a valid quiz turn as
  `QUIZ_AUDIT_STALE`.
- **G-dispatch-object-task** *(hard)* — verifier/worker dispatches go through the
  `dispatch` helper, which takes the JSON envelope as an **object** and runs the
  child through pi-subagents' structured delegation bridge (`subagent` is
  `exposure: "model-only"`, so the bridge is the only extension path). `dispatch`
  serializes the envelope and mints the gate receipt itself, so a model that emits
  an object `task` — the shape that dead-ends the `subagent` tool with
  `task: must be string` — still gets a bound receipt. The legacy `subagent`
  `workflow`/`args` forms are blocked and redirected to `dispatch`. Nothing in
  the prompt resources may spell a `subagent(` dispatch call.
- **G-viz-turn-requires-audit** *(hard)* — a `[[TURN:viz]]` message renders only
  with a passing, bound `viz-audit` receipt: missing → `NO_VIZ_AUDIT`, an
  `ISSUES` verdict → `VIZ_AUDIT_ISSUES`, a valid-but-unbound receipt →
  `VIZ_AUDIT_STALE`.
- **G-viz-audit-binds-spec-and-prose** *(hard)* — a `viz-audit` receipt binds
  only when its canonical `spec` equals the emitted fenced spec **and** its
  `rendered_content` covers the emitted text; a different spec, or a
  present-but-wrong-shape envelope missing the spec/`rendered_content`,
  authorizes no emission.
- **G-viz-standalone-turn** *(hard)* — a ```viz fence may only appear in a
  `[[TURN:viz]]` message; a viz block inside a claims or transition turn is
  withheld (`VIZ_REQUIRES_OWN_TURN`).
- **G-viz-spec-valid** *(hard)* — a `[[TURN:viz]]` message with no parseable
  ```viz JSON spec is withheld (`VIZ_SPEC_INVALID`).
- **G-viz-infer-from-bound** *(hard)* — a dropped viz tag is recovered from a
  bound `viz-audit` receipt (canonical spec match + prose coverage).

### The judge (model-based semantic decisions)

The gate can run a **judge**: a model (Gemini `gemini-3.5-flash-lite`, with
`gemini-3.5-flash` as an escalation) that answers the semantic questions the
deterministic code cannot. The judge only **sees and writes text** — it runs no
tool, writes no file, changes no state. The engine performs every action. When
no judge is configured, or the judge faults, the gate runs the legacy
deterministic path unchanged (G-judge-degraded-fallback).

- **G-turn-type-inferred** *(hard)* — turn tags are hints; the judge reads the
  turn type from the content. Verifier/notification channels are never gated.
- **G-full-coverage-binding** *(hard)* — a turn renders only when 100% of the
  emitted text is covered by the verifier's verified draft; any uncovered span
  blocks, and the remedy names the span.
- **G-pass-substantive** *(hard)* — a PASS the judge scores unsubstantiated
  (thin/none, missing items, no evidence) does not verify the turn.
- **G-issues-no-cap** *(hard)* — while a high/medium issue remains the gate
  keeps blocking and never dumps the turn as `⛔ UNVERIFIED`; the cap applies to
  every other reason.
- **G-verifier-dispute** *(policy)* — the same issue blocking three times is
  adjudicated by the judge (does it still apply?); if not, the engine releases
  the turn with `⚠️ VERIFIER DISPUTED`. The judge only answers.
- **G-receipt-source-is-verifier** *(hard)* — a receipt is the verifier's own
  statement; the judge never authors or rewrites receipt fields.
- **G-judge-degraded-fallback** *(policy)* — a judge fault falls back to the
  legacy checks; a learning turn never dead-ends on a judge fault.
- **G-judge-escalation** *(policy)* — a hard case (valid receipt not fully
  covering, no best receipt, or thin substantiveness) escalates from
  `gemini-3.5-flash-lite` to `gemini-3.5-flash`, budget-capped per day; a
  primary outage escalates before falling back to the legacy path.

The judge also writes the **ledger** (`~/.pi/agent/learning-gate/`: 
`receipts.ndjson`, `decisions.ndjson`) — receipt provenance for the weekly
audit and the accountability record for every decision.

### Launcher & update gate

- **S-1** behavior lives here and in the tagged tests; it changes only through
  the revise door.
- **S-2** tests run against a synthetic fixture state; real learning state is
  never a fixture and never written by the harness.
- **S-3** every promotion is journaled in `versions.lock.json` and reversible
  with `pi-safe-update rollback`.
- **S-4** the launcher (`bin/pi`) never updates anything; `pi-safe-update` is
  the only path that changes versions.
- **S-5** the end-to-end learner journeys (`harness/e2e-runner.py`, `test/e2e/`)
  replay real flows against a sandbox and read model access from the real agent
  dir read-only (credentials and model catalog copied into a throwaway 0700
  sandbox; packages never installed into the real agent). They are an **opt-in**
  gate step (`lpi e2e`, `learn-check --e2e`, `pi-safe-update update --e2e`), not
  a default. A failed journey never promotes and never patches code; it leaves a
  transcript and result JSON under `~/.cache/learning-pi/e2e-*`.

### Sidecars (existing suites)

- **P-1** `ops.py` resolves its root to a checkout containing
  `Learning System/Core` (not a hardcoded path).
- **P-2** `ops.py` rejects path escapes outside the workspace.
- **P-3** `ops.py state <track>` returns the concept table rows, not just the
  heading.
- **P-4** `audit_state.py` is read-only and prints a `STATE_AUDIT_FIXES:` JSON
  hint array.
- **P-5** `audit_gates.py` exits non-zero on error-level findings.

## Adding a newly installed extension

If a new extension participates in the learning flow, add its behavioral role
here (what receipts it mints, what turns it gates) and a tagged test. Do not
couple the test to the extension's internal shape — express it in domain terms
and let `pi-adapter/` (or a new adapter file) absorb the wire format.

## Residual risk (accepted)

Model-side drift — the server-side behavior of a model changing with no version
bump — cannot be pinned. It is caught by the fail-loud design (withhold +
banner, never corrupt state), the optional live smoke, and the weekly
`audit_gates` pass over real sessions. See `README.md`. The judge adds a second
model to this surface; it is bounded by the ledger, the legacy fallback, and the
free-tier budget (the gate degrades to the deterministic path when the budget is
spent).
