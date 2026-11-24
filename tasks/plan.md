# Implementation Plan: Sung-style reading mode

Specs: `docs/specs/CAPABILITY-MAP-reading-mode.md` + `docs/specs/SPEC-{read-gate,benchmark-session,free-recall,model-diagnose,benchmark-retrieval}.md` (approved 2026-11-24). Task list: appended to `tasks/todo.md` under "Reading mode implementation todo" (the solo-first pilot's open tasks stay untouched above it).

## Overview

Add a lightweight reading mode as a new `[[FLOW:read]]` flow alongside teach/review/solo: declare reading + attached text → session brief (stop point, outcome, 15 grounded benchmark questions at 5 low / 5 mid / 5 high, plain keywords) → free-recall dump with confidence marks and a quoted check → mental-model diagnosis (diagnose, never rewrite) → benchmark questions due at +1d / +1w / +1m through the existing review machinery, scored against 90/80/70. The `/teach` interrogation flow is untouched; every contract change is additive and lands in one `revise(contract):` commit approved by the user.

## Architecture Decisions

1. **`read` becomes a real gated flow.** Today an unknown `[[FLOW:read]]` silently fails open (`primitives.ts:51` `FLOW_TAG_RE`, `primitives.ts:63` `Flow` union, `engine.ts:138` `foundationApplies` gate it out as `"other"` — no gating). The flow is registered so the one-turn-tag, full-draft, and grounding machinery applies, which is what "fact-checked like the rest of the system" requires.
2. **Reuse the existing turn-kind vocabulary; add none.** The 9 global kinds carry only light shape checks except `triage|attack|autopsy`, which the reading flow never uses. Mapping: session brief → `plan`; free-recall check and model diagnosis → `answer`; retrieval sessions reuse the existing `[[TURN:quiz]]`/`[[TURN:grade]]` machinery with `qtype free-recall` (already a valid enum value, and MCQ is already contract-banned outside probes — both specs satisfied for free).
3. **9th prompt, 6th skill, zero new agents.** `.pi/prompts/read.md`, `.pi/skills/learning-read/`. The reading flow reuses `fact-check`, `quiz-audit`, `grade-audit`, `clerk`, `review-clerk`, and `review-session-audit`. The agent count stays as-is. Bonus: the concept/design clone mandate is type-gated, so benchmark-typed items are naturally exempt from graduation clones — the user's "no clones" decision falls out of the existing rule unchanged.
4. **Benchmark is a fifth ops.py type with fixed-advance semantics.** `DEFAULT_INTERVALS` gains `"benchmark": [1, 7, 30]`. Unlike the adaptive ladders, every benchmark attempt advances `interval_index` regardless of pass/fail (never reset — user decision). A miss additionally writes a Mistakes row, which is exactly how the queue already makes items re-appear at the next session. Graduation after the third shot follows the existing clerk-prose pattern (far-future `next_review` + graduated marking); ops.py has no code graduation transition today and doesn't need one.
5. **Per-level scores live on attempt records; reports are derived.** `ops.py attempt` gains a validated optional `--level low|mid|high` stored on the attempt record (record-only, never a scheduling input — same rule as `targets[]`). Hit rates per level derive from `Attempts.json`; the score report is written into the session note by `review-clerk` and tallied by `review-session-audit`, which learns the fifth schedule in the same prose updates that today name the four.
6. **Commit sequencing (CI constraint drives it).** The repo requires every commit touching `CONTRACT.md`, `contracts/`, or `test/` to carry a `revise(contract):` subject, and the user approved a single coherent contract diff. So: Phase 1–3 tasks land as ordinary commits touching only `.pi/` and `state/` (the contract resource checks are presence-based — extra prompt/skill files don't fail them, and every existing suite must stay green at every commit); the new gate tests, `R-*` invariants, `CONTRACT.md` prose, and the expected-resource list updates all land together in the single final `revise(contract):` commit, after the user has seen and approved the diff. The contract version field bumps in that commit; its value is read from the JSON, never restated in prose.

## Task List

### Phase 1: Foundation (`read-gate`)

- [ ] Task R1: Register the `read` flow in the gate engine
- [ ] Task R2: Prompt, skill skeleton, and router entries

### Checkpoint 3: reading-mode foundation

### Phase 2: Session behavior (three parallel branches)

- [ ] Task B1: Session brief (`benchmark-session`)
- [ ] Task F1: Free recall (`free-recall`)
- [ ] Task M1: Model diagnosis (`model-diagnose`)

### Checkpoint 4: session dry-run end to end

### Phase 3: Retrieval (`benchmark-retrieval`)

- [ ] Task P1: ops.py benchmark type + attempt `--level`
- [ ] Task P2: Benchmark ledger + queue integration
- [ ] Task P3: Retrieval session shape and close

### Checkpoint 5: retrieval dry-run

### Phase 4: Revise door

- [ ] Task V1: Author the contract change (invariants + tests)
- [ ] Task V2: User-approved `revise(contract)` commit + docs

### Final checkpoint: one real reading session + the +1d shot

Full acceptance criteria, verification commands, dependencies, and file lists per task live in `tasks/todo.md` (the task list target).

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Adding `read` to `foundationApplies` accidentally arms teach-only shape checks (repair sequencing, attack menu) in reading sessions | High | Task R1 audits every flow comparison in the engine (`engine.ts` flow checks around lines 326–876) before touching `foundationApplies`; the untouched gate suites must stay green |
| Presence-based resource checks may not tolerate extra prompt/skill files mid-build (assumed) | Medium | Task R2 verifies `learn-check --no-load` after adding the files; if not tolerant, the resource-list edits move from V1 into an early revise-door commit instead of ordinary commits |
| `test/contract/load_probe.py` may pin prompt-template counts (7 templates noted in its docstring) | Medium | Checked when the 9th prompt lands; expectation updates go in the V1 commit |
| Queue slot policy (default 5 slots) vs. 15 benchmark questions per session | Medium | Task P2 groups benchmark items under one reading-session row/track so a due benchmark session enters the queue as one unit |
| V1 is a large single commit (the door requires invariant + test + implementation together) | Medium | Phases 1–3 are already landed and green as ordinary commits, so V1's diff is only contract + tests + resource lists; user reviews it before it commits |
| 15 rows per reading session bloating `Active Concepts` | Low | One row per reading session (not per question); questions live in the benchmark ledger file |

## Open Questions

All spec-level open questions are resolved by the mechanism audit: turn-kind vocabulary (reuse the existing nine), persistence shape (benchmark ledger + `level` on attempts), close machinery (review-session-audit with the fifth schedule + tally extension). No user input is blocking; the one remaining approval is the V2 contract diff, which is by design.

## Verification commands

- Offline gate + contract: `scripts/learn-check --no-load`
- Full (with candidate-pi load probe): `scripts/learn-check`
- Doc drift: `python3 scripts/check-docs`
- Skill-pack integrity: `scripts/check-skills`
- Diff floor vs `origin/main`: `node scripts/floor-guard.mjs`
- State tooling: `python3 -m unittest discover -s state/scripts -p '*_test.py'` (or the `--with-sidecars` pass of learn-check)
