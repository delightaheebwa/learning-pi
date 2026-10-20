---
name: teach
description: Teach a topic or concept through the probe -> scope contract -> adversarial ladder loop against live curriculum sources and Further Reading, with every-turn subagent verification. Trigger with /teach <topic>.
---

# Teach Flow (`/teach <topic>`)

Teach an active curriculum topic or requested concept using the adversarial-constructivist pedagogy (see [pedagogy.md](./references/pedagogy.md)), backed by independent subagents for live source scouting, content verification, and handoff auditing. The learner builds every idea; you build the pressure.

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
   - When `scout` returns with `SCOUT_RECEIPT`, dispatch **`auditor`** to verify source completeness (including `anomalies[]` candidates for Broken Worlds):
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

1. Formulate a 3–4 question probe batch covering fundamental prerequisites and core concepts. MCQs are legal **only here** (diagnostic context).
2. Ensure each question offers an explicit "I don't know" option and asks the learner to tag confidence (`sure`, `hunch`, or `no-idea`).
3. **Verify with Subagent**:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "verifier",
           "Role": "Quiz Verifier",
           "Prompt": "mode: 'quiz_audit', context: 'probe', questions: [...], draft: '...'"
       }]
   )
   ```
   Pause and wait for `verifier`'s `PASS` receipt before presenting the probe to the learner.
4. When the learner answers:
   - Verify grades via `verifier` (`mode: "grade_audit"`).
   - Retain attempt records in conversation context for Clerk to log at lesson conclusion.

---

## Step 2: Scope Contract (No Roadmap)

1. Summarize from the probe: what is solid, what is fuzzy, what is absent.
2. State the **scope contract**: what this lesson will cover, what will be skipped, expanded, or reframed — as prose about *scope*, not a mechanism preview.
3. **Do not** draw a dependency roadmap or pre-teach how upcoming concepts connect: a pre-lesson Mermaid graph biases every checkpoint answer. (A consolidated dependency diagram is allowed at Step 4 synthesis, after the work is done.)
4. **Never name the mechanisms of upcoming concepts** in the contract — naming a tool before its Collision pre-solves every mini-checkpoint.
5. Verify contract text with `verifier` (`mode: "fact_check", turn_kind: "plan"`). Present and invite the learner's approval or adjustments.

---

## Step 3: Interactive Teaching (Collision → Invention → Boundary Hunt → Falsify)

Follow the procedures in [pedagogy.md](./references/pedagogy.md):

1. **Prerequisite Check**: Before each checkpoint, run `python3 scripts/ops.py prereqs "<concept>"`. If `blocks: true`, re-derive the prerequisite before proceeding.
2. **Mini-Checkpoints** — for each atomic idea, execute the ladder:
   - **Collision** (`turn_kind: "collision"`): open with a grounded anomaly from the digest where the learner's existing toolkit fails. Never name the concept or preview the fix.
   - **Invention** (`turn_kind: "invention"`): the learner diagnoses the violated constraint and proposes a fix. Only then name the formal concept and supply the mechanism, leaving a bridging step for the learner.
   - **Boundary Hunt** (`turn_kind: "boundary_hunt"`): the learner produces the failure regime (`conditions`) and the nearest-neighbour misuse (`contrast`).
   - **Falsify-Until-Tight** (`turn_kind: "falsify"`): capture the learner's statement verbatim (v1); if it overgeneralizes, break it with a counterexample that satisfies it as written; the learner patches it; capture v2+.
   - **Verify Every Turn**: Before emitting any collision, evaluation, boundary question, falsification, hint, or practice item, dispatch `verifier` (`mode: "fact_check"` or `mode: "quiz_audit"`) with the learner-attempt flags and pause. Emit only upon a `PASS` receipt.
   - **Pause after every mini-checkpoint** to invite questions.
3. **Practice**:
   - At the end of each checkpoint, deliver a single **unlabeled** practice item (the stem never names the concept) requiring a **3-line reasoning trace** (governing principle → setup/crux → result + sanity check).
   - Grade the learner's reply using `verifier` (`mode: "grade_audit"`) — the trace is graded, not just the final answer.
   - Retain attempt metadata (qtype, confidence, hints) in conversation context.
   - Pause again after grading.

---

## Step 4: Lesson End — Proof-of-Work Battery & Handoff

1. **Proof-of-Work Battery** (not a quiz-plus-summary):
   - **Perturbation**: mutate a load-bearing assumption in a formula/algorithm just learned; the learner traces the downstream consequences. Verify and grade via `verifier` (`grade_audit`, `pow: "perturbation"`).
   - **Sabotage**: present a plausible derivation/code/design proof with one subtle conceptual bug; the learner finds the exact step, proves it illegal with a counterexample, and fixes it (`grade_audit`, `pow: "sabotage"`).
   - **Clone** (two phases): first ask the learner to write out their explanation of the concept in their own words ("teach it to a novice"). Do **not** dispatch anything yet. When the learner replies, dispatch the **`naive-student`** subagent with `concept`, a seeded plausible `misconception`, `prereq_level` (the concept's prerequisites), `target_task`, and `learner_transcript` = the learner's teaching reply verbatim. `naive-student` attempts the target task using only what the learner explicitly said. Success logs as `feynman_pass`; failure as `feynman_fail`.
   - **Consolidation**: after the battery, a dependency Mermaid diagram synthesizing what was built is now allowed.
2. **Delegate Handoff Batch to Clerk**:
   The Tutor focuses purely on teaching and writes no files to `Learning System/`. Dispatch **`clerk`**:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "clerk",
           "Role": "State Clerk",
           "Prompt": "mode: 'lesson_handoff', topic: '<topic>', slug: '<slug>', concepts: [...], mistakes: [...], learner_quotes: {v1: {...}, v2: {...}}, falsifications: [...], attempts: [...], pow_outcomes: [...], dependency_events: [...], session_summary: '...'"
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
