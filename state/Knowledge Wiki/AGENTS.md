# Knowledge Wiki — Local Schema & Operating Rules

This file documents how the wiki layer of this repo is structured and maintained. The canonical build/maintenance rules live in `Skills/llm-wiki/SKILL.md`; this file is the local contract for the files in this folder.

## Layout

```
raw/sources/   immutable raw layer — source notes and clipped text, never edited after ingest
raw/assets/    screenshots and attachments, linked from the source notes
wiki/          curated wiki pages — short, single-idea pages, aggressively cross-linked
graph/         knowledge graph — propositions + reasoning chains (machine-written ledger)
index.md       catalog of all wiki pages (updated on every ingest)
log.md         chronological record of ingests (one entry per ingest)
```

## Rules

- **Raw sources are immutable.** Once ingested into `raw/sources/`, a source is never rewritten; corrections land in the wiki layer or a new source note.
- **Wiki pages are short** — one main idea per page. Split, don't bloat.
- **Cross-link aggressively.** Related ideas connect with `[[wikilinks]]` / relative markdown links.
- **Revise, don't duplicate.** If a concept already has a page, update it with genuinely new material instead of creating a near-copy.
- **Contradictions are stated directly.** If new material conflicts with an old claim, say so on the page.
- **Keep unresolved questions visible.** Never drop an open question during maintenance.
- **index.md and log.md are updated on every ingest** (per `Skills/learning-system/SKILL.md`).

## Knowledge graph (`graph/`)

`graph/nodes.jsonl` and `graph/chains.jsonl` are the durable propositions +
reasoning-chains ledger. Rules:

- **World knowledge only.** Never mastery, verdicts, confidence, attempts, or
  "the learner understands X" — a misconception enters as its true correction.
  Learner evidence belongs in `Learning System/Core/Attempts.json` + `🧯 Mistakes.md`.
- **Machine-written.** Only `pi/graph.py` in the learning-pi control layer
  (`merge` / `retract`, run by the Clerk during ingest) writes these files.
  Never hand-edit, append to, or rewrite the JSONL.
- **Append-only + provenanced.** Every record names the source file it came
  from; re-encounters append a `link` line (verbatim alias + provenance union),
  and corrections are `retract` tombstones. Format + commands: `graph/README.md`.
- **Edges are derived, not stored.** The rendered graph (implication nodes per
  reasoning chain) is produced by `graph.py export`.

## Provenance & trust order

The wiki is a **synthesis layer, not a source**. Trust flows *from* evidence:

> raw source > verified claim > labelled AI synthesis > learner note

Every page carries a provenance marker on its first lines:

```
<!-- provenance: status=<verified|synthesis|learner-note|unverified> | source=<ref> | verified-by=<who> | date=YYYY-MM-DD -->
```

- `verified` — a claim checked against the cited source by a verifier
  (fact-check / review-gate) or a human.
- `synthesis` — AI synthesis from the source(s), not independently re-checked.
- `learner-note` — the learner's own understanding/notes.
- `unverified` — not yet classified (the default; treated as synthesis-quality,
  never authoritative).

**An unstamped page is treated as `unverified`.** A wiki page is never a source of
truth for a claim it does not cite; the citation is the evidence, the page is the
map. Corrections update the status in place and, when a claim changes, state the
change on the page. If a source is retracted, mark the dependent pages
`unverified` and re-check them — do not leave a corrected claim looking verified.

Lint / stamp: `python3 scripts/wiki_provenance.py [--check | --json | --stamp]`.

## Learner-authored understanding ("My understanding")

Concept pages carry a `## My understanding` section written in the **learner's
own words** (captured during the session at the learner-consolidation rung).
This section is authored by the learner, not the AI:

- The Clerk **preserves and appends** it — never overwrites, paraphrases, or
  rewrites it. The AI may annotate *around* it (a `Source framing:` /
  `External angle:` note beside it) but the learner's words stay verbatim.
- When the section is the learner's own text, the page provenance records
  `status=learner-note` for it (a page may be `status=synthesis` overall while
  its `## My understanding` block is the learner's note).
- The learner's words are captured at consolidate (`learning-teach`) and passed
  to the Clerk in the lesson handoff; the Clerk places them on the page.
- Trust order still holds: the learner's note is *their* model, not a verified
  claim — the AI's job is to check it against the cited source and name what is
  missing, not to replace it.

## Source of truth

This repo is authoritative. Any Open WebUI mirror (Knowledge base / Notes) is a convenience copy that must never be edited and pushed back; always update the repo copy first.