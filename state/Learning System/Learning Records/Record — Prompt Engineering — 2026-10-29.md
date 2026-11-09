# Record — Prompt Engineering — 2026-10-29

- **Date:** 2026-10-29 (interrogation started 2026-10-28, resumed and completed)
- **Lesson:** Phase 11 L01 — Prompt Engineering (LLM Engineering track)
- **Concepts:** Prompt Engineering (primary); touches: temperature/determinism distinction, chain-of-thought conditionality, eval harness design

## What was learned (learner-owned, all captured verbatim in the lesson file)

1. **Instruction→distribution mechanism (from 2026-10-28, reused heavily):** a prompt conditions each next-token distribution; vague instructions leave fork arms unresolved so the probability mass spreads (generic output); precise instructions delete arms so mass concentrates (narrow, more deliberate output). "Models take prompts literally = they take what conditioning of the next token distribution they imply seriously."
2. **The measurement layer is the ruler, and the ruler is fixed expected outputs:** "The prompt harness holds the set of expected outputs and the outputs we actually received, allowing us to compare the two sets for any regression. When we make a change, the prompt runs." Old-vs-new diffing is a reading aid, never the verdict — "You compare what you got against what you expected."
3. **Sampling determinism is not quality:** temp 0 "makes the model pick the top choice in the next token distribution every time" but "won't change whether the output is good or not" — used correctly across the session (the concentration-as-quality detour was killed by this very distinction).
4. **Failure regime 1 — over-specific role:** "the model gets biased toward a very small subset of training data … it will hallucinate" — ground-truthed to Rohit's "very little high-quality text at that intersection."
5. **Failure regime 2 — chain-of-thought scale conditionality:** "if step one builds on a flawed or unfounded premise, the next step is built on that shaky foundation … pollutes the rest of the response"; 10-40% CoT gains "is for models greater than approximately 100 billion parameters"; below that, "better for smaller models to generate in one shot." The Rohit-vs-Wei contradiction was resolved by the learner as a scope boundary, not a wording shuffle.
6. **Ruler independence (sabotage battery):** "the model writes what it sees as a good, expected output … poisons the rest of the chain of versions" — a model judge is a scorer, not a ruler; what remains missing is "what the human actually wants," authored and held outside the judged system.
7. **When the ruler is unnecessary:** one-off responses — a single judgment event, no version stacking, no drift to catch; repeated versions are exactly why a fixed anchor is needed (entailment check, broken half produced after two misses).

## Evidence — highest Bloom level demonstrated

- **Evaluate:** clone task decision — the naive-student, running the learner's v2 verbatim, rejected a 7B-model expert-persona + step-by-step proposal on both failure regimes and routed the version comparison through the ruler (seeded "more constraints always help" refuted twice).
- **Analyze:** the Rohit-vs-Wei CoT contradiction resolved as a scope clash with a causal mechanism (pollution by conditioning) located inside the learner's own arms-and-mass model.
- **Apply:** harness walk-through of a new prompt version end-to-end; the caretaking of the temp-0 distinction across five different surfaces without relapse.

## Model evolution (v1 → breaking case → v2)

- **v1 (2026-10-28, hand-written):** "Prompt engineering is the process of tweaking the prompt in order to get the desired quality results" — no measurement layer, no failure regime, no mechanism.
- **Breaking cases:** the v1/v2/v3 article oscillation (no ruler → regression invisible); the concentration-as-quality detour; the self-judge sabotage.
- **v2 (2026-10-29, verbatim in lesson file):** drift-measured prompt work + conditioning mechanism + compulsory measurement layer with the one-off boundary + two failure regimes + the harness as nearest tool.

## State / open items

- Attempts: 30 total (17 pass / 13 fail), `interval_index` 3, `consecutive_correct` 3, `next_review` 2026-11-28, `feynman` pass (naive-student clone).
- Open in Mistakes.md: 2026-10-28 mechanism row and pause exit-ticket row (active); NEW clone-blind-spots row (active): too-specific threshold/advance test, regime coexistence, the vague↔specific middle.
- Untaught material available for later lessons: temperature/top-p mechanics, prefill contradiction, PE2 limits, Rohit's Johnny citation error (real), the lesson's "build it" code section.
- Curriculum: Phase 11 L01 complete; next curriculum target Phase 11 L02, with the Phase 1 L10 branch (Kernel PCA) still paused at Checkpoint 6/6, mini 1/3.
