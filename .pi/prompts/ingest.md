---
description: Ingest content into the learning system
argument-hint: "<content or URL>"
---
[[FLOW:ingest]]
Ingest the following content into the learning system:

$ARGUMENTS

Load the `learning-system` skill and follow its Ingest flow via the `clerk` subagent. Run the `review-gate` before finalizing. Commit and push state only (`Learning System/`, `Knowledge Wiki/`).

Begin every assistant message with a turn tag on its first line — use `[[TURN:none]]` for ingest summaries. The gate strips the tag before the learner sees it.
