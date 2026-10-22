---
name: continue
description: Resume an in-progress or paused lesson at its recorded mini-checkpoint. Always delegates context recovery and the resume pointer to scout. Trigger with /continue.
---

# Continue Flow (`/continue`)

Resume a paused or in-progress lesson directly at its next atomic mini-checkpoint without re-starting the lesson from scratch.

---

## Step 0: Scout-First Context & Resume Pointer Recovery

The model reading this skill **must delegate context recovery to the `scout` subagent**. Do not search `Learning System/Lessons/`, `Learning System/Sessions/`, or source material yourself, and do not resume from an old digest just because it is under 7 days old.

1. **Flow Marker**: Include `[[FLOW:resume]]` in your internal thought/context.
2. **Mandatory Scout Dispatch**: On every `/continue` — fresh digest or not — dispatch **`scout`** with `purpose: "resume"` and end your turn:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "scout",
           "Role": "Resume Scout",
           "Prompt": "mode: 'lesson', purpose: 'resume', topic: '<topic if known>', slug: '<slug if known>'"
       }]
   )
   ```
   Pause and await `SCOUT_RECEIPT`. Scout owns the search: it locates the newest non-`done` lesson and the latest session note, extracts the resume pointer, re-reads core metadata, and re-grounds sources when the digest is older than 7 days or missing.
3. **Read the Receipt, Not the Directories**:
   - Use the receipt's `lesson_file`, `session_file`, and `resume_from` (`Checkpoint N/M, mini K/L`). Do not re-derive or guess them from filenames.
   - If `resume_from` is `null` or `status: "none"`, inform the learner that no in-progress lesson exists and suggest `/lesson` to start the next topic.
   - If `failed_refs` or `contradictions` are non-empty, surface them with a visible `⚠️` callout before resuming; never silently resume on incomplete sources.
4. **Read the Identified Lesson for Narrative Continuity**: Read only the `lesson_file` and `session_file` named by the receipt (not the directories, not other lessons), then proceed to Step 1.

---

## Step 1: Resume Teaching

1. State clearly to the learner which topic and mini-checkpoint is resuming, using the receipt's `resume_from`.
2. Follow the **mini-checkpoint pause protocol** and the Collision → Sketch the Move → Read the Formula & Hunt the Boundary → Counterexample Test ladder from [pedagogy.md](../teach/references/pedagogy.md).
3. **Verify Every Turn**: Before presenting each collision, Socratic hint, boundary-hunt question, counterexample, practice item, or grade, dispatch **`verifier`** and await `PASS`.
4. At lesson end, execute the Operational Intuition Battery (perturbation, misapplication-spotter, naive-student clone), delegate the final handoff write batch to **`clerk`** (`mode: 'lesson_handoff'`), dispatch **`auditor`** (`mode: 'tutor_audit'`) to verify the handoff files, then **auto-ingest inline** — dispatch **`clerk`** (`mode: 'ingest'`) on `Learning System/Core/Pending Ingest.json` and **`auditor`** (`mode: 'review_gate'`) on the written wiki pages, looping until the audit returns `PASS`, before presenting the completion summary. Never instruct the learner to run `/ingest` manually.
