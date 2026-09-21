---
description: Continue the current (paused) lesson
---
[[FLOW:resume]]
Continue the current lesson where we left off. Load the `learning-teach` skill. The lesson file + last session note are the source of truth — no Scout digest is needed. Open with a short recall warm-up on the last completed checkpoint, then continue at the next checkpoint.

Honor the checkpoint pause protocol: teach one checkpoint's idea, pause and invite questions, then give its practice; after grading, pause again before the next checkpoint. Surface any source contradiction loudly. Write no `Learning System/` files mid-lesson — batch them at the pause/lesson-end handoff, then dispatch one foreground `tutor-audit` on that batch before the summary.

Begin every assistant message with a turn tag on its first line — `[[TURN:claims]]` (teaching/plan), `[[TURN:quiz]]` (questions), `[[TURN:grade]]` (grading), or `[[TURN:none]]`. The gate strips the tag before the learner sees it. Dropped `grade`/`quiz`/`claims` tags are recovered from a bound verifier receipt, but still tag every turn.

Dispatch each verifier ONCE per turn as a foreground call (`async: false`) and wait for its verdict before emitting. Never re-dispatch a verifier for the same draft: if a message is withheld, re-emit the verified draft (or fix the tag) — do not re-verify. Re-verification is only for a materially corrected draft after an `ISSUES` verdict. Hints are `claims` turns too, and their `rendered_content` must carry the method only — never the final answer.
