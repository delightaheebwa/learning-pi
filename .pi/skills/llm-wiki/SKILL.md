---
name: llm-wiki
description: Build and maintain a Karpathy-style personal LLM wiki from notes, screenshots, clipped pages, and other source files. Use when asked to ingest, dump notes or screenshots into a persistent wiki, query, lint, cross-link, or update the wiki.
---

# LLM wiki

Turn raw sources into a persistent markdown wiki. Keep the source layer immutable, the wiki layer curated, and the index and log current after every ingest.

## Layout

Paths are relative to the working repository root, the learning-system checkout.

- `Knowledge Wiki/raw/sources/` holds source notes and clipped text.
- `Knowledge Wiki/raw/assets/` holds screenshots and attachments.
- `Knowledge Wiki/wiki/` holds curated pages.
- `Knowledge Wiki/index.md` is the catalog.
- `Knowledge Wiki/log.md` is the chronological record.
- `Knowledge Wiki/AGENTS.md` holds the local schema and operating rules.

## Ingest

Treat an ingest as a source-processing job.

1. Preserve every raw source in `raw/sources/`.
2. Copy screenshots and attachments into `raw/assets/` and link them from the source note.
3. Read the source and extract its core claims, entities, concepts, open questions, and contradictions or weak spots.
4. Update the wiki layer with small, focused pages.
5. Update `index.md` and append a log entry.
6. Keep unresolved questions visible.

If the source is mostly screenshots, write a source note that embeds the images. Build the wiki pages from the ideas you extract.

## Provenance

Put a provenance marker on the first lines of every page:

```
<!-- provenance: status=<verified|synthesis|learner-note|unverified> | source=<ref> | verified-by=<who> | date=YYYY-MM-DD -->
```

New pages default to `status=synthesis`. Set `source=` to the raw source file, or to the lesson or URL the page came from. Set `verified-by=—`.

A page becomes `status=verified` only when a verifier such as fact-check or review-gate has checked it against the cited source. Record `verified-by=` and the date in that case. The learner's own understanding goes in as `status=learner-note`. Never upgrade a status without the check.

Lint with `python3 scripts/wiki_provenance.py`. An unstamped page counts as `unverified`.

The trust order is raw source, verified claim, labelled synthesis, then learner note. A wiki page is never a source of truth for a claim it does not cite. The citation is the evidence and the page is the map.

## The learner's own words

Every concept page carries a `## My understanding` section written by the learner. Capture it verbatim during the session at the learner-consolidation rung and carry it in the lesson handoff's `learner_understanding` field. The AI never ghost-writes it.

Preserve and append that section. Never overwrite it. The Clerk places the learner's text verbatim under the heading and may annotate around it with `Source framing:` and `External angle:` lines, a sources-disagree callout, or a missing-piece note. The Clerk must not paraphrase, polish, or replace the learner's words.

Mark the section as the learner's. Set the page provenance to `status=learner-note` for that block and record it in the provenance line. A page may keep `status=synthesis` overall while that block stays the learner's note.

The learner's note is their model, not a verified claim. Check it against the cited source and name plainly what is wrong or missing. Do not rewrite it. Corrections the learner accepts become an annotation, not a replacement.

Sample page shape:

```markdown
<!-- provenance: status=synthesis | source=raw/sources/... | verified-by=— | date=2026-10-08 -->
# Eigenvalues

**Insight:** …

## My understanding
> status=learner-note. The learner's words, verbatim, preserved.
> "An eigenvector is a direction the matrix only stretches, so the eigenvalue is how much it stretches it."

**Source framing:** the curriculum states it as Av = λv.

## Notes
…
```

## Maintenance

- Prefer short pages with one main idea.
- Link related ideas with wiki links.
- Revise existing pages instead of duplicating them.
- If new material contradicts an old claim, say so directly.
- If a concept appears often, give it its own page.

## Query

Read `index.md` first. Then open the relevant pages and synthesize the answer. Reference the wiki pages and raw sources explicitly.

## Lint

Check periodically for orphan pages, stale claims, missing cross-links, duplicate pages, unresolved questions, and concepts that should become their own pages.

## Output discipline

Use relative links inside the wiki. Keep filenames stable and descriptive. When in doubt, create a note rather than lose information.

## Source of truth

The repository working copy is authoritative. An external mirror such as a knowledge base or notes app is a convenience copy. Never edit it and push back. Update the repo copy first.
