---
name: review
description: Run a spaced-repetition review session on the active track. Gathers the deterministic due queue, composes unlabeled interleaved and synthesis questions, audits them, verifies grades (qualitative traces included), pauses for learner questions on the feedback, then auto-persists the review state and auto-ingests into the Knowledge Wiki. Trigger with /review.
---

# Review Flow (`/review`)

Conduct a spaced-repetition review session on your active learning track using the deterministic due queue. Reviews test **cue selection and transfer**, not recognition: questions are unlabeled, interleaved, and graded on qualitative traces.

The session closes in three phases: **verified feedback → learner Q&A pause → automatic persistence and ingest**. Nothing is written and nothing is ingested until the learner has had the chance to question the feedback and explicitly says they have no questions.

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
4. Keep the audited verdicts, pow outcomes, and learner traces verbatim in conversation context — they are the source for the feedback in Step 3 and the persistence batch in Step 5. Do **not** present the verdicts yet.

---

## Step 3: Feedback & Mandatory Question Pause

1. **Compose the learner-facing feedback**: for each item, the verified verdict and *why* the trace passed or slipped (the exact step that failed), plus the pow outcome and — when a repair is needed — one concrete micro-check. Never expose verifier receipts, prompts, or audit mechanics.
2. **Verify the rendered feedback** before emitting it:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "verifier",
           "Role": "Feedback Verifier",
           "Prompt": "mode: 'fact_check', turn_kind: 'grade_feedback', draft: '<exact rendered feedback>', grade_verdicts: [...], claims: [...], raw_files: [...]"
       }]
   )
   ```
   Await `PASS`; apply any `ISSUES` corrections silently and re-verify until `PASS`.
3. **Present the feedback and pause in the same turn.** End with an explicit invitation, e.g.:
   > *"Anything here that isn't clear — a verdict, the step you slipped on, or the repair? Ask now. If it's all clear, say 'no questions' and I'll save the session and ingest the results."*
4. **Stop the turn.** Do not dispatch `clerk`, do not ingest, and do not present the completion summary while the question pause is open. Silence or a bare acknowledgement is **not** an explicit "no questions" — if the learner does not clearly signal it, ask once for confirmation.

---

## Step 4: Inquiry Loop (Until the Learner Has No Questions)

1. For every learner message that contains a question:
   - Answer it as a normal tutoring turn: repair the slip, explain the relevant mechanism, or correct a misread of the feedback.
   - Every explanatory turn goes through `verifier` (`mode: 'fact_check'`, `turn_kind: 'answer'` — or `'repair'` when correcting the slip — with the exact `draft`, `claims: [...]`, and `raw_files`/`source_urls: [...]`) before you emit it; if the inquiry challenges a verdict, re-run `verifier` (`mode: 'grade_audit'`) on that item and adopt the verifier's `correct_verdict`.
   - Honor hint discipline and the AGENTS.md **Clean Reveal + Immediate Knob Check**: if the learner asks to be told the answer outright, ask only where the wall is, deliver the full intuitive model + anatomical formula read immediately, record `just_tell_me` as a `dependency_events[]` entry for the Step 5 handoff, and ask one immediate qualitative prediction on an altered case.
   - After answering, **pause again** with the same invitation. Do not persist state while questions remain.
2. Advance to Step 5 only when the learner explicitly signals they have no questions ("no questions", "none", "all clear", "go ahead"). If the signal is ambiguous, ask once more; never assume.

---

## Step 5: Auto-Persist the Review State (Clerk & Auditor)

The Reviewer session writes **no state files directly**.

1. **Dispatch Clerk** (`mode: 'review_close'`):
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "clerk",
           "Role": "State Clerk",
           "Prompt": "mode: 'review_close', track: '<track>', grade_verdicts: [...], pow_outcomes: [...], dependency_events: [...], transcript: '<exact Q/A + learner answers + verified feedback + inquiry Q/A>'"
       }]
   )
   ```
   Wait for `clerk` to log attempts (with `pow` types noted), update `Active Concepts.md` and `Mistakes.md`, write the `Reviews/` and `Sessions/` notes, run `audit_state.py`, and commit state. Confirm the receipt's `mode: 'review_close'`.
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
   Wait for `PASS`. On `ISSUES`, re-dispatch `clerk` with the corrections and re-audit until zero blocking issues.

---

## Step 6: Auto-Ingest (Inline, No Manual `/ingest`)

Ingest runs automatically in this same turn sequence — the learner never has to type `/ingest` for a review.

1. **Dispatch Clerk** (`mode: 'ingest'`) using the review note as the source of truth:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "clerk",
           "Role": "State Clerk",
           "Prompt": "mode: 'ingest', source: 'Learning System/Reviews/Review — <track> — <YYYY-MM-DD>.md', track: '<track>', concepts: [...]"
       }]
   )
   ```
   Wait for the `CLERK_RECEIPT` with `mode: 'ingest'` (it writes or enriches `Knowledge Wiki/wiki/<page>.md`, preserves `## My understanding`, updates `Active Concepts.md` / `CURRICULUM.md`, runs `audit_state.py`, and commits).
2. **Dispatch the Ingest Review Gate**:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "auditor",
           "Role": "Wiki Auditor",
           "Prompt": "mode: 'review_gate', target_files: ['Knowledge Wiki/wiki/<page>.md', ...]"
       }]
   )
   ```
   Await the verdict. On in-scope `ISSUES` (unverified claims, missing provenance, broken links), re-dispatch `clerk` with the corrections and re-audit until a clean `PASS`. State/bookkeeping findings stay as context notes and do not block.

---

## Step 7: Completion Summary

1. Verify the rendered closing summary with `verifier` (`mode: 'fact_check', turn_kind: 'answer', draft: '<exact summary>', claims: [...], raw_files: [...]`) when it is substantive, then present it concisely:
   - Per-concept verdicts and mastery movement.
   - Ingested / enriched wiki pages and their links.
   - New concepts added to `Active Concepts.md` and their next review dates.
   - Confirmation of a clean state audit (`audit_state.py` report: 0 errors).
2. Note any open mistakes and what clears them. Do not claim completion if the auditor has not returned `PASS`.
