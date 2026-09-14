---
description: Pause the current lesson and bank progress
---
[[FLOW:resume]]
Pause the current lesson where we are. Load the `learning-teach` skill and run the pause protocol: an exit ticket for today's checkpoints only, a partial lesson file with Status + Resume-from pointer, and a partial `Pending Ingest.json` (status, resume_from, concepts, mistakes). Write no `Learning System/` files until this handoff, then dispatch one foreground `tutor-audit` on the written batch. Finally run the Ingest flow via the `clerk` subagent to bank today's progress (this keeps the Scout digest and the lesson in-progress).

Begin every assistant message with a turn tag on its first line — `[[TURN:quiz]]` (exit ticket), `[[TURN:grade]]` (grading), or `[[TURN:none]]` (summaries). The gate strips the tag before the learner sees it.
