---
name: llm-wiki
description: Build and maintain a Karpathy-style personal LLM wiki from notes, screenshots, clipped pages, and other source files. Use when asked to ingest, dump notes or screenshots into a persistent wiki, query, lint, cross-link, or update the wiki.
---

# LLM Wiki

## Overview

Turn raw sources into a persistent markdown wiki. Keep the source layer immutable, the wiki layer curated, and the index/log updated on every ingest.

## Layout

Paths are relative to the working repository root (the learning-system checkout).

- `Knowledge Wiki/raw/sources/` for source notes and clipped text
- `Knowledge Wiki/raw/assets/` for screenshots and other attachments
- `Knowledge Wiki/wiki/` for curated wiki pages
- `Knowledge Wiki/index.md` for the catalog of pages
- `Knowledge Wiki/log.md` for the chronological record
- `Knowledge Wiki/AGENTS.md` for the local schema and operating rules

## Ingest

When asked to ingest, treat it as a source-processing job.

1. Preserve every raw source in `raw/sources/`.
2. Copy screenshots or other attachments into `raw/assets/` and link them from the source note.
3. Read the source carefully and extract:
   - core claims
   - entities
   - concepts
   - open questions
   - contradictions or weak spots
4. Update the wiki layer with small, focused pages.
5. Update `index.md` and append a log entry.
6. Keep unresolved questions visible instead of dropping them.

If the source is mostly screenshots, make a source note that embeds the images and then build the wiki pages from the extracted ideas.

## Provenance (required)

Every page starts with a provenance marker on its first lines:

```
<!-- provenance: status=<verified|synthesis|learner-note|unverified> | source=<ref> | verified-by=<who> | date=YYYY-MM-DD -->
```

- New pages default to `status=synthesis` (AI synthesis from the source), with
  `source=` the raw-source file (or the lesson/URL it came from) and
  `verified-by=—`.
- A page becomes `status=verified` only when a verifier (fact-check / review-gate)
  has checked it against the cited source; record `verified-by=` and the date.
- The learner's own understanding goes on as `status=learner-note`.
- Never upgrade a status without the check. Lint with
  `python3 scripts/wiki_provenance.py`; an unstamped page counts as `unverified`.

Trust order: **raw source > verified claim > labelled synthesis > learner note**.
A wiki page is never a source of truth for a claim it does not cite; the
citation is the evidence, the page is the map.

## Learner-authored understanding ("My understanding", P1.7)

Every **concept** page carries a `## My understanding` section written in the
learner's own words. The learner authors it (captured verbatim during the
session at the learner-consolidation rung and carried in the lesson handoff's
`learner_understanding`); the AI never ghost-writes it.

- **Preserve and append — never overwrite.** The Clerk places the learner's
  text verbatim under `## My understanding` and may annotate *around* it
  (`Source framing:` / `External angle:` lines, a `⚠️ Sources disagree`
  callout, a missing-piece note), but must not paraphrase, polish, or replace
  the learner's words.
- Mark the section as the learner's: set the page provenance
  `status=learner-note` for that block (a page may be `status=synthesis`
  overall while its `## My understanding` block is the learner's note), and
  record it in the page's provenance line.
- The learner's note is *their model*, not a verified claim: check it against
  the cited source and name plainly what is wrong or missing — do not rewrite
  it. Corrections the learner accepts become an annotation, not a replacement.

Sample page shape:

```markdown
<!-- provenance: status=synthesis | source=raw/sources/... | verified-by=— | date=2026-10-08 -->
# Eigenvalues

**Insight:** …

## My understanding
> status=learner-note — the learner's words, verbatim, preserved.
> "An eigenvector is a direction the matrix only stretches, so the eigenvalue is how much it stretches it."

**Source framing:** the curriculum states it as Av = λv.

## Notes
…
```

## Wiki maintenance

- Keep raw sources immutable.
- Prefer short pages with one main idea.
- Use wiki links aggressively so related ideas connect.
- Revise existing pages instead of duplicating them.
- If new material contradicts an old claim, say so directly.
- If a concept appears often, give it its own page.

## Query

When asked a question about the wiki, read `index.md` first, then open the relevant pages, then synthesize the answer. Prefer explicit source references back to the wiki pages and raw sources.

## Lint

Periodically check for:

- orphan pages
- stale claims
- missing cross-links
- duplicate pages
- unresolved questions
- concepts that should become their own pages

## Output discipline

- Use markdown.
- Use relative links inside the wiki.
- Keep filenames stable and descriptive.
- When in doubt, create a note rather than losing information.

## Source of truth

The repository working copy is authoritative. Any external mirror (knowledge base, notes app) is a convenience copy that must never be edited and pushed back; always update the repo copy first.
