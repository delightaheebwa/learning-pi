---
name: ingest
description: Ingest new learning material or finalize a completed/paused lesson handoff into the Knowledge Wiki and Active Concepts. Runs Clerk persistence, independent review gate, and state consistency audit. Trigger with /ingest [content or URL].
---

# Ingest Flow (`/ingest [content or URL]`)

Ingest notes, articles, or lesson handoffs into your personal Knowledge Wiki and spaced-repetition schedules.

---

## Step 0: Input Handling & Transcription

1. **Flow Marker**: Include `[[FLOW:ingest]]` in your internal thought/context.
2. **Handoff vs Standalone**:
   - If `Learning System/Core/Pending Ingest.json` exists (from a `/pause` or completed lesson), read it as the primary source of truth.
   - If standalone text or a URL is passed in the command, use that as the source.
3. **Handwritten Notes (Image Handling)**:
   - If the user attached an image of handwritten notes or a book page, transcribe it verbatim first.
   - Preserve headings, bullet structures, and math equations. Perform light spelling cleanup only; do not summarize or rephrase.

---

## Step 1: Persistence via Clerk

1. Dispatch the **`clerk`** subagent:
   ```python
   invoke_subagent(
       TypeName="clerk",
       Role="State Clerk",
       Prompt="mode: 'ingest', source: 'Pending Ingest.json' /* or raw content */"
   )
   ```
   Pause and await `clerk`'s completion.
2. `clerk` performs the overlap check, writes or enriches `Knowledge Wiki/wiki/<page>.md`, preserves `## My understanding` notes (`status=learner-note`), updates `Active Concepts.md` and `CURRICULUM.md`, runs `audit_state.py`, and commits state files to git.

---

## Step 2: Ingest Review Gate via Auditor

1. When `clerk` returns `CLERK_RECEIPT`, dispatch **`auditor`** to review the newly written wiki pages:
   ```python
   invoke_subagent(
       TypeName="auditor",
       Role="Wiki Auditor",
       Prompt="mode: 'review_gate', target_files: ['Knowledge Wiki/wiki/<page>.md', ...]"
   )
   ```
   Pause and await `auditor`'s verdict.
2. **Issue Resolution**:
   - If `auditor` finds in-scope content issues (unverified claims, missing provenance headers, or broken links), re-dispatch `clerk` with the required corrections, then re-audit.
   - Repeat until `auditor` returns a clean `PASS` (zero in-scope issues).
   - State/bookkeeping findings are surfaced as context notes and do not block the ingest.

---

## Step 3: Completion Summary

Present a concise summary to the learner:
- Ingested / enriched wiki pages and their links.
- New concepts added to `Active Concepts.md` and their next review dates.
- Confirmation of state audit cleanliness (`audit_state.py` report: 0 errors).
