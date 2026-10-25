---
description: Run an AI-free (closed-book) solo check
---
[[FLOW:solo]]
Run an AI-free solo check. This is a CLOSED-BOOK operational test: no hints, no teaching, no worked steps, no repair prose, no MCQs, no widgets. The gate withholds any `[[TURN:claims]]` message in this flow (`SOLO_NO_TEACHING`) and any `[[TURN:ui]]` widget (`SOLO_NO_AIDS`), so teaching is impossible by construction.

First `dispatch` the `review-scout` agent to build the due queue (deterministic `ops.py queue`); its `queue` is authoritative — use it verbatim. Compose ONE unlabeled batch: 3-line qualitative traces (cue & principle → mechanism/knob-turn → direction & extreme check), at least one perturbation, one misapplication, one decoy/near-miss, and a teach-the-clone item for a `concept`/`design` entry. No calculation or derivation prompts. Attach graph `targets[]` (ids copied from the digest's `prior_knowledge`; omit when none) to each question, its grade item, and `REVIEW_WRITES.grade_verdicts[].targets`.

Verify the batch with ONE `quiz-audit` (`context:"solo"`, `questions_json` + `rendered_content` = the exact full batch), then present it in ONE `[[TURN:quiz]]` message with: "Closed-book check. Work independently without hints or references. Include your 3-line qualitative trace for each item. Reply with your final answers."

When the learner replies, dispatch `naive-student` for the clone item, then ONE batched `grade-audit` (`items[]` with traces and `naive_student_receipt`), and report the verifier's per-item verdicts directly — no repairs or explanations. Hand the durable writes to ONE `review-clerk` with `"mode":"solo"` so every attempt is recorded AI-free, then ONE `review-session-audit` on the exact writes and fold both verdicts. You write no state yourself.

Begin every assistant message with a turn tag — `[[TURN:quiz]]`, `[[TURN:grade]]`, or `[[TURN:none]]`. Never `[[TURN:claims]]` or `[[TURN:ui]]` in this flow.
