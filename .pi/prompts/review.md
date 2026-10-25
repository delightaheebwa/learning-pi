---
description: Run a spaced-repetition review on the active learning track
---
[[FLOW:review]]
Run a spaced-repetition review. Load the `learning-system` skill and follow its Review flow.

First `dispatch` the `review-scout` agent to gather the context and build the due queue; the digest's `queue` is authoritative — use it verbatim and do not rebuild or re-sort it. Derive the active track and position from `Learning System/MISSION.md` and `CURRICULUM.md`; if they disagree, stop and report.

Reviews test cue selection and transfer, not recognition: compose **unlabeled, interleaved** items with the **3-line qualitative trace** (cue & principle → mechanism/knob-turn → direction & extreme check). **No MCQs, no calculation/derivation prompts.** Include composite scenarios when the queue has 3+ entries, at least one decoy/near-miss, one perturbation, one misapplication, and a **teach-the-clone** item for a `concept`/`design` entry. Before asking a queued concept, run `ops.py prereqs "<concept>"` and defer a downstream item when a direct prerequisite is fuzzy.

Ask the whole batch in ONE `[[TURN:quiz]]` message and verify it with ONE `quiz-audit` (`context:"review"`, `questions_json` + `rendered_content` = the exact full batch). No visuals until the answers are graded. Grade the reply with the clone phase first (`naive-student` when a teach-the-clone item was answered), then ONE batched `grade-audit` (`items[]` with traces, `pow`, `qtype`, `confidence`, `tutor_turns`, `naive_student_receipt`).

Then present verified feedback (`fact-check` `turn_kind:"grade_feedback"` + `grade_verdicts`, smallest visual that carries it) and **pause for learner questions in the same turn**. Persist nothing until the learner explicitly says "no questions" (silence is not consent). Answer questions through the inquiry loop with verified `answer`/`repair` turns, re-grading any disputed item, then pause again.

At the close, `dispatch` ONE `review-clerk` (`REVIEW_WRITES` envelope with the exact transcript, verdicts, battery outcomes, `dependency_events`, and mistakes), then ONE `review-session-audit` on the exact writes. A `PASS` releases the verified closing summary; `ISSUES` withholds it until the writes are fixed and a fresh audit returns zero issues — no cycle cap. You write no state yourself.

Begin every assistant message with a turn tag; dispatch each verifier once (`dispatch({ agent, task: { ...envelope... } })`, foreground) and emit the verified draft unchanged.
