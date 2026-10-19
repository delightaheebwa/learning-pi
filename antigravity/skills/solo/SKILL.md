---
name: solo
description: AI-free closed-book review check. The due queue is evaluated without teaching explanations, hints, or interactive widgets, and attempts are recorded in solo mode to feed the independence gate. Trigger with /solo.
---

# Solo Flow (`/solo`)

An AI-free closed-book assessment. Evaluates your true retention and independent mastery without any tutor hints, scaffolds, or interactive aids.

---

## Hard Invariants of Solo Mode

1. **Flow Marker**: Include `[[FLOW:solo]]` in your internal thought/context.
2. **Zero Teaching**: Never provide explanations, conceptual summaries, derivations, or context hints.
3. **Zero Scaffolds**: Do not provide Socratic guiding questions.
4. **Zero Widgets**: Never generate or embed HTML widgets (`SOLO_NO_AIDS`).
5. **Pure Evaluation**: You present questions, collect the learner's closed-book answers, grade them via `verifier`, and hand off the writes.

---

## Step 0: Queue Generation via Scout

1. Determine the active track from `Learning System/MISSION.md`.
2. Dispatch **`scout`** to compute the due queue:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "scout",
           "Role": "Review Scout",
           "Prompt": "mode: 'review', track: '<track>'"
       }]
   )
   ```
   Wait for `REVIEW_SCOUT_RECEIPT`.

---

## Step 1: Closed-Book Question Batch

1. Format the due queue items into a single numbered batch.
2. Verify the batch with **`verifier`** (`mode: "quiz_audit"`).
3. Present the batch with explicit instructions:
   *"Closed-book check. Work independently without hints or references. Reply with your final answers."*

---

## Step 2: Independent Grading

1. When the learner answers:
   - Run mechanical MCQ grading if applicable (`python3 scripts/ops.py grade-mcq ...`).
   - Dispatch **`verifier`** (`mode: "grade_audit"`) to verify all verdicts.
2. Report the verified verdicts (Pass/Fail) directly without providing teaching repairs.

---

## Step 3: State Persistence in Solo Mode

1. Dispatch **`clerk`** with the verdicts, instructing it to log attempts with `--mode solo`:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "clerk",
           "Role": "State Clerk",
           "Prompt": "mode: 'review_close', track: '<track>', grade_verdicts: [...], solo_mode: true"
       }]
   )
   ```
   This ensures passed attempts feed the concept's independence score in `ops.py mastery`.
2. Dispatch **`auditor`** (`mode: "review_session_audit"`).
3. Present the final score and updated mastery metrics.
