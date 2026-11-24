# Capability Map: Sung-style reading mode

Status: approved 2026-11-24. Module ids are stable; never renamed mid-initiative.

Source: `~/Documents/Justin Sung - The Current System for Learning Anything (2023-2026).md`
and the user's reference ChatGPT session (declare reading → benchmark → plain
keywords → mental model → assessment). The user's four scope decisions
(2026-11-24): new mode alongside `/teach` (nothing destroyed), diagnose-don't-rewrite
for mental models, fixed 1d/1w/1m benchmark shots, source text attached by the
learner. Fact-checking, free recall, and use-level retrieval were added at map
review.

| Module id | Responsibility | Depends on |
|---|---|---|
| `read-gate` | Revise-door plumbing: `[[FLOW:read]]` prompt, router entries, contract resource lists, skeleton invariants + tagged tests; gate/fact-check coverage extended to the reading flow | — |
| `benchmark-session` | Declare reading + attached text → stop point, outcome definition, 5 low / 5 mid / 5 high grounded questions written at use-level with real cues, plain keyword list | `read-gate` |
| `free-recall` | Closed-book dump after reading and at every retrieval session; checked against source; confidence-rated; feedback only after full generation | `read-gate` |
| `model-diagnose` | Learner presents mental model → grounded diagnosis of wrong/missing/misplaced; learner redraws; pi never rewrites the model | `read-gate` |
| `benchmark-retrieval` | +1d / +1w / +1m fixed shots (misses re-appear, never reset), free recall + benchmark questions, scores tracked vs 90/80/70 | `benchmark-session`, `free-recall` |

Build order: `read-gate` → `benchmark-session`, `free-recall`, `model-diagnose`
(three independent branches) → `benchmark-retrieval`.

Cross-module rules:

- The existing `/teach` interrogation flow (triage → attacks → repair ladder →
  graduation) is untouched. No invariant is removed; all contract changes are
  additive and land in **one** `revise(contract):` commit, approved by the user,
  after all modules are green.
- Every part of the reading flow runs under the existing verification gate:
  benchmark questions, keywords, free-recall feedback, and model diagnoses must
  be grounded in the attached source text and in the learner's verbatim words.
- Retrieval sessions enforce generate-before-feedback with confidence rated
  before any check is revealed ("retrieve in the way you will use it").

Specs, one per module, live alongside this map as `SPEC-<module id>.md`.
