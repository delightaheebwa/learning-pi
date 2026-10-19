---
name: lesson
description: Teach the next sequential curriculum lesson. Derives the lesson position from MISSION.md and CURRICULUM.md and executes the teaching pipeline. Trigger with /lesson.
---

# Lesson Flow (`/lesson`)

Initiate or resume the next sequential curriculum lesson defined in your learning system roadmap.

---

## Step 0: Position Derivation

1. **Flow Marker**: Include `[[FLOW:teach]]` in your internal thought/context.
2. **Derive Active Position**:
   - Read `Learning System/MISSION.md` to identify the active track and focus.
   - Read `Learning System/CURRICULUM.md` to identify the next sequential lesson that is not marked `done`.
   - Cross-check against the latest files in `Learning System/Lessons/` and `Learning System/Sessions/`.
   - **Contradiction Guard**: If `MISSION.md`, `CURRICULUM.md`, and recent session files disagree on the current position, **stop immediately and report the discrepancy to the user**. Do not guess or auto-advance.

---

## Step 1: Resume or Teach

1. Check if a lesson file for this topic already exists with status `in-progress`:
   - If an in-progress file exists, route immediately to the **`continue`** flow at the recorded checkpoint.
   - If starting fresh, invoke the **`teach`** skill for the resolved topic:
     - Dispatch `scout` (`mode: "lesson"`) for curriculum and Further Reading sources.
     - Dispatch `auditor` (`mode: "scout_audit"`).
     - Run the probe → plan → mini-checkpoint teaching loop with every-turn `verifier` verification.
