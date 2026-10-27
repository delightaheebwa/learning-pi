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
every repair; the Tutor never teaches cold and fills a hole only through a bounded repair turn, after
the learner's own repair has failed.

Those shapes conflict at one point: LearnHarness's teacher *installs* the next fact; this repo's
Tutor may not. The hybrid resolves the conflict by importing LearnHarness's **measurement, planning,
pacing, and repair** — not its authorship.

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
| Diagnose → repair → re-check before building on it | **Repair mode**: after a miss survives the hint ladder (or at once for a `missing`/structural gap), teach the diagnosed gap one checked step at a time, then a **fresh-surface check** and the learner's own-words restatement close it | Gate `repairGaps` + `NO_REPAIR_RECEIPT`; `fact-check` §4c; `quiz-audit`/`grade-audit` repair rules |
| Unconditional truths first; motivated discovery | `where_from` asks for **conceptual entailment** (never algebra); a hole resting on a missing foundation is attacked after the foundation | `fact-check` §10–11; triage ordering |
| The click — the goal feels obviously true | **Entailment check** before the clone ("why must this hold now?") | `grade-audit` `qtype:"explain-back"` |
| Question craft | Checks answerable from the session, application-first, diagnostic distractors, answer-is-signal | `quiz-audit` §10; `grade-audit` |
| Voice | No praise, no agreement bias, no performed profundity | `APPEND_SYSTEM.md` |

## Repair mode — teaching the diagnosed gap

Repair mode is the one legal place the Tutor *teaches* the material the learner is being tested on.
It is entered only after self-repair has failed:

| Diagnosis (`grade-audit` `miss_class`) | What happens first | Repair tactic |
| :--- | :--- | :--- |
| `cue` (nothing came) | source return + a retrieval cue, one attempt | `source_return` / `retrieval_cue` |
| `discrimination` (a confusable won) | a contrasting-pair nudge, one attempt | `contrasting_pair` |
| `execution` (right idea, wrong run) | one worked step, re-run | `worked_step` |
| `careless` | re-read/re-check only | — (no repair mode) |
| `structural` (the held proposition is wrong) | one verification nudge; if the learner cannot name the wrong model, repair mode | `push_down` |
| `missing` (never learned) | nothing to cue — repair mode at once | `full_teach` |

**The method is LearnHarness's one method, at a smaller grain:** start from the unconditional truth
the gap rests on (or the nearest thing the learner already holds), and build **one motivated
reasoning step at a time** — *how could the learner have discovered this?* Socratic first: pose the
step and let the learner attempt it; narrate the discovery (expository) only when it is beyond cold
reach or the learner asked to be told. **Check every step** with one question, and never build on a
step the learner has not demonstrated. There is no wall of text that "covers" the missing ground.

**One step per turn.** The `step` block is the same shape as an `autopsy` patch
(`index`/`total`/`fact`/`rests_on`/`check`); a repair that installs several facts at once is a
lecture and is withheld. If the repair needs more steps, ship step 1 and wait for its check answer.

**"Fully repaired" is operational, not a feeling.** The Tutor closes the repair with
`status:"done"`, which requires both (1) a **fresh-surface** check the learner answered and
`grade-audit` passed — not a re-ask of the repair turn's own question, not a recital of the Tutor's
prose — and (2) the learner's own-words restatement, quoted verbatim. Until that `done` turn
renders, the attack battery is withheld (`NO_REPAIR_RECEIPT`). The learner still authors v1 and v2;
repair mode never writes the model.

## What is deliberately not imported

- **Teacher-first cold lessons.** The entry gate still requires the learner's material and a
  closed-book model before any interrogation.
- **A methodology catalogue.** LearnHarness has one method, not a menu: repair selects a *tactic*
  from the diagnosed `miss_class`, and the only presentation choice is Socratic vs. expository per
  step. A free-form "pick a teaching technique" dispatcher would be unenforceable and drift.
- **Reveal-and-move-on / bounded repair.** Attempt caps and "if the repair fails, reveal and move
  on" are explicitly forbidden upstream and here: repair is unbounded, and the learner must
  generate the correction. (The hint ladder's 2/1/0 budget caps *hints*, not repair attempts.)
- **LearnHarness's practice-session pacing.** Considered for this change and deliberately left
  alone: one problem per turn with a working-trace channel and a `conclude` record, retest-at-close,
  and the unfiltered thinking field. The review flow keeps its batched quiz + batched `grade-audit`
  (the receipt economy depends on it); the practice doctrine already imports the hint ladder, miss
  taxonomy, ~85% band, inactive-state retrieval, and interleaving.
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
2. an `autopsy` after an explicit "just tell me",
3. an `idea` the learner asked for, or
4. a **repair turn** after the learner's own repair attempt has failed.

Each installs **one** new fact resting on something the learner already holds, followed by **one**
check. If the repair needs more than one step, the Tutor ships step 1 and waits for the learner's
answer. The gate enforces this deterministically for `autopsy` and `repair` (the `step` block); the
R2+ and `idea` cases are enforced by `fact-check` and the stance. Repair mode is the only reveal that
can continue for more than one step, and only while its gap stays open.

## Contract anchors

- `G-interrogation-stance` — the stance, the bracket, one-step reveals, the entailment check.
- `G-triage-shape` — orderable, acyclic attack tree.
- `G-foundation-beats` — `autopsy` step, `idea` foundation, conceptual-entailment wording.
- `G-verifier-interrogation-audit` — predict context, one-step autopsy, entailment grading.
- `G-clone-protocol` — entailment check before the clone.
- `G-review-no-mcq` — MCQs legal only in a bracket probe.
- `G-repair-trigger` — repair mode engages only after self-repair fails (miss-class → tactic).
- `G-repair-method` — one gap, one bound step per teaching turn, Socratic-first.
- `G-repair-scope` — the repair teaches only the bound gap; the learner authors v1/v2.
- `G-repair-complete` — the battery waits for a graded fresh-surface pass + own-words restatement.
