---
description: Ingest content into the learning system
argument-hint: "<content or URL>"
---
[[FLOW:ingest]]

Ingest the following content into the learning system:

$ARGUMENTS

Load the `learning-system` skill and follow its Ingest flow through the `clerk` subagent.

## Verify the writes

When Clerk returns its `CLERK_WRITES` receipt, dispatch one independent `review-gate` on the wiki pages it wrote. The Clerk does not gate itself.

If `CLERK_WRITES.graph` lists any created or linked nodes or chains, also dispatch one independent `graph-audit` over those exact ids before the summary. Send this envelope:

`{"gate":"graph_audit","session":"...","written_nodes":[...],"written_chains":[...],"material":[...],"lesson_ref":"..."}`

The close is withheld (`NO_GRAPH_AUDIT_PASS`) until the audit returns `PASS` over every written id. An `ISSUES` verdict withholds it (`GRAPH_AUDIT_ISSUES`) until the Clerk records a fix and a fresh audit passes. Fold all verdicts.

Commit and push state only. State means `Learning System/` and `Knowledge Wiki/`.

## Summary

After the `clerk` subagent completes, fold its result into one final summary whose first line is exactly `[[TURN:none]]`.

Include these markers verbatim: the Tutor's `REVIEW_GATE_VERDICT` from your own review-gate dispatch, the `GRAPH_AUDIT_VERDICT` when graph records were written, and the Clerk's `STATE_AUDIT_VERDICT`.
