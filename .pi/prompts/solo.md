---
description: Run an AI-free (closed-book) solo check
---
[[FLOW:solo]]

Run an AI-free solo check. This is a closed-book operational test. Give no hints, no teaching, no worked steps, no repair prose, no MCQs, and no widgets. The gate withholds any `[[TURN:claims]]` message in this flow (`SOLO_NO_TEACHING`) and any `[[TURN:ui]]` widget (`SOLO_NO_AIDS`). ## Build the batch

Dispatch `review-scout` first to build the due queue with the deterministic `ops.py queue`. The digest's `queue` is authoritative. Use it verbatim and check prerequisites.

Compose one unlabeled batch with 3-line qualitative traces: cue and principle, mechanism or knob turn, then direction and extreme check. Terse and keyword lines are the default. Form is never graded; content is. All three lines are still required.

For a `concept` or `design` entry, add a teach-the-clone item. Its transcript must carry what the concept is, when and why it applies, the mechanism in one full causal clause, a failure regime, and the nearest-neighbour contrast. Add at least one perturbation, one misapplication, and one decoy or near miss. Do not use calculation or derivation prompts.

When the digest's `prior_knowledge` names graph propositions or chains for an item, copy their ids into that question's `targets[]`. Omit the field when there are none. Carry the ids onto the grade item and into `REVIEW_WRITES.grade_verdicts[].targets`.

## Present and grade

Verify the batch with one `quiz-audit` (`context:"solo"`). Send `questions_json` and set `rendered_content` to the exact full batch. Present it in one `[[TURN:quiz]]` message with this text:

"Closed-book check. Work independently without hints or references. Include your 3-line qualitative trace for each item. Phrases and keywords are fine; form is never graded. Reply with your answers and traces."

When the learner replies, dispatch `naive-student` for the clone item. Then run one batched `grade-audit` with `items[]` carrying traces and `naive_student_receipt`. Report the verifier's per-item verdicts directly. Give no repairs and no explanations.

## Close

Hand the durable writes to one `review-clerk` with `"mode":"solo"` so every attempt is recorded AI-free. Then dispatch one `review-session-audit` on the exact writes. Fold both verdicts. You write no state yourself.

Begin every assistant message with a turn tag: `[[TURN:quiz]]`, `[[TURN:grade]]`, or `[[TURN:none]]`. Never use `[[TURN:claims]]` or `[[TURN:ui]]` in this flow.
