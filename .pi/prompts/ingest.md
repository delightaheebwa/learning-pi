---
description: Ingest content into the learning system
argument-hint: "<content or URL>"
---
[[FLOW:ingest]]
Ingest the following content into the learning system:

$ARGUMENTS

Load the `learning-system` skill and follow its Ingest flow via the `clerk` subagent. When Clerk returns its `CLERK_WRITES` receipt, dispatch ONE independent `review-gate` on the wiki pages it wrote (the Clerk does not gate itself), then fold both verdicts. Commit and push state only (`Learning System/`, `Knowledge Wiki/`).

After the `clerk` subagent completes, fold its result into ONE final summary whose first line is exactly `[[TURN:none]]` (the gate strips it before the learner sees it). Include the Tutor's `REVIEW_GATE_VERDICT` (from your own review-gate dispatch) and the Clerk's `STATE_AUDIT_VERDICT` markers verbatim — they are this turn's verification, so an untagged ingest summary now renders as an implicit `[[TURN:none]]` turn rather than dead-ending.
