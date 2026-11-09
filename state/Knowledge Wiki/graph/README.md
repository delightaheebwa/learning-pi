# Knowledge graph — propositions + reasoning chains

Durable, append-only record of what has been taught: the ideas of a subject and
the arguments that derive them. It is **world knowledge, never learner state** —
no mastery, verdicts, confidence, attempts, or "the learner understands X". A
misconception enters as its true correction. Evidence about the learner lives in
`Learning System/Core/Attempts.json` and `🧯 Mistakes.md`.

Written **only** by `pi/graph.py` in the learning-pi control layer, run by the
Clerk during ingest (`merge` / `retract`). Agents never hand-edit these files.

**Backfill:** on 2026-10-26 the ledger was seeded once from the existing wiki
pages (one-time extraction, independently audited). Those records cite the wiki
page they came from as their provenance `file`, alongside session-ingest records.

## Files

| file | holds |
|---|---|
| `nodes.jsonl` | propositions: one line per assertion |
| `chains.jsonl` | reasoning chains: a premise set that jointly entails a conclusion |

## Node line

```
{"id":"n_ab12cd34ef","op":"define","name":"Row independence",
 "statement":"A linear layer acts on each row independently.",
 "aliases":[],"provenance":[{"file":"…/Lesson.md","message":"…"}],
 "createdAt":"…"}
```

- `id` is content-derived from the normalized statement: re-asserting the same
  proposition appends a `link` line instead of creating a duplicate.
- `statement` is the identity anchor: one self-contained, precise claim.
- A re-encounter appends `{"id":…,"op":"link","statement":"<verbatim phrasing>",
  "provenance":[…]}` — the phrasing joins `aliases[]`, provenance unions, and the
  original statement is never overwritten.
- `{"id":…,"op":"retract","reason":"…"}` tombstones an id.

## Chain line

```
{"id":"arg_…","op":"assert","premises":["n_…","n_…"],"conclusion":"n_…",
 "statement":"A ∧ B ⟹ C","provenance":[…]}
```

Premises jointly entail the conclusion. Chains are deduped by premise set +
conclusion. **Edges are never stored**: `graph.py export` derives the rendered
graph, minting one implication node per chain (premises -> ⟹ -> conclusion), so
two independent arguments for one conclusion stay two diamonds.

## Commands

```
python3 "$HOME/learning-pi/pi/graph.py" list --json         # compact read for probes/attacks
python3 "$HOME/learning-pi/pi/graph.py" status              # integrity + counts
python3 "$HOME/learning-pi/pi/graph.py" export              # mermaid derived view
python3 "$HOME/learning-pi/pi/graph.py" retract ID --reason "…"
```

`merge` reads a candidate spec on stdin (see the `pi/graph.py` module docstring):
new propositions carry `name`/`statement`/`provenance`, re-encounters carry
`link_to`, and chains reference `@N` (spec nodes) or `n_…` (existing) ids.
