# Knowledge Wiki: local schema and operating rules

This file documents how the wiki layer of this repo is structured and
maintained. The canonical build and maintenance rules live in
`learning-pi/.pi/skills/llm-wiki/SKILL.md`, and the copy under `state/Skills/`
is a frozen legacy snapshot. This file is the local contract for the files in
this folder.

## Layout

```
raw/sources/   immutable raw layer: source notes and clipped text, never edited after ingest
raw/assets/    screenshots and attachments, linked from the source notes
wiki/          curated wiki pages: short, single-idea pages, aggressively cross-linked
graph/         knowledge graph: propositions and reasoning chains, machine-written ledger
index.md       catalog of all wiki pages, updated on every ingest
log.md         chronological record of ingests, one entry per ingest
```

## Rules

These rules apply to every wiki file:

- Raw sources are immutable. Once ingested into `raw/sources/`, a source is never
  rewritten. Corrections land in the wiki layer or in a new source note.
- Wiki pages are short and hold one main idea each. Split, do not bloat.
- Cross-link aggressively. Related ideas connect with `[[wikilinks]]` or
  relative markdown links.
- Revise, do not duplicate. If a concept already has a page, update it with
  genuinely new material instead of creating a near-copy.
- Contradictions are stated directly. If new material conflicts with an old
  claim, say so on the page.
- Keep unresolved questions visible. Never drop an open question during
  maintenance.
- Update `index.md` and `log.md` on every ingest, per the canonical
  `.pi/skills/learning-system/SKILL.md`.

## Knowledge graph

`graph/nodes.jsonl` and `graph/chains.jsonl` are the durable ledger of
propositions and reasoning chains. These rules apply:

- Store world knowledge only. Never store mastery, verdicts, confidence,
  attempts, or a claim that the learner understands something. A misconception
  enters as its true correction. Learner evidence belongs in
  `Learning System/Core/Attempts.json` and `🧯 Mistakes.md`.
- The files are machine-written. Only `pi/graph.py` in the learning-pi control
  layer writes them, through `merge` and `retract` run by the Clerk during
  ingest. Never hand-edit, append to, or rewrite the JSONL.
- Records are append-only and provenanced. Every record names the source file it
  came from. A re-encounter appends a `link` line with the verbatim alias and a
  provenance union, and corrections are `retract` tombstones. Format and
  commands are in `graph/README.md`.
- Edges are derived, not stored. `graph.py export` produces the rendered graph,
  with implication nodes per reasoning chain.

## Provenance and trust order

The wiki is a synthesis layer, not a source. Trust flows from evidence:

> raw source > verified claim > labelled AI synthesis > learner note

Every page carries a provenance marker on its first lines:

```
<!-- provenance: status=<verified|synthesis|learner-note|unverified> | source=<ref> | verified-by=<who> | date=YYYY-MM-DD -->
```

- `verified`: a claim checked against the cited source by a verifier, either
  `fact-check` or `review-gate`, or by a human.
- `synthesis`: AI synthesis from the source or sources, not independently
  re-checked.
- `learner-note`: the learner's own understanding and notes.
- `unverified`: not yet classified. This is the default, treated as synthesis
  quality and never authoritative.

An unstamped page is treated as `unverified`. A wiki page is never a source of
truth for a claim it does not cite. The citation is the evidence, and the page
is the map. Corrections update the status in place and, when a claim changes,
state the change on the page. If a source is retracted, mark the dependent pages
`unverified` and re-check them. Do not leave a corrected claim looking verified.

Lint or stamp with `python3 scripts/wiki_provenance.py [--check | --json | --stamp]`.

## Learner-authored understanding

Concept pages carry a `## My understanding` section in the learner's own words.
The learner writes it during the session at the learner-consolidation rung, not
the AI:

- The Clerk preserves and appends it, and never overwrites, paraphrases, or
  rewrites it. The AI may annotate around it with a `Source framing:` or
  `External angle:` note beside it, but the learner's words stay verbatim.
- When the section is the learner's own text, the page provenance records
  `status=learner-note` for it. A page may be `status=synthesis` overall while
  its `## My understanding` block is the learner's note.
- The learner's words are captured at consolidate in `learning-teach` and passed
  to the Clerk in the lesson handoff. The Clerk places them on the page.
- Trust order still holds. The learner's note is their model, not a verified
  claim. The AI's job is to check it against the cited source and name what is
  missing, not to replace it.

## Source of truth

This repo is authoritative. Any Open WebUI mirror, such as the Knowledge base or
Notes, is a convenience copy that must never be edited and pushed back. Always
update the repo copy first.
