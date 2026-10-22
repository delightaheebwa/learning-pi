---
name: teach
description: Teach a topic or concept through the probe -> scope contract -> intuition ladder loop against live curriculum sources and Further Reading, with every-turn subagent verification. Trigger with /teach <topic>.
---

# Teach Flow (`/teach <topic>`)

Teach an active curriculum topic or requested concept using the intuition-first pedagogy (see [pedagogy.md](./references/pedagogy.md)), backed by independent subagents for live source scouting, content verification, and handoff auditing. The learner sketches every move and owns every boundary; you supply the formalism openly and build the pressure where it counts.

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

## Step 3: Interactive Teaching (Collision → Sketch the Move → Read the Formula & Hunt the Boundary → Counterexample Test)

Follow the procedures in [pedagogy.md](./references/pedagogy.md):

1. **Prerequisite Check**: Before each checkpoint, run `python3 scripts/ops.py prereqs "<concept>"`. If `blocks: true`, re-establish the prerequisite's intuition before proceeding.
2. **Mini-Checkpoints** — for each atomic idea, execute the ladder:
   - **Collision** (`turn_kind: "collision"`): open with a grounded anomaly from the digest where the learner's existing toolkit fails. Never name the concept or preview the fix.
   - **Sketch the Move** (`turn_kind: "invention"`): the learner proposes the *intuitive* fix in plain words or a sketch. Only then name the formal concept, put the formula openly on screen, and guide an **Anatomical Read** (what each term does as a knob, extremes $\to 0$ / $\to \infty$). The learner restates the mechanism in their own words — never a derivation.
   - **Boundary Hunt** (`turn_kind: "boundary_hunt"`): the learner produces the failure regime (`conditions`) and the nearest-neighbour misuse (`contrast`).
   - **Counterexample Test** (`turn_kind: "falsify"`, one round): capture the learner's statement verbatim (v1); if it overgeneralizes, break it with one counterexample that satisfies it as written; the learner patches it; capture v2.
   - **Verify Every Turn**: Before emitting any collision, evaluation, boundary question, counterexample, hint, or practice item, dispatch `verifier` (`mode: "fact_check"` or `mode: "quiz_audit"`) with the learner-attempt flags and pause. Emit only upon a `PASS` receipt.
   - **Pause after every mini-checkpoint** to invite questions.
3. **Practice**:
   - At the end of each checkpoint, deliver a single **unlabeled** practice item (the stem never names the concept for selection/application items; naming is allowed only for a meaning/anatomy read) requiring a **3-line qualitative trace** (cue & principle → mechanism/knob-turn → direction & extreme check).
   - Grade the learner's reply using `verifier` (`mode: "grade_audit"`) — the mechanism and direction are graded, not a scalar, and no derivation is required.
   - Retain attempt metadata (qtype, confidence, hints) in conversation context.
   - Pause again after grading.

---

## Step 4: Lesson End — Operational Intuition Battery & Handoff

1. **Operational Intuition Battery** (not a quiz-plus-summary):
   - **Perturbation**: mutate a load-bearing assumption or term just learned; the learner predicts the qualitative downstream behaviour (which way it moves, what breaks). Verify and grade via `verifier` (`grade_audit`, `pow: "perturbation"`).
   - **Sabotage (Misapplication)**: present a plausible real-world *use* of the concept (or a look-alike) where a `condition` is violated; the learner names the broken assumption and what should have been done instead. No algebraic bug-hunting (`grade_audit`, `pow: "sabotage"`).
   - **Clone** (two phases): first ask the learner to explain the concept in their own words ("teach it to a novice"). Do **not** dispatch anything yet. When the learner replies, dispatch the **`naive-student`** subagent with `concept`, a seeded plausible `misconception`, `prereq_level` (the concept's prerequisites), a **qualitative** `target_task` (a prediction or tool choice), and `learner_transcript` = the learner's teaching reply verbatim. `naive-student` makes the qualitative call using only what the learner explicitly said. Success logs as `feynman_pass`; failure as `feynman_fail`.
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
4. **Auto-Ingest (Inline)**: Do not stop after the handoff and do not tell the learner to run `/ingest` — the lesson end ingests automatically, in this same turn sequence.
   1. Dispatch **`clerk`** (`mode: 'ingest'`) with the handoff as the source of truth:
      ```python
      invoke_subagent(
          Subagents=[{
              "TypeName": "clerk",
              "Role": "State Clerk",
              "Prompt": "mode: 'ingest', source: 'Learning System/Core/Pending Ingest.json', topic: '<topic>', slug: '<slug>', concepts: [...]"
          }]
      )
      ```
      Wait for the `CLERK_RECEIPT` with `mode: 'ingest'` (wiki pages written or enriched, `Active Concepts.md` / `CURRICULUM.md` updated, `audit_state.py` run, state committed).
   2. Dispatch **`auditor`** (`mode: 'review_gate'`) on the written wiki pages:
      ```python
      invoke_subagent(
          Subagents=[{
              "TypeName": "auditor",
              "Role": "Wiki Auditor",
              "Prompt": "mode: 'review_gate', target_files: ['Knowledge Wiki/wiki/<page>.md', ...]"
          }]
      )
      ```
      On in-scope `ISSUES` (unverified claims, missing provenance, broken links), re-dispatch `clerk` with the corrections and re-audit until a clean `PASS`. State/bookkeeping findings stay as context notes and do not block.
5. **Completion Summary**: Present the lesson completion summary (concepts mastered, wiki pages written/enriched, next review dates, state audit 0 errors). Verify the rendered summary with `verifier` (`mode: 'fact_check', turn_kind: 'answer', draft: '<exact summary>', claims: [...], raw_files: [...]`) when it is substantive. Never leave the learner with a pending `/ingest` step.
