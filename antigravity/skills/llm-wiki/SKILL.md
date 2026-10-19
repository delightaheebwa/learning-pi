---
name: llm-wiki
description: Build and maintain a Karpathy-style personal knowledge wiki from notes, source texts, clipped documents, and lesson handoffs. Trigger with /llm-wiki or during wiki maintenance.
---

# LLM Wiki

Build, query, cross-link, and maintain a Karpathy-style personal knowledge wiki with strict provenance and source tracking.

---

## Directory Layout

All paths are relative to the learning-system repository root:
- `Knowledge Wiki/raw/sources/`: Immutable raw source texts and clipped reference passages.
- `Knowledge Wiki/raw/assets/`: Diagram images, screenshots, and visual media attachments.
- `Knowledge Wiki/wiki/`: Curated markdown concept and insight pages.
- `Knowledge Wiki/index.md`: Catalog of pages categorized by domain and topic.
- `Knowledge Wiki/log.md`: Chronological changelog of ingests and edits.
- `Knowledge Wiki/AGENTS.md`: Local schema and operating rules.

---

## Provenance Header (Mandatory)

Every page in `Knowledge Wiki/wiki/` begins with a provenance marker on its first lines:

```markdown
<!-- provenance: status=<verified|synthesis|learner-note|unverified> | source=<ref> | verified-by=<who> | date=YYYY-MM-DD -->
```

- `status=synthesis`: Default for new pages created by AI synthesis from a cited raw source.
- `status=verified`: Applied only after an independent verification run (`verifier` or `auditor`).
- `status=learner-note`: Applied specifically to the learner's own stated conceptual understanding.
- Verify provenance compliance at any time by running:
  ```bash
  python3 scripts/wiki_provenance.py --root .
  ```

---

## Learner-Authored Understanding (`## My understanding`)

Every concept page contains a `## My understanding` section:
1. **Preserve Verbatim**: Capture the learner's exact words from the session ladder (Rung 3). The AI must **never** polish, rewrite, or ghost-write this section.
2. **Annotate Around**: The AI adds contextual notes (`Source framing:`, `External angle:`, or `⚠️ Sources disagree`), but leaves the learner's quote untouched.
3. **Format**:
   ```markdown
   ## My understanding
   > status=learner-note — the learner's words, verbatim, preserved.
   > "An eigenvector is a direction the matrix only stretches, so the eigenvalue is how much it stretches it."

   **Source framing:** the curriculum defines it as Av = λv.
   ```

---

## Maintenance & Integrity

- **Section-Level Reading**: Avoid reading entire massive wiki pages. Use `python3 scripts/ops.py bundle "Knowledge Wiki/wiki/<page>.md@^## "` to inspect headings, then fetch only the relevant section.
- **Batch Updates**: Apply multi-file wiki updates and log appends in a single `ops.py apply` batch.
- **Cross-Linking**: Always use relative links between wiki pages (e.g. `[Eigenvalues](Eigenvalues.md)`).
