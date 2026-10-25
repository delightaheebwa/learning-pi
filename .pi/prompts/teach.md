---
description: Stress-test the learner's model of a topic or source
argument-hint: "<topic-or-source>"
---
[[FLOW:teach]]
Stress-test the learner's own model of the topic/source. Load the `learning-teach` skill and run its interrogation flow; do not teach the topic cold.

Entry gate first: if the learner has not brought (1) notes/material and (2) a closed-book model in their own words (3–6 lines: problem, mechanism, failure regime, nearest-neighbour tool), send one reading brief — exactly what to read and what to attempt — verify it with `fact-check` (`turn_kind:"plan"`), and stop. Never preview the mechanism, summarize the reading, or probe before the model arrives.

Once the model arrives: capture v1 verbatim → grade it (`grade-audit`, `qtype:"free-recall"`) → present a verified `turn_kind:"triage"` table (`solid`/`missing`/`suspect`, with a learner quote for every suspect row and a source citation for every missing row) → attack one non-solid item per turn with exactly one `attack` subtype (`mechanism|counterexample|perturbation|source_clash|sabotage|synthesis`) → pause after each grade. Never fill the hole; the learner produces the repair. On "just tell me", use a `turn_kind:"autopsy"` patch labeled as a patch, log `just_tell_me`, and immediately ask one perturbation on the patched model.

At the end: capture v2 verbatim, run the `naive-student` clone (`pow:"clone"`) for `concept`/`design` types, run any battery item not already exercised, write the four handoff artifacts once, dispatch `tutor-audit`, then auto-ingest inline (`clerk` → `review-gate`) before the completion summary. The completion summary is an attack report (what was exposed, the v1→v2 scar, what still needs another session), not a lesson summary.

Begin every assistant message with a turn tag; dispatch each verifier once with `dispatch({ agent, task: { ...envelope... } })` (foreground) and emit the verified draft unchanged. `turn_kind` is required on every teach/resume claims turn; `triage` carries `triage[]`, `attack` carries exactly one `attack` subtype, and only `idea` carries the four-beat `foundation`.
