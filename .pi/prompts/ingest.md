---
description: Ingest content into the learning system
argument-hint: "<content or URL>"
---
[[FLOW:ingest]]
Ingest the following content into the learning system:

$ARGUMENTS

Load the `learning-system` skill and follow its Ingest flow via the `clerk` subagent. When Clerk returns its `CLERK_WRITES` receipt, dispatch ONE independent `review-gate` on the wiki pages it wrote (the Clerk does not gate itself). If `CLERK_WRITES.graph` lists any created or linked nodes/chains, also dispatch ONE independent `graph-audit` over those exact ids (`{"gate":"graph_audit","session":"...","written_nodes":[...],"written_chains":[...],"material":[...],"lesson_ref":"..."}`) before the summary: the close is withheld (`NO_GRAPH_AUDIT_PASS`) until it returns PASS over every written id, and an `ISSUES` verdict withholds (`GRAPH_AUDIT_ISSUES`) until the Clerk records a fix and a fresh audit passes. Fold all verdicts. Commit and push state only (`Learning System/`, `Knowledge Wiki/`).

After the `clerk` subagent completes, fold its result into ONE final summary whose first line is exactly `[[TURN:none]]` (the gate strips it before the learner sees it). Include the Tutor's `REVIEW_GATE_VERDICT` (from your own review-gate dispatch), the `GRAPH_AUDIT_VERDICT` (when graph records were written), and the Clerk's `STATE_AUDIT_VERDICT` markers verbatim — they are this turn's verification, so an untagged ingest summary now renders as an implicit `[[TURN:none]]` turn rather than dead-ending.
