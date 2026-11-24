# Spec: `read-gate` — revise-door plumbing for the reading mode

Module of: `docs/specs/CAPABILITY-MAP-reading-mode.md` (approved 2026-11-24)

## Objective

Make it *possible* for pi to run a lightweight Sung-style reading session
without dismantling the existing interrogation system. This module delivers no
learner-visible behavior of its own; it delivers the flow entry point, the
router, the contract changes, and the tagged tests that `benchmark-session`,
`free-recall`, `model-diagnose`, and `benchmark-retrieval` hang off.

The user story: "I tell pi I'm going to read something, and a reading session
starts — not a teach session, not a review session."

## Tech Stack

- `.pi/prompts/read.md` — new prompt template carrying `[[FLOW:read]]` (today
  there are 8 prompt templates; this is the 9th).
- `.pi/APPEND_SYSTEM.md` — router additions ("I'm going to read…", "I'm
  reading…", "reading session") and the reading-mode stance paragraph.
- `.pi/skills/learning-read/` — new skill (today 5 skills; this is the 6th)
  owning the reading-session pipeline prose.
- `contracts/learning-core.json` + `CONTRACT.md` + `test/` — new `R-*`
  invariants for the reading flow, each bound to ≥1 passing tagged test, and
  updated resource lists (prompts 8→9, skills 5→6; agent count unchanged —
  the reading flow reuses the existing verifier set).
- `.pi/extensions/learning-gate/` — gate coverage for the new flow's turn
  kinds, only to the extent the behavior modules need it.

## Commands

- Verify (offline): `scripts/learn-check --no-load`
- Verify (full): `scripts/learn-check`
- Doc drift: `python3 scripts/check-docs`
- Diff floor: `node scripts/floor-guard.mjs`

## Project Structure

- New: `.pi/prompts/read.md`, `.pi/skills/learning-read/SKILL.md`
- Edited: `.pi/APPEND_SYSTEM.md`, `contracts/learning-core.json`,
  `CONTRACT.md`, `test/contract/check_learning_layer.py`, gate suites under
  `test/`
- Untouched: `.pi/skills/learning-teach/`, every existing invariant and its
  tests

## Code Style

New invariants follow the existing JSON shape exactly — id, severity, text,
and the test-name substrings that must have at least one passing test:

```json
{
  "id": "R-reading-flow-grounded",
  "severity": "hard",
  "text": "Every [[FLOW:read]] claims turn is grounded in the attached source text or the learner's verbatim words. A benchmark question, keyword, feedback item, or diagnosis with no traceable source anchor is withheld.",
  "tests": ["read_flow_grounded"]
}
```

`R-` prefix reserved for reading-mode invariants (G- = gate/graph, S-/P-/B- are
taken). Prose mirror in `CONTRACT.md` keeps the existing section format.

## Testing Strategy

- `test/contract/check_learning_layer.py`: resource lists updated (9 prompts,
  6 skills); each new `R-*` invariant covered by ≥1 passing `PASS <name>`
  substring; every listed test name matches a real test.
- Gate suites (`test/gate_test.mjs`, golden/redteam/judge where relevant):
  new cases for reading-flow turn shapes and grounding withholding.
- Existing tests: none removed; existing invariants: none edited.

## Boundaries

- Always: run `scripts/learn-check --no-load` before every commit; keep the
  contract diff additive; contract edits only in the single
  `revise(contract):` commit with the user's approval of the diff.
- Ask first: any change to an existing invariant, any new agent file, any
  change to the gate engine's core turn-tagging rule.
- Never: remove or reword an existing invariant to make room; edit vendored
  `.opencode/` or `state/Skills/`; weaken `CONSTRAINTS.md`.

## Success Criteria

1. Saying "I'm going to read X" in pi routes to `[[FLOW:read]]`, loads
   `learning-read`, and does not start a teach/review session.
2. `scripts/learn-check --no-load` passes with the new resource lists and
   `R-*` invariants bound to passing tests.
3. `/teach`, `/lesson`, `/continue`, `/review`, `/solo` behave exactly as
   before — verified by the untouched existing gate suites.
4. The commit touching `contracts/`, `CONTRACT.md`, or `test/` carries the
   `revise(contract):` subject and the user has approved the contract diff.

## Open Questions

- Turn-kind vocabulary for the reading flow (reuse `plan`/`claims`/`grade`
   vs. new `R-`-scoped kinds) — decided in the plan phase, not here.
