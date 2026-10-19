---
name: continue
description: Resume an in-progress or paused lesson at its recorded mini-checkpoint. Trigger with /continue.
---

# Continue Flow (`/continue`)

Resume a paused or in-progress lesson directly at its next atomic mini-checkpoint without re-starting the lesson from scratch.

---

## Step 0: Context & Resume Pointer Recovery

1. **Flow Marker**: Include `[[FLOW:resume]]` in your internal thought/context.
2. **Locate Active Lesson**:
   - Find the newest lesson file in `Learning System/Lessons/` that is not marked `done`.
   - Read the lesson file and the latest note in `Learning System/Sessions/`.
   - Extract the resume pointer: `Checkpoint N/M, mini K/L`.
   - If no in-progress lesson exists, inform the user and suggest running `/lesson` to start the next topic.
3. **Digest TTL Check**:
   - Check the creation timestamp of `Learning System/.tmp/context-*-<slug>.json`.
   - If the digest is older than 7 days, source passages must be re-grounded: dispatch `scout` (`mode: "lesson"`) before resuming new material.
   - If within 7 days, resume directly from the existing lesson context and raw files.

---

## Step 1: Resume Teaching

1. State clearly to the learner which topic and mini-checkpoint is resuming.
2. Follow the **mini-checkpoint pause protocol** and constructivist ladder from [pedagogy.md](../teach/references/pedagogy.md).
3. **Verify Every Turn**: Before presenting each new idea, Socratic hint, practice item, or grade, dispatch **`verifier`** and await `PASS`.
4. At lesson end, execute the cumulative assessment, write the final handoff files, dispatch `auditor` (`mode: "tutor_audit"`), and prompt `/ingest`.
