---
name: review
description: Run a spaced-repetition review session on the active track. Gathers the deterministic due queue, composes unlabeled interleaved and synthesis questions, audits them, verifies grades (qualitative traces included), and delegates state updates to clerk and auditor. Trigger with /review.
---

# Review Flow (`/review`)

Conduct a spaced-repetition review session on your active learning track using the deterministic due queue. Reviews test **cue selection and transfer**, not recognition: questions are unlabeled, interleaved, and graded on qualitative traces.

---

## Step 0: Queue Generation via Scout

1. **Flow Marker**: Include `[[FLOW:review]]` in your internal thought/context.
2. Determine active track from `Learning System/MISSION.md` (e.g. `aiefs` or `aie`).
3. Dispatch the **`scout`** subagent to build the due queue:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "scout",
           "Role": "Review Scout",
           "Prompt": "mode: 'review', track: '<track>'"
       }]
   )
   ```
   Pause and await `scout`'s wakeup response with `REVIEW_SCOUT_RECEIPT`.
4. The digest's `queue` (up to 2 due mistakes + due concepts) is **authoritative** for scheduling: every due entry must be covered by the session's questions, and no non-due concept may be tested in isolation — but presentation (Step 1) composes entries into scenarios rather than one question per row.

---

## Step 1: Scenario Composition & Quiz Audit

1. **Prerequisite Check**: For each queued concept, run `python3 scripts/ops.py prereqs "<concept>"`. If `blocks: true`, re-establish the blocked prerequisite's intuition rather than treating the concept as independent.
2. **Compose Unlabeled Items (no MCQs)**:
   - **Never name the concept** when the item tests *tool selection or application* (the learner must select the tool, not be handed it). For an item that directly tests a concept's *meaning or anatomy*, naming it is allowed.
   - **Multi-concept collisions**: when the queue has 3+ entries, compose 1–2 composite scenarios that chain concepts from different weeks (plus one known mistake) instead of asking one isolated question per concept. Grade each component concept separately within the scenario so scheduling stays per-concept; record the scenario→concept mapping in the handoff, never shown to the learner.
   - **Decoy / near-miss items**: include at least one item whose surface vocabulary resembles a due concept but violates one of its `conditions`, so that blindly applying the due concept fails. It actually requires an older tool.
   - **Perturbation items**: for at least one due concept, mutate a load-bearing assumption and ask the learner to predict the qualitative downstream behaviour (which way it moves, what breaks).
   - **Misapplication items**: include an item presenting a plausible real-world use where a `condition` is violated; the learner names the broken assumption and what should have been done instead.
   - For `concept`/`design` types, the Feynman check is the **clone protocol**, run in two phases: in this batch, add a "teach the clone" item asking the learner to explain the (unlabeled) concept in their reply. Do **not** dispatch `naive-student` yet — there is nothing to teach it until the learner answers.
3. **Qualitative Trace Requirement**: Instruct the learner to reply with the 3-line qualitative trace — cue & principle (why it applies) → mechanism/knob-turn → direction & extreme check — not only a final answer. No derivation or calculation prompts: this review tests the mental model.
4. **Verify Batch**:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "verifier",
           "Role": "Quiz Auditor",
           "Prompt": "mode: 'quiz_audit', context: 'review', questions: [...], draft: '...'"
       }]
   )
   ```
   Pause and wait for `verifier`'s `PASS` receipt before presenting the questions.
5. Present the full batch in a single turn so the learner can reply in one message.

---

## Step 2: Evaluation & Grade Audit

1. When the learner replies, build the grade items with the learner's **trace** included per item.
2. **Run the Clone Phase (if the batch contained a teach-the-clone item)**:
   - Dispatch **`naive-student`** now, with `concept`, a seeded plausible `misconception`, `prereq_level` (the concept's prerequisites), a **qualitative** `target_task` (a prediction or tool choice), and `learner_transcript` = the learner's teaching reply verbatim.
   - Await `NAIVE_STUDENT_RECEIPT` (it attempts the target task using only what the learner explicitly taught).
3. **Verify Grades**:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "verifier",
           "Role": "Grade Verifier",
           "Prompt": "mode: 'grade_audit', items: [ {id: 1, concept: '...', pow: '...', question: '...', learner_answer: '...', trace: '...', claimed_verdict: 'pass|fail', source_excerpt: '...', tutor_turns: [...], naive_student_receipt: {...}}, ... ]"
       }]
   )
   ```
   Pause and await the verifier's `correct_verdict` (it grades the mechanism and the direction/extreme check, not a scalar, and never requires algebra; it flags shallow passes against your recent turns; and for clone items it audits the `NAIVE_STUDENT_RECEIPT` against the claimed verdict). If the verifier disagrees, use the verifier's verdict.
3. Present the graded feedback. If repair is needed, explain the slip and provide a micro-check.

---

## Step 3: State Persistence via Clerk & Auditor

The Reviewer session writes **no state files directly**.

1. **Dispatch Clerk**:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "clerk",
           "Role": "State Clerk",
           "Prompt": "mode: 'review_close', track: '<track>', grade_verdicts: [...], pow_outcomes: [...], transcript: '...'"
       }]
   )
   ```
   Wait for `clerk` to log attempts (with `pow` types noted), update `Active Concepts.md` and `Mistakes.md`, write `Reviews/` and `Sessions/` notes, run `audit_state.py`, and commit state.
2. **Dispatch Auditor**:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "auditor",
           "Role": "Session Auditor",
           "Prompt": "mode: 'review_session_audit', concepts: [...], grade_verdicts: [...], pow_outcomes: [...], written_files: [...]"
       }]
   )
   ```
   Wait for `auditor`'s `PASS` receipt.
3. Present the completion summary, showing updated mastery scores and next scheduled review dates.
