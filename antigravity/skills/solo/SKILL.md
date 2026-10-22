---
name: solo
description: AI-free closed-book review check. The due queue is evaluated without teaching explanations, hints, or interactive widgets, using unlabeled operational items (no MCQs), and attempts are recorded in solo mode to feed the independence gate. Trigger with /solo.
---

# Solo Flow (`/solo`)

An AI-free closed-book assessment. Evaluates your true retention and independent mastery without any tutor hints, scaffolds, or interactive aids. Solo items are **operational, not declarative**: perturbations, misapplication spotters, unlabeled problems, and qualitative traces.

---

## Hard Invariants of Solo Mode

1. **Flow Marker**: Include `[[FLOW:solo]]` in your internal thought/context.
2. **Zero Teaching**: Never provide explanations, conceptual summaries, derivations, or context hints.
3. **Zero Scaffolds**: Do not provide Socratic guiding questions.
4. **Zero Widgets**: Never generate, embed, or mark up an HTML widget (`<agent-embed>`), and never emit a Mermaid diagram that diagrams the method — both are aids (`SOLO_NO_AIDS`).
5. **Zero MCQs**: Recognition is not retrieval — solo batches contain no multiple-choice items, ever.
6. **Pure Evaluation**: You present questions, collect the learner's closed-book answers (with qualitative traces), grade them via `verifier`, and hand off the writes.

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

## Step 1: Closed-Book Operational Batch

1. Compose the batch from the due queue with **unlabeled items** (stems never name the concept for selection/application items; naming is allowed only for a concept's meaning/anatomy):
   - Qualitative items requiring the 3-line trace (cue & principle → mechanism/knob-turn → direction & extreme check). No derivations or calculations.
   - At least one **perturbation** item (mutate a load-bearing assumption; predict the qualitative downstream behaviour).
   - At least one **misapplication** item (a plausible real-world use that violates a `condition`; name the broken assumption and the right tool).
   - At least one **decoy / near-miss** item (surface resembles a due concept, but violates its `conditions`; requires an older tool).
   - One `concept`/`design` item closed out via the **clone protocol**, in two phases: in this batch, add a "teach the clone" item asking the learner to explain the (unlabeled) concept. Do **not** dispatch `naive-student` yet — there is nothing to teach it until the learner answers. This is solo's Feynman replacement and is logged as `feynman_pass`/`feynman_fail`.
2. Verify the batch with **`verifier`** (`mode: "quiz_audit", context: "solo"`).
3. Present the batch with explicit instructions:
   *"Closed-book check. Work independently without hints or references. Include your 3-line qualitative trace for each item. Reply with your final answers."*

---

## Step 2: Independent Grading

1. When the learner answers, build grade items including each learner trace.
2. **Run the Clone Phase (if the batch contained a teach-the-clone item)**:
   - Dispatch **`naive-student`** now, with `concept`, a seeded plausible `misconception`, `prereq_level` (the concept's prerequisites), a **qualitative** `target_task` (a prediction or tool choice), and `learner_transcript` = the learner's teaching reply verbatim.
   - Await `NAIVE_STUDENT_RECEIPT` (it makes the qualitative call using only what the learner explicitly taught).
3. Dispatch **`verifier`** (`mode: "grade_audit"`, with `naive_student_receipt` on clone items) to verify all verdicts — it grades the mechanism and the direction/extreme check, not a scalar, flags shallow passes, and audits the clone receipt against the claimed verdict.
4. Report the verified verdicts (Pass/Fail) directly without providing teaching repairs.

---

## Step 3: State Persistence in Solo Mode

1. Dispatch **`clerk`** with the verdicts and pow outcomes, instructing it to log attempts with `--mode solo`:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "clerk",
           "Role": "State Clerk",
           "Prompt": "mode: 'review_close', track: '<track>', grade_verdicts: [...], pow_outcomes: [...], solo_mode: true"
       }]
   )
   ```
   This ensures passed attempts feed the concept's independence score in `ops.py mastery`.
2. Dispatch **`auditor`** (`mode: "review_session_audit"`).
3. Present the final score and updated mastery metrics.
