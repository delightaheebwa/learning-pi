---
description: Continue the current (paused) lesson
---
[[FLOW:resume]]
Continue the current lesson where we left off. Load the `learning-teach` skill. The lesson file + last session note are the source of truth — no Scout digest is needed. Open with a short recall warm-up on the last completed checkpoint, then continue at the next checkpoint.

Honor the checkpoint pause protocol: teach one checkpoint's idea, pause and invite questions, then give its practice; after grading, pause again before the next checkpoint. Surface any source contradiction loudly. Write no `Learning System/` files mid-lesson — batch them at the pause/lesson-end handoff, then dispatch one foreground `tutor-audit` on that batch before the summary.

Begin every assistant message with a turn tag on its first line — `[[TURN:claims]]` (teaching/plan), `[[TURN:quiz]]` (questions), `[[TURN:grade]]` (grading), or `[[TURN:none]]`. The gate strips the tag before the learner sees it. A dropped grade/quiz tag is tolerated while its verifier receipt is pending; `claims`/`none` must be tagged.
