---
name: pause
description: Cleanly pause an in-progress lesson, deliver an exit ticket, write partial handoff files, audit via auditor, and bank progress. Trigger with /pause.
---

# Pause Flow (`/pause`)

Stop a lesson cleanly at any mini-checkpoint, banking progress to disk without losing position.

---

## Step 0: Exit Ticket

1. **Flow Marker**: Include `[[FLOW:resume]]` in your internal thought/context.
2. Ask 1 quick exit ticket question summarizing today's key takeaways or self-reflection. (Unlabeled — do not name the concepts in the stem; ask the learner to name what they learned.)
3. Verify question and answer with `verifier` (`mode: "quiz_audit", context: "practice"` and `mode: "grade_audit"`).

---

## Step 1: Delegate Handoff to Clerk

The Tutor focuses purely on teaching and writes no files to `Learning System/`. Dispatch **`clerk`**:
```python
invoke_subagent(
    Subagents=[{
        "TypeName": "clerk",
        "Role": "State Clerk",
        "Prompt": "mode: 'pause_handoff', topic: '<topic>', slug: '<slug>', resume_from: 'Checkpoint N/M, mini K/L', partial: true, concepts: [...], mistakes: [...], attempts: [...]"
    }]
)
```
Wait for `CLERK_RECEIPT`.

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
