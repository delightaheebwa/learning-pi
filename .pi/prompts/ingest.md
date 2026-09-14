---
description: Ingest content into the learning system
argument-hint: "<content or URL>"
---
[[FLOW:ingest]]
Ingest the following content into the learning system:

$ARGUMENTS

Load the `learning-system` skill and follow its Ingest flow via the `clerk` subagent. Run the `review-gate` before finalizing. Commit and push state only (`Learning System/`, `Knowledge Wiki/`).

After the `clerk` subagent completes, fold its result into ONE final summary whose first line is exactly `[[TURN:none]]` (the gate strips it before the learner sees it). Include the clerk's `REVIEW_GATE_VERDICT` and `STATE_AUDIT_VERDICT` markers verbatim — they are this turn's verification, so an untagged ingest summary now renders as an implicit `[[TURN:none]]` turn rather than dead-ending.
