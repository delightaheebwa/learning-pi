---
description: Run a spaced-repetition review on the active learning track
---
[[FLOW:review]]

Run a spaced-repetition review. Load the `learning-system` skill and follow its Review flow.

## Context and queue

Dispatch `review-scout` first to gather context and build the due queue. The digest's `queue` is authoritative. Use it verbatim. Do not rebuild or re-sort it. Derive the active track and position from `Learning System/MISSION.md` and `Learning System/CURRICULUM.md`. If they disagree, stop and report.

## Compose the batch

Reviews test cue selection and transfer, not recognition. Use unlabeled, interleaved items with a 3-line qualitative trace: cue and principle, mechanism or knob turn, then direction and extreme check. Terse and keyword lines are the default. Form is never graded; content is. All three lines are still required.

For a teach-the-clone item, the transcript must carry what the concept is, when and why it applies, the mechanism in one full causal clause, a failure regime, and the nearest-neighbour contrast.

Do not use MCQs. Do not use calculation or derivation prompts.

Include composite scenarios when the queue has 3 or more entries, at least one decoy or near miss, one perturbation, one misapplication, and the teach-the-clone item for a `concept` or `design` entry. Before asking a queued concept, run `ops.py prereqs "<concept>"`. Defer a downstream item when a direct prerequisite is fuzzy.

When the digest's `prior_knowledge` names graph propositions or chains for an item, copy their ids into that question's `targets[]`. Never invent ids. Omit the field when there are none. Carry the ids onto the grade item and into `REVIEW_WRITES.grade_verdicts[].targets`.

## Ask, verify, and grade

Ask the whole batch in one `[[TURN:quiz]]` message. Verify it with one `quiz-audit` using `context:"review"`. Send `questions_json` and set `rendered_content` to the exact full batch. Show no visuals until the answers are graded.

When the learner replies, grade the clone phase first with `naive-student` when a teach-the-clone item was answered. Then run one batched `grade-audit` with `items[]` carrying traces, `pow`, `qtype`, `confidence`, `tutor_turns`, and `naive_student_receipt`.

## Feedback and pause

Present verified feedback with `fact-check` (`turn_kind:"grade_feedback"` and `grade_verdicts`). Use the smallest visual that carries it. Pause for learner questions in the same turn. Persist nothing until the learner explicitly says "no questions". Silence is not consent. Answer questions through the inquiry loop with verified `answer` and `repair` turns. Re-grade any disputed item. Then pause again.

## Close

Dispatch one `review-clerk` with a `REVIEW_WRITES` envelope carrying the exact transcript, verdicts, battery outcomes, `dependency_events`, and mistakes. Then dispatch one `review-session-audit` on the exact writes. A `PASS` releases the verified closing summary. An `ISSUES` verdict withholds it until the writes are fixed and a fresh audit returns zero issues. There is no cycle cap. You write no state yourself.

Begin every assistant message with a turn tag. Dispatch each verifier once in the foreground with `dispatch({ agent, task: { ...envelope... } })`. Emit the verified draft unchanged.
