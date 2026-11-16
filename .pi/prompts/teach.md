---
description: Stress-test the learner's model of a topic or source
argument-hint: "<topic-or-source>"
---
[[FLOW:teach]]

Stress-test the learner's own model. Load the `learning-teach` skill and run its interrogation flow. Do not teach the topic cold.

## Entry gate

If the learner has not brought notes or material and a closed-book model in their own words, send one reading brief. State exactly what to read and what to attempt. Verify the brief with `fact-check` (`turn_kind:"plan"`). Then stop. Do not preview the mechanism, summarize the reading, or probe before the model arrives.

Their model needs 3 to 6 lines covering the problem, the mechanism, a failure regime, and the nearest-neighbour tool.

## Interrogation

Once the model arrives:

1. Capture v1 verbatim.
2. Grade it with `grade-audit` (`qtype:"free-recall"`).
3. If v1 is ambiguous, bracket the edge with one short `context:"probe"` batch.
4. Present a verified `turn_kind:"triage"` table. Mark each row `solid`, `missing`, or `suspect`. Quote the learner for every suspect row and cite a source for every missing row. Order the rows with `requires` and `on_path`.
5. Attack the shallowest on-path root first. Allow one non-solid item and exactly one `attack` subtype per turn. Use `mechanism`, `counterexample`, `perturbation`, `source_clash`, `sabotage`, or `synthesis`.
6. Ask for a prediction before the attack (`context:"predict"`, one open question, not graded).
7. Pause after each grade. Run one check on the repaired claim.

## Repair mode

When the learner's own repair fails, or the gap is `missing`, enter repair mode. Use one `turn_kind:"repair"` turn bound to that gap. Teach one checked step at a time, Socratic first, starting from the unconditional truth the gap rests on. Close the repair only after a graded fresh-surface pass and the learner's own-words restatement (`repair.status:"done"`). Withhold the attack battery until then.

On "just tell me", use a `turn_kind:"autopsy"` patch labeled as a patch. Carry exactly one `step:{index,total,fact,rests_on,check}`. Log `just_tell_me` and `repair_steps[]`. Close with that check.

## Graduation

Capture v2 verbatim. Run the entailment check ("why must this hold now?", `explain-back`). For `concept` and `design` types, run the `naive-student` clone (`pow:"clone"`). Run any battery item not already exercised. Write the four handoff artifacts once. Dispatch `tutor-audit`. Then auto-ingest inline with `clerk` and `review-gate` before the completion summary.

Make the completion summary an attack report. Name what was exposed, the v1-to-v2 scar, and what needs another session. Do not write a lesson summary.

## Every turn

Begin every assistant message with a turn tag. Dispatch each verifier once in the foreground with `dispatch({ agent, task: { ...envelope... } })`. Emit the verified draft unchanged. `turn_kind` is required on every teach and resume claims turn. `triage` carries `triage[]`. `attack` carries exactly one `attack` subtype. `autopsy` carries one `step` block. Only `idea` carries the four-beat `foundation`.
