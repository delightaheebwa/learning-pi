---
name: pause
description: Cleanly pause an in-progress lesson, deliver an exit ticket, write partial handoff files, audit via auditor, and bank progress. Trigger with /pause.
---

# Pause Flow (`/pause`)

Stop a lesson cleanly at any mini-checkpoint, banking progress to disk without losing position.

---

## Step 0: Exit Ticket

1. **Flow Marker**: Include `[[FLOW:resume]]` in your internal thought/context.
2. Ask 1 quick exit ticket question summarizing today's key takeaways or self-reflection.
3. Verify question and answer with `verifier` (`mode: "quiz_audit"` and `mode: "grade_audit"`).

---

## Step 1: Write Handoff Batch

Write the 4 partial handoff artifacts in a single pass:
1. `Learning System/Lessons/Lesson — <slug> — <date>.md`:
   - Keep status as `in-progress`.
   - Record exact resume position: `Checkpoint N/M, mini K/L`.
2. `Learning System/Sessions/Session — <topic> — <date>.md`:
   - Summarize what was covered today, learner phrasings, and open questions.
3. `Learning System/Learning Records/Record — <topic> — <date>.md`:
   - Update concept mastery notes and attempt history.
4. `Learning System/Core/Pending Ingest.json`:
   - Set `"partial": true`.
   - Set `"status": "in-progress"`.
   - Set `"resume_from": "Checkpoint N/M, mini K/L"`.
   - List touched concepts and recorded mistakes.

---

## Step 2: Handoff Audit & Wrap-Up

1. Dispatch the **`auditor`** subagent to inspect the handoff writes:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "auditor",
           "Role": "Tutor Auditor",
           "Prompt": "mode: 'tutor_audit', flow: 'pause', files: ['Learning System/Lessons/...', 'Learning System/Sessions/...', 'Learning System/Learning Records/...', 'Learning System/Core/Pending Ingest.json']"
       }]
   )
   ```
2. Wait for a passing `AUDITOR_RECEIPT`.
3. Inform the learner:
   - Progress is securely banked.
   - Run `/ingest` to sync the wiki and state tables for today's covered concepts.
   - Run `/continue` anytime to pick up right at `Checkpoint N/M, mini K/L`.
