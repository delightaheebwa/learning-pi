# The LearnHarness hybrid teaching methodology

This page explains how the interrogation flow relates to
[`amosblomqvist/learnharness`](https://github.com/amosblomqvist/learnharness), and where the two
deliberately diverge. Use it as a reference when you change teaching behavior. The enforceable rules
live in `CONTRACT.md` (`G-interrogation-*`, `G-foundation-beats`, `G-clone-protocol`).

## The two shapes

LearnHarness is a teacher-first harness. It measures the learner's edge, plans a minimal dependency
tree to the goal, then teaches one reasoning step at a time. It checks after every step, as described
upstream in `docs/teaching-methodology.md` and `src/agent/prompts/teacher/*`. The terminal condition
is that the goal "feels obviously true", not that the learner can recite it.

This repo is an interrogation harness. The learner reads first and brings notes plus a closed-book
model. The Tutor triages the holes and attacks them. The learner owns every word of v1 and v2 and
produces every repair. The Tutor never teaches cold. It fills a hole only through a bounded repair
turn, after the learner's own repair has failed.

Those shapes conflict at one point. LearnHarness's teacher installs the next fact. This repo's Tutor
may not. The hybrid resolves the conflict by importing LearnHarness's measurement, planning, pacing,
and repair. It does not import LearnHarness's authorship.

> LearnHarness's "one reasoning step at a time" governs how much a legal reveal gives away, not
> whether the Tutor may teach cold. The learner still produces the repair, and v2 is still the
> learner's own words.

## What is imported

| LearnHarness | Here | Enforcement |
| :--- | :--- | :--- |
| Measure before planning | Bracket probe after v1, when the model is ambiguous | `quiz-audit` `context:"probe"`. SKILL Step 1.5. |
| Minimal dependency tree that prunes what the learner holds | Dependency-ordered triage (`requires`/`on_path`) that attacks the shallowest on-path root | Gate `triageGaps`. `fact-check` attack ordering. |
| Predict, teach, then check | Predict, attack, then check (`context:"predict"`, then one check after a repair) | `quiz-audit` predict rules. SKILL Step 3. |
| One reasoning step, checked | `autopsy` and hints past R2 install one step with its check | Gate `stepGaps`. `fact-check` §5. |
| Diagnose, repair, then re-check before building on the repair | Repair mode teaches the diagnosed gap one checked step at a time. It starts after a miss survives the hint ladder, or at once for a `missing` or structural gap. A fresh-surface check and the learner's own-words restatement close the repair. | Gate `repairGaps` and `NO_REPAIR_RECEIPT`. `fact-check` §4c. `quiz-audit` and `grade-audit` repair rules. |
| Unconditional truths first, with motivated discovery | `where_from` asks for conceptual entailment, never algebra. A hole that rests on a missing foundation is attacked after the foundation. | `fact-check` §10 and §11. Triage ordering. |
| The click, where the goal feels obviously true | Entailment check before the clone: "why must this hold now?" | `grade-audit` `qtype:"explain-back"`. |
| Question craft | Checks answerable from the session, application-first, diagnostic distractors, and answer-is-signal | `quiz-audit` §10. `grade-audit`. |
| Voice | No praise, no agreement bias, no performed profundity | `APPEND_SYSTEM.md`. |

## Answer brevity does not lower rigor

The review trace and the solo trace are content requirements, not prose requirements. The 3-line
trace must carry the cue, the mechanism, the direction check, and the extreme check. Keyword or
telegraphic phrasing is the default, and it is never docked. `grade-audit` grades the model, not the
wording (`G-review-no-mcq`, `G-practice-difficulty`). A conclusion-only trace fails as a missing
mechanism. It never fails for brevity. The clone is the exception where completeness matters. Its
transcript must carry a failure regime that states when the model breaks. `naive-student` tests
whether the explanation survives an uncharitable read (`G-clone-protocol`).

## Repair mode teaches the diagnosed gap

Repair mode is the one legal place where the Tutor teaches the material the learner is being tested
on. It is entered only after self-repair has failed.

| Diagnosis (`grade-audit` `miss_class`) | What happens first | Repair tactic |
| :--- | :--- | :--- |
| `cue`, where nothing came | A source return and a retrieval cue, one attempt | `source_return` or `retrieval_cue` |
| `discrimination`, where a confusable won | A contrasting-pair nudge, one attempt | `contrasting_pair` |
| `execution`, where the idea is right and the run is wrong | One worked step, then a re-run | `worked_step` |
| `structural`, where the held proposition is wrong | One verification nudge. If the learner cannot name the wrong model, repair mode follows. | `push_down` |
| triage `missing`, where the learner never learned it and there is no miss to diagnose | Nothing to cue, so repair mode at once | `full_teach` |

`careless` is re-checked, never repaired, so it is not a repair `miss_class`. For a `missing` triage
row, the repair declares the class that `grade-audit` returned, usually `cue`, and the `full_teach`
tactic.

The method is LearnHarness's one method at a smaller grain. Start from the unconditional truth the
gap rests on, or the nearest thing the learner already holds. Build one motivated reasoning step at
a time. Ask how the learner could have discovered this. Socratic first. Pose the step and let the
learner attempt it. Narrate the discovery in expository mode only when it is beyond cold reach or
the learner asked to be told. Check every step with one question. Never build on a step the learner
has not demonstrated. No wall of text can cover the missing ground.

The Tutor ships one step per turn. The `step` block has the same shape as an `autopsy` patch:
`index`, `total`, `fact`, `rests_on`, and `check`. A repair that installs several facts at once is a
lecture, and the gate withholds it. If the repair needs more steps, ship step 1 and wait for its
check answer.

"Fully repaired" is operational, not a feeling. The Tutor closes the repair with `status:"done"`,
which requires two things. First, it requires a fresh-surface check. The learner must answer that
check, and `grade-audit` must pass it with `repair_gap` naming this same gap. That check must not
re-ask the repair turn's own question, must not recite the Tutor's prose, and must not be graded for
another gap. Second, the Tutor needs the learner's own-words restatement, quoted verbatim. Until that
`done` turn renders, the attack battery is withheld (`NO_REPAIR_RECEIPT`, including at the retry cap).
The learner still authors v1 and v2. Repair mode never writes the model.

## What is deliberately not imported

The following list records what the hybrid leaves out and what it leaves alone.

- The hybrid does not import teacher-first cold lessons. The entry gate still requires the learner's
  material and a closed-book model before any interrogation.
- It does not import a methodology catalogue. LearnHarness has one method, not a menu. Repair selects
  a tactic from the diagnosed `miss_class`, and the only presentation choice is Socratic or
  expository per step. A free-form "pick a teaching technique" dispatcher would be unenforceable and
  would drift.
- It does not import reveal-and-move-on or bounded repair. Attempt caps and "if the repair fails,
  reveal and move on" are explicitly forbidden upstream and here. Repair is unbounded, and the
  learner must generate the correction. The hint ladder's 2/1/0 budget caps hints, not repair
  attempts.
- LearnHarness's practice-session pacing was considered for this change and deliberately left alone.
  The pacing is one problem per turn with a working-trace channel and a `conclude` record,
  retest-at-close, and the unfiltered thinking field. The review flow keeps its batched quiz and
  batched `grade-audit`, because the receipt economy depends on that batching. The practice doctrine
  already imports the hint ladder, miss taxonomy, ~85% band, inactive-state retrieval, and
  interleaving.
- It does not import Tutor-authored v2. A one-step `autopsy` is logged separately in `repair_steps[]`
  and is never merged into the learner's model. `MODEL_GHOSTWRITING` still blocks polished
  paraphrase.
- It does not show a visible plan map before triage. The dependency tree is the Tutor's attack plan.
  Showing it early would leak the structure the learner is meant to build.
- It keeps the `sure|hunch|no-idea` scale and `Attempts.json` calibration unchanged.
- It does not import symbolic derivations. "No derivations" now means no algebra, proofs, or hand
  computation. Conceptual one-step entailment is allowed and, at graduation, expected.

## The reveal boundary

A legal reveal is one of four things.

- a `hint` past R2, from the stuck ladder,
- an `autopsy` after an explicit "just tell me",
- an `idea` the learner asked for, or
- a repair turn after the learner's own repair attempt has failed.

Each reveal installs one new fact that rests on something the learner already holds, followed by one
check. If the repair needs more than one step, the Tutor ships step 1 and waits for the learner's
answer. The gate enforces this deterministically for `autopsy` and `repair`, through the `step`
block. `fact-check` and the stance enforce it for the R2+ and `idea` cases. Repair mode is the only
reveal that can continue for more than one step, and only while its gap stays open.

## Critique mode is not the interrogation hybrid

The critique flow (`[[FLOW:critique]]`) is the learner-led diagnosis loop, not
the LearnHarness hybrid. The learner brings an own-words model (explain-back) or
a source excerpt plus an interrogation; the Tutor returns one quoted diagnosis
and writes no next version. It reuses the reading mode's diagnose-never-rewrite
rule and none of the interrogation machinery: no entry gate, triage, dependency
tree, attack battery, hint ladder, repair mode, quiz batch, or graduation clone.

The flow exists because the interrogation hybrid is heavier than a plain
explain-back or a paragraph interrogation needs to be. Its unit is the learner's
artifact, not a curriculum position. Every diagnosis is fact-checked before it
renders, and both modes capture v1, the diagnosis, and v2 verbatim at close.

## Contract anchors

These contract rules anchor the behavior above.

- `G-interrogation-stance`: the stance, the bracket, one-step reveals, and the entailment check.
- `G-triage-shape`: orderable, acyclic attack tree.
- `G-foundation-beats`: `autopsy` step, `idea` foundation, and conceptual-entailment wording.
- `G-verifier-interrogation-audit`: predict context, one-step autopsy, and entailment grading.
- `G-clone-protocol`: entailment check before the clone.
- `G-review-no-mcq`: MCQs legal only in a bracket probe.
- `G-repair-trigger`: repair mode engages only after self-repair fails, and the miss class selects
  the tactic.
- `G-repair-method`: one gap, one bound step per teaching turn, Socratic-first.
- `G-repair-scope`: the repair teaches only the bound gap, and the learner authors v1 and v2.
- `G-repair-complete`: the battery waits for a graded fresh-surface pass and an own-words
  restatement.
- `C-critique-*`: the critique flow's turn kinds, fact-check binding, artifact-first rule,
  grounded verdicts, no-rewrite rule, both-mode capture, and no-machinery policy.
