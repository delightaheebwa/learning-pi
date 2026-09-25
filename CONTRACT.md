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
  only from a content-bound passing fact-check (≥85% coverage).
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
  note, a summary turn needs a `review-session-audit` receipt.
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

### Launcher & update gate

- **S-1** behavior lives here and in the tagged tests; it changes only through
  the revise door.
- **S-2** tests run against a synthetic fixture state; real learning state is
  never a fixture and never written by the harness.
- **S-3** every promotion is journaled in `versions.lock.json` and reversible
  with `pi-safe-update rollback`.
- **S-4** the launcher (`bin/pi`) never updates anything; `pi-safe-update` is
  the only path that changes versions.

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
`audit_gates` pass over real sessions. See `README.md`.
