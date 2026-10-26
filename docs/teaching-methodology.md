# Teaching methodology — the LearnHarness hybrid

How the interrogation flow relates to
[`amosblomqvist/learnharness`](https://github.com/amosblomqvist/learnharness), and where the two
deliberately diverge. Reference for changing teaching behaviour; enforceable rules live in
`CONTRACT.md` (`G-interrogation-*`, `G-foundation-beats`, `G-clone-protocol`).

## The two shapes

**LearnHarness** is a teacher-first harness. It measures the learner's edge, plans a minimal
dependency tree to the goal, then teaches one reasoning step at a time, checking after every step
(`docs/teaching-methodology.md` and `src/agent/prompts/teacher/*` upstream). The terminal condition is
that the goal "feels obviously true", not that it can be recited.

**This repo** is an interrogation harness. The learner reads first, brings notes plus a closed-book
model, and the Tutor triages and attacks the holes. The learner owns every word of v1/v2 and produces
every repair; the Tutor never teaches cold and never fills a hole.

Those shapes conflict at one point: LearnHarness's teacher *installs* the next fact; this repo's
Tutor may not. The hybrid resolves the conflict by importing LearnHarness's **measurement, planning,
and pacing** — not its authorship.

> LearnHarness's "one reasoning step at a time" governs **how much a legal reveal gives away**, not
> **whether the Tutor may teach cold**. The learner still produces the repair, and v2 is still the
> learner's own words.

## What is imported

| LearnHarness | Here | Enforcement |
| :--- | :--- | :--- |
| Measure before planning | **Bracket probe** after v1, when the model is ambiguous | `quiz-audit` `context:"probe"`; SKILL Step 1.5 |
| Minimal dependency tree; prune what is held | **Dependency-ordered triage** (`requires`/`on_path`); attack the shallowest on-path root | Gate `triageGaps`; `fact-check` attack ordering |
| Predict → teach → check | **Predict → attack → check** (`context:"predict"`, then one check after a repair) | `quiz-audit` predict rules; SKILL Step 3 |
| One reasoning step, checked | `autopsy` and hints past R2 install **one** step with its check | Gate `stepGaps`; `fact-check` §5 |
| Unconditional truths first; motivated discovery | `where_from` asks for **conceptual entailment** (never algebra); a hole resting on a missing foundation is attacked after the foundation | `fact-check` §10–11; triage ordering |
| The click — the goal feels obviously true | **Entailment check** before the clone ("why must this hold now?") | `grade-audit` `qtype:"explain-back"` |
| Question craft | Checks answerable from the session, application-first, diagnostic distractors, answer-is-signal | `quiz-audit` §10; `grade-audit` |
| Voice | No praise, no agreement bias, no performed profundity | `APPEND_SYSTEM.md` |

## What is deliberately not imported

- **Teacher-first cold lessons.** The entry gate still requires the learner's material and a
  closed-book model before any interrogation.
- **Tutor-authored v2.** A one-step `autopsy` is logged separately in `repair_steps[]` and is never
  merged into the learner's model. `MODEL_GHOSTWRITING` still blocks polished paraphrase.
- **A visible plan map before triage.** The dependency tree is the Tutor's attack plan; showing it
  early would leak the structure the learner is meant to build.
- **Numeric per-answer confidence.** The `sure|hunch|no-idea` scale and `Attempts.json` calibration are
  unchanged.
- **Symbolic derivations.** "No derivations" now means no algebra, proofs, or hand computation.
  Conceptual one-step entailment is allowed and, at graduation, expected.

## The reveal boundary

A legal reveal is one of:

1. a `hint` past R2 (the stuck ladder),
2. an `autopsy` after an explicit "just tell me", or
3. an `idea` the learner asked for.

Each installs **one** new fact resting on something the learner already holds, followed by **one**
check. If the repair needs more than one step, the Tutor ships step 1 and waits for the learner's
answer. The gate can only enforce this deterministically for `autopsy` (the `step` block); the R2+
and `idea` cases are enforced by `fact-check` and the stance.

## Contract anchors

- `G-interrogation-stance` — the stance, the bracket, one-step reveals, the entailment check.
- `G-triage-shape` — orderable, acyclic attack tree.
- `G-foundation-beats` — `autopsy` step, `idea` foundation, conceptual-entailment wording.
- `G-verifier-interrogation-audit` — predict context, one-step autopsy, entailment grading.
- `G-clone-protocol` — entailment check before the clone.
- `G-review-no-mcq` — MCQs legal only in a bracket probe.
