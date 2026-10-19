---
name: teach
description: Teach a topic or concept through the probe -> plan -> teach loop against live curriculum sources and Further Reading, with every-turn subagent verification. Trigger with /teach <topic>.
---

# Teach Flow (`/teach <topic>`)

Teach an active curriculum topic or requested concept using the Guided Learning pedagogy, backed by independent subagents for live source scouting, content verification, and handoff auditing.

---

## Step 0: Flow Initialization & Scout Dispatch

1. **Flow Marker**: Include `[[FLOW:teach]]` in your internal thought/context.
2. **Context Check**:
   - Check if an in-progress lesson file exists under `Learning System/Lessons/Lesson — <topic> — *.md`. If so, route to the **`/continue`** flow instead.
   - Check if an unexpired `.tmp/context-*-<slug>.json` digest exists (within its 7-day TTL).
   - If no valid digest exists, dispatch the **`scout`** subagent:
     ```python
     invoke_subagent(
         Subagents=[{
             "TypeName": "scout",
             "Role": "Source Scout",
             "Prompt": "mode: 'lesson', topic: '<topic>', slug: '<slug>'"
         }]
     )
     ```
   - End your turn and wait for `scout`'s wakeup response.
3. **Scout Audit**:
   - When `scout` returns with `SCOUT_RECEIPT`, dispatch **`auditor`** to verify source completeness:
     ```python
     invoke_subagent(
         Subagents=[{
             "TypeName": "auditor",
             "Role": "Scout Auditor",
             "Prompt": "mode: 'scout_audit', digest: '<path>', raw_files: [...]"
         }]
     )
     ```
   - If `auditor` flags issues, surface them with `⚠️ SCOUT AUDIT FLAGS SURFACED` and proceed with the lesson context.

---

## Step 1: Probe (Initial Knowledge Assessment)

1. Formulate a 3–4 question probe batch covering fundamental prerequisites and core concepts.
2. Ensure each question offers an explicit "I don't know" option and asks the learner to tag confidence (`sure`, `hunch`, or `no-idea`).
3. **Verify with Subagent**:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "verifier",
           "Role": "Quiz Verifier",
           "Prompt": "mode: 'quiz_audit', purpose: 'probe', questions: [...], draft: '...'"
       }]
   )
   ```
   Pause and wait for `verifier`'s `PASS` receipt before presenting the probe to the learner.
4. When the learner answers:
   - Verify grades via `verifier` (`mode: "grade_audit"`).
   - Retain attempt records in conversation context for Clerk to log at lesson conclusion.

---

## Step 2: Plan (Interactive Learning Graph)

1. Construct a Mermaid dependency flowchart showing the checkpoints for this lesson.
2. Explicitly outline what will be skipped, expanded, or reframed based on the probe responses.
3. Verify plan text with `verifier` (`mode: "fact_check", turn_kind: "plan"`).
4. Present the plan and invite the learner's approval or adjustments.

---

## Step 3: Interactive Teaching (Mini-Checkpoint Protocol)

Follow the procedures in [pedagogy.md](./references/pedagogy.md):

1. **Prerequisite Check**: Before each checkpoint, run `python3 scripts/ops.py prereqs "<concept>"`. If `blocks: true`, re-derive the prerequisite before proceeding.
2. **Mini-Checkpoints**:
   - For each atomic idea, execute the **Elicit → Attempt → State → Check-and-Extend** ladder.
   - On the idea turn, declare `turn_kind: "idea"` and include the 4 foundation beats (`problem`, `where_from`, `conditions`, `contrast`).
   - **Verify Every Turn**: Before emitting the idea, hint, or practice item, dispatch `verifier` (`mode: "fact_check"` or `mode: "quiz_audit"`) and pause. Emit only upon a `PASS` receipt.
   - **Pause after every mini-checkpoint** to invite questions.
3. **Practice**:
   - At the end of each checkpoint, deliver a single practice item.
   - Grade the learner's reply using `verifier` (`mode: "grade_audit"`).
   - Retain attempt metadata (qtype, confidence, hints) in conversation context.
   - Pause again after grading.

---

## Step 4: Lesson End & Handoff

1. **Cumulative Assessment**: Deliver a short 3–4 question quiz plus a mandatory Feynman explain-back for all `concept`/`design` types. Audit via `verifier` (`quiz_audit` and `grade_audit`).
2. **Delegate Handoff Batch to Clerk**:
   The Tutor focuses purely on teaching and writes no files to `Learning System/`. Dispatch **`clerk`**:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "clerk",
           "Role": "State Clerk",
           "Prompt": "mode: 'lesson_handoff', topic: '<topic>', slug: '<slug>', concepts: [...], mistakes: [...], learner_quotes: {...}, attempts: [...], session_summary: '...'"
       }]
   )
   ```
   Wait for `CLERK_RECEIPT`.
3. **Handoff Audit**: Dispatch **`auditor`** to verify Clerk's handoff files:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "auditor",
           "Role": "Tutor Auditor",
           "Prompt": "mode: 'tutor_audit', flow: 'lesson-end', files: [...]"
       }]
   )
   ```
   Wait for a passing receipt.
4. **Prompt Ingest**: Present the lesson completion summary and instruct the learner to run `/ingest` to reconcile wiki and state records.
