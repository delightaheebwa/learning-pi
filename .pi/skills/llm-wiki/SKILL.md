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
