---
description: Run the next curriculum lesson as an interrogation
---
[[FLOW:teach]]
Run the next curriculum lesson as an interrogation, not a lecture. Derive the next lesson from `Learning System/CURRICULUM.md`, `Learning System/MISSION.md`, and `Learning System/Lessons/`; if they disagree, stop and report.

If an in-progress lesson exists, route to `/continue`. Otherwise dispatch `scout` for the curriculum document and every Further Reading URL, then ONE independent `scout-audit` on its digest (missing audit withholds the first claims turn; ISSUES surfaces as a banner — fix via re-scout + re-audit, no cycle cap). The scout persists sources and never summarizes them for the learner.

Then send the entry-gate reading brief from the `learning-teach` skill (what to read, what to attempt, and the two deliverables: notes/material + a closed-book model in their own words). Verify it with `fact-check` (`turn_kind:"plan"`) and stop. When the learner returns, run the full interrogation: closed-book spine check (v1) → triage → one targeted attack per turn → repair mode for a gap whose self-repair failed (one checked step at a time, closed only by a graded fresh-surface pass and the learner's restatement) → model patch (v2) → clone and battery → handoff + `tutor-audit` → auto-ingest inline.

Begin every assistant message with a turn tag; verify every substantive turn with the matching verifier and emit the verified draft unchanged. Never teach a topic cold, never rewrite the learner's words, and never fill a hole the learner is meant to repair.
