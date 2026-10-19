---
name: review
description: Run a spaced-repetition review session on the active track. Gathers the deterministic due queue, audits questions, verifies grades, and delegates state updates to clerk and auditor. Trigger with /review.
---

# Review Flow (`/review`)

Conduct a spaced-repetition review session on your active learning track using the deterministic due queue.

---

## Step 0: Queue Generation via Scout

1. **Flow Marker**: Include `[[FLOW:review]]` in your internal thought/context.
2. Determine active track from `Learning System/MISSION.md` (e.g. `aiefs` or `aie`).
3. Dispatch the **`scout`** subagent to build the due queue:
   ```python
   invoke_subagent(
       TypeName="scout",
       Role="Review Scout",
       Prompt="mode: 'review', track: '<track>'"
   )
   ```
   Pause and await `scout`'s wakeup response with `REVIEW_SCOUT_RECEIPT`.
4. The digest's `queue` (up to 2 due mistakes + due concepts) is **authoritative**: use it verbatim without re-sorting, re-filtering, or expanding beyond due items.

---

## Step 1: Question Batching & Quiz Audit

1. **Prerequisite Check**: For each queued concept, run `python3 scripts/ops.py prereqs "<concept>"`. If `blocks: true`, re-derive the blocked prerequisite rather than treating the concept as independent.
2. **Formulate Questions**:
   - Write 1 targeted question per entry, numbered, matching the entry's `question_type` and grounded in `source_excerpt`.
   - **Math on Paper**: For derivations or calculations, instruct the learner to work on paper and reply with only the final number or option letter.
   - For `concept` or `design` types, include a Feynman explain-back item.
3. **Verify Batch**:
   ```python
   invoke_subagent(
       TypeName="verifier",
       Role="Quiz Auditor",
       Prompt="mode: 'quiz_audit', purpose: 'review', questions: [...], draft: '...'"
   )
   ```
   Pause and wait for `verifier`'s `PASS` receipt before presenting the questions.
4. Present the full batch in a single turn so the learner can reply in one message.

---

## Step 2: Evaluation & Grade Audit

1. When the learner replies:
   - For MCQs with known keys, grade mechanically first:
     `python3 scripts/ops.py grade-mcq --key A,B,C --answers <learner-answers>`
   - For free-recall and Feynman explain-backs, grade against the 4-point Feynman rubric.
2. **Verify Grades**:
   ```python
   invoke_subagent(
       TypeName="verifier",
       Role="Grade Verifier",
       Prompt="mode: 'grade_audit', items: [ {id: 1, concept: '...', question: '...', learner_answer: '...', claimed_verdict: 'pass|fail', source_excerpt: '...'}, ... ]"
   )
   ```
   Pause and await the verifier's `correct_verdict`. If the verifier disagrees, use the verifier's verdict.
3. Present the graded feedback. If repair is needed, explain the slip and provide a micro-check.

---

## Step 3: State Persistence via Clerk & Auditor

The Reviewer session writes **no state files directly**.

1. **Dispatch Clerk**:
   ```python
   invoke_subagent(
       TypeName="clerk",
       Role="State Clerk",
       Prompt="mode: 'review_close', track: '<track>', grade_verdicts: [...], transcript: '...'"
   )
   ```
   Wait for `clerk` to log attempts, update `Active Concepts.md` and `Mistakes.md`, write `Reviews/` and `Sessions/` notes, run `audit_state.py`, and commit state.
2. **Dispatch Auditor**:
   ```python
   invoke_subagent(
       TypeName="auditor",
       Role="Session Auditor",
       Prompt="mode: 'review_session_audit', concepts: [...], grade_verdicts: [...], written_files: [...]"
   )
   ```
   Wait for `auditor`'s `PASS` receipt.
3. Present the completion summary, showing updated mastery scores and next scheduled review dates.
