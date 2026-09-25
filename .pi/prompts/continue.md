---
description: Continue the current (paused) lesson
---
[[FLOW:resume]]
Continue the current lesson where we left off. Load the `learning-teach` skill. The lesson file + last session note are the source of truth — no Scout digest is needed. Open with a short recall warm-up on the last completed mini-checkpoint, then continue at the next mini-checkpoint (or the checkpoint's practice) — never restart the checkpoint from its first idea.

Honor the mini-checkpoint pause protocol: deliver a checkpoint as a sequence of mini-checkpoints — one atomic idea per message, pausing after each to invite questions/tangents before the next piece; only after the last mini-checkpoint give the checkpoint's single practice, then pause again after grading. Never dump a whole checkpoint at once. Deliver each mini-checkpoint's idea through elicit → attempt → consolidate — one grounded prediction question, then at most two guiding questions, then the clean statement — and always honor "just tell me". Keep turns answer-first and about one screen; never skip a step in a worked example. Surface any source contradiction loudly. Write no `Learning System/` files mid-lesson — batch them at the pause/lesson-end handoff, then dispatch one foreground `tutor-audit` on that batch before the summary.

Begin every assistant message with a turn tag on its first line — `[[TURN:claims]]` (teaching/plan), `[[TURN:quiz]]` (questions), `[[TURN:grade]]` (grading), or `[[TURN:none]]`. The gate strips the tag before the learner sees it. Dropped `grade`/`quiz`/`claims` tags are recovered from a bound verifier receipt, but still tag every turn.

Dispatch each verifier ONCE per turn as a foreground call (`async: false`) and wait for its verdict before emitting. Never re-dispatch a verifier for the same draft: if a message is withheld, re-emit the verified draft (or fix the tag) — do not re-verify. Re-verification is only for a materially corrected draft after an `ISSUES` verdict. Hints are `claims` turns too, and their `rendered_content` must carry the method only — never the final answer.
