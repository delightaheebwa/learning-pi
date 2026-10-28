# ADR-0001 — Keep the weekly gate audit and the e2e runner as separate transcript readers

- **Status:** Accepted
- **Date:** 2026-10-28
- **Deciders:** architecture review (learning-pi)

## Context

Two Python tools read pi session transcripts and the verdict markers inside them:

- `pi/audit_gates.py` — post-hoc provenance. Correlates each dispatched subagent
  run with its `subagent-artifacts/<runId>_<agent>_meta.json` metadata and asks
  whether a claimed verdict is backed by a real run. Its only scheduled consumer
  is a weekly human-triage log (`harness/audit-recent-sessions.sh`, exit 0
  always); `harness/e2e-runner.py` also records its output for human triage, never
  for pass/fail.
- `harness/e2e-runner.py` — liveness. Decides whether the expected agents ran and
  whether assertion substrings appear in the transcript; it merges async
  `subagent-notify` notices and deliberately skips error results.

A 2026-10-28 architecture review proposed a third shape: collapse both into one
deep `pi/transcript.py` (a single `Run`/`Receipt` reader), on the grounds that
one wire format has three divergent recognizers (the third being the TypeScript
gate's marker matchers).

The review did not survive verification:

- The consumers are a Sunday human-triage log and opt-in tooling (not in
  `learn-check` defaults, absent from CI, last run three weeks ago). Stakes are
  low; a divergence produces a spurious or missing log line, never a gate
  decision.
- The readers answer **different questions** with opposite semantics (provenance
  from artifact metadata and recorded errors vs liveness from async notices with
  error results skipped). One interface would need flags that re-create both
  branches — a shallow umbrella module, not a deep one.
- Both readers have zero tests. Unifying them would be untested surgery on
  working diagnostics for a log-only defect.
- The TypeScript gate cannot share a Python module; the cross-language seam is
  the wire format itself, pinned by `CONTRACT.md` and `contracts/learning-core.json`.

## Decision

Do **not** unify `pi/audit_gates.py` and `harness/e2e-runner.py` behind a shared
transcript-reader module. Keep each reader where it is, answering its own
question.

The one real defect found — `audit_gates`'s marker regexes were stricter than
the live gate's, so a lowercase or pretty-printed marker could read as "no
verdict" while the gate accepted it — is fixed by keeping the marker matchers in
step with `.pi/extensions/learning-gate/gate-core/primitives.ts` (case-insensitive
presence matching), not by a shared module. The gate's prose fallback
(`N errors, M warnings`) is intentionally not mirrored: `audit_gates` reads the
whole session, so it would flag the learner's own prose.

## Consequences

- Two small readers remain, each with a single consumer and its own semantics.
- A marker-format change must be applied in `primitives.ts` and the two Python
  marker regexes; the comment above `REVIEW_MARKER_RE` names the pair.
- No test suite covers either reader yet; adding one for `audit_state.py`'s
  rule table (a separate candidate) would be the natural first net in this area.

## Revisit when

- A third consumer of session JSONL appears (then the seam is real and the
  reader earns a module), or
- `audit_gates` or the e2e runner gains a pass/fail consumer (then divergence
  becomes load-bearing and needs executable coverage).
