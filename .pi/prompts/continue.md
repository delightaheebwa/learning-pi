---
description: Continue the current (paused) lesson
---
[[FLOW:resume]]
Continue the current lesson where we left off. Load the `learning-teach` skill. The lesson file + last session note are the source of truth — no Scout digest is needed. Open with a short recall warm-up on the last completed checkpoint, then continue at the next checkpoint.

Begin every assistant message with a turn tag on its first line — `[[TURN:claims]]` (teaching/plan), `[[TURN:quiz]]` (questions), `[[TURN:grade]]` (grading), or `[[TURN:none]]`. The gate strips the tag before the learner sees it.
