# ADR-0001: Keep the weekly gate audit and the e2e runner as separate transcript readers

- Status: Accepted
- Date: 2026-10-28
- Deciders: architecture review (learning-pi)

## Context

Two Python tools read pi session transcripts and the verdict markers inside them.

- `pi/audit_gates.py` handles post-hoc provenance. It correlates each dispatched subagent run with
  its `subagent-artifacts/<runId>_<agent>_meta.json` metadata. It then asks whether a claimed verdict
  is backed by a real run. Its only scheduled consumer is a weekly human-triage log
  (`harness/audit-recent-sessions.sh`, exit 0 always). `harness/e2e-runner.py` also records
  `audit_gates` output for human triage, never for pass or fail.
- `harness/e2e-runner.py` checks liveness. It decides whether the expected agents ran and whether
  assertion substrings appear in the transcript. It merges async `subagent-notify` notices and
  deliberately skips error results.

A 2026-10-28 architecture review proposed a third shape. The proposal was to collapse both tools
into one deep `pi/transcript.py` with a single `Run` and `Receipt` reader. The argument was that one
wire format has three divergent recognizers, and the third is the TypeScript gate's marker matchers.

The review did not survive verification.

- The consumers are a Sunday human-triage log and opt-in tooling. That tooling is not in
  `learn-check` defaults, is absent from CI, and last ran three weeks ago. Stakes are low. A
  divergence produces a spurious or missing log line, never a gate decision.
- The readers answer different questions with opposite semantics. Provenance comes from artifact
  metadata and recorded errors. Liveness comes from async notices with error results skipped. One
  interface would need flags that re-create both branches. That is a shallow umbrella module, not a
  deep one.
- Both readers have zero tests. Unifying them would be untested surgery on working diagnostics for a
  log-only defect.
- The TypeScript gate cannot share a Python module. The cross-language seam is the wire format
  itself, pinned by `CONTRACT.md` and `contracts/learning-core.json`.

## Decision

Do not unify `pi/audit_gates.py` and `harness/e2e-runner.py` behind a shared transcript-reader module.
Keep each reader where it is, answering its own question.

One real defect was found. `audit_gates`'s marker regexes were stricter than the live gate's, so a
lowercase or pretty-printed marker could read as "no verdict" while the gate accepted it. The fix
keeps the marker matchers in step with
`.pi/extensions/learning-gate/gate-core/primitives.ts` using case-insensitive presence matching. A
shared module is not the fix. The gate's prose fallback (`N errors, M warnings`) is intentionally not
mirrored. `audit_gates` reads the whole session, so the fallback would flag the learner's own prose.

## Consequences

- Two small readers remain, each with a single consumer and its own semantics.
- A marker-format change must be applied in `primitives.ts` and the two Python marker regexes. The
  comment above `REVIEW_MARKER_RE` names the pair.
- No test suite covers either reader yet. Adding one for `audit_state.py`'s rule table, a separate
  candidate, would be the natural first net in this area.

## Revisit when

- A third consumer of session JSONL appears. Then the seam is real and the reader earns a module.
- `audit_gates` or the e2e runner gains a pass or fail consumer. Then divergence becomes load-bearing
  and needs executable coverage.
