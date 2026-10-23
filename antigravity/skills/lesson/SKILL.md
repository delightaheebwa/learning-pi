---
name: lesson
description: Stress-test the learner's model of the next sequential curriculum lesson. Derives the lesson position from MISSION.md and CURRICULUM.md, points the learner at the raw material, then runs the interrogation pipeline. Trigger with /lesson.
---

# Lesson Flow (`/lesson`)

Start or resume the next sequential curriculum lesson as an **interrogation**, not a lecture. The learner reads the curriculum document and its Further Reading themselves; the Tutor tests the model they bring back.

---

## Step 0: Position Derivation

1. **Flow Marker**: Include `[[FLOW:teach]]` in your internal thought/context.
2. **Derive Active Position**:
   - Read `Learning System/MISSION.md` to identify the active track and focus.
   - Read `Learning System/CURRICULUM.md` to identify the next sequential lesson that is not marked `done`.
   - Cross-check against the latest files in `Learning System/Lessons/` and `Learning System/Sessions/`.
   - **Contradiction Guard**: If `MISSION.md`, `CURRICULUM.md`, and recent session files disagree on the current position, **stop immediately and report the discrepancy to the user**. Do not guess or auto-advance.

---

## Step 1: Point at the Material, or Resume

1. Check if a lesson file for this topic already exists with status `in-progress`:
   - If an in-progress file exists, route immediately to the **`continue`** flow at the recorded attack/triage state.
   - If starting fresh, do **not** run a probe or a scope contract. Dispatch `scout` (`mode: "lesson"`) for the curriculum document and every Further Reading link, then `auditor` (`mode: "scout_audit"`). The scout persists sources; it does not summarize them.
2. Send the **entry gate** brief from the `teach` skill: exactly what to read and what to attempt, plus the two deliverables (notes/material + a closed-book model in the learner's own words). Do not preview the mechanism or pre-teach the lesson. Verify the brief with `verifier` (`turn_kind: "plan"`) and stop.
3. When the learner returns, continue with the **`teach`** flow: closed-book spine check (v1) → triage → targeted attacks → model patch and graduation.
4. **Compose visuals automatically**: every attack turn uses the smallest format that carries the idea (`AGENTS.md` §6): a triage table, Mermaid for structure, or a Predict-Before-Render widget built by `ui-generator` from your spec when the learner must vary a knob and predict the outcome. Each `verifier` dispatch carries `visual_plan`; widget turns require a passing `ui_audit` bound to the returned file before the `<agent-embed>` is emitted.
