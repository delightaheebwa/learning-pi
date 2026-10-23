---
name: pause
description: Cleanly pause an in-progress interrogation, deliver a model-recall exit ticket, write partial handoff files, audit via auditor, and bank progress. Trigger with /pause.
---

# Pause Flow (`/pause`)

Stop an interrogation cleanly at any point, banking the learner's model and the open attack list to disk without losing position.

---

## Step 0: Model-Recall Exit Ticket

1. **Flow Marker**: Include `[[FLOW:resume]]` in your internal thought/context.
2. Ask **one** exit-ticket question that produces a model, not a summary: *"Without looking at your notes, state the part of your model you are least sure about and one case you think might break it."* (Do not name the concept in the stem; ask the learner to name what they learned.)
3. Verify the question with `verifier` (`mode: "quiz_audit", context: "practice"`) and the learner's answer with `verifier` (`mode: "grade_audit"`), grading the mechanism and the proposed breaking case. A fail is recorded, not softened.

---

## Step 1: Delegate Handoff to Clerk

The Tutor writes no files. Dispatch **`clerk`**:
```python
invoke_subagent(
    Subagents=[{
        "TypeName": "clerk",
        "Role": "State Clerk",
        "Prompt": "mode: 'pause_handoff', topic: '<topic>', slug: '<slug>', resume_from: 'Checkpoint N/M, mini K/L', partial: true, material: [...], learner_model: {v1: '...', v2: '... (if patched)'}, triage: [...], open_attacks: [...], attempts: [...], mistakes: [...]"
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
   - The model and the open attack list are securely banked.
   - Run `/ingest` to sync the wiki and state tables for the concepts touched.
   - Run `/continue` anytime to pick up at the first unresolved attack — no re-reading needed, though the exact source pointer is in the lesson file.
