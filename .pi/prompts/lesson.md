---
description: Run the next curriculum lesson as an interrogation
---
[[FLOW:teach]]

Run the next curriculum lesson as an interrogation, not a lecture. Derive the next lesson from `Learning System/CURRICULUM.md`, `Learning System/MISSION.md`, and `Learning System/Lessons/`. If they disagree, stop and report.

## Before the briefing

If an in-progress lesson exists, route to `/continue`.

Otherwise dispatch `scout` for the curriculum document and every Further Reading URL. Then dispatch one independent `scout-audit` on its digest. A missing audit withholds the first claims turn. `ISSUES` surfaces as a banner. Fix those by re-scouting and re-auditing, with no cycle cap. The scout persists sources and never summarizes them for the learner.

## Briefing and interrogation

Send the entry-gate reading brief from the `learning-teach` skill. State what to read, what to attempt, and the two deliverables: notes or material, plus a closed-book model in the learner's own words. Verify the brief with `fact-check` (`turn_kind:"plan"`). Then stop.

When the learner returns, run the full interrogation:

1. Closed-book spine check (v1).
2. Triage.
3. One targeted attack per turn.
4. Repair mode for a gap whose self-repair failed. Teach one checked step at a time and close only after a graded fresh-surface pass and the learner's restatement.
5. Model patch (v2).
6. Clone and battery.
7. Handoff plus `tutor-audit`.
8. Auto-ingest inline.

Begin every assistant message with a turn tag. Verify every substantive turn with the matching verifier and emit the verified draft unchanged. Never teach a topic cold, never rewrite the learner's words, and never fill a hole the learner is meant to repair.
