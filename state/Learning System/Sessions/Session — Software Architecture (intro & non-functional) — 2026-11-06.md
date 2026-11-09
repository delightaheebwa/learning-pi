# Session — Software Architecture (intro & placement of 'non-functional') — 2026-11-06

**Type:** Teach (interrogation) — **PAUSED, clean** after a repair close (`partial: true` handoff; pause-banked ingest)
**Track:** branch, **off-curriculum** — learner-surfaced from *Head First Software Architecture*, Ch.1. Not a Rohit node; the sequential curriculum position (Phase 1 L10, Dimensionality Reduction) is **unchanged**.
**Resume from (handoff, verbatim):** "Checkpoint: open attack queued (see open_attacks), no attacks in flight — pause taken cleanly after repair close"

## Material (as supplied)

- **`material[0]`:** *Head First Software Architecture*, Ch.1 — **index entry only**, surfaced by the learner: "non-functional" filed under **requirements** — a label for **how a running system behaves**, not failures/downtime.
- **Provenance discipline:** the chapter body was **not read or fetched** in this session. Nothing below implies the learner read a source they did not bring. Raw source note: `Knowledge Wiki/raw/sources/2026-11-06 - software-architecture - head-first-ch1.md`.

## Learner model — v1 (verbatim, typos preserved, closed book)

> "I worked on Software architectire intro. my model is that software architecture is the part of software that is expensive and hard to change later. With it however, we can have maintainable and functional software otherwise we have software thats hard to mainiatin and non-fucntional software(unreliable)."

- **`learner_model.v2`:** `null` — no v2 this session (pause before graduation; v1 must not be rewritten or merged).

## Triage (handoff order preserved; no `requires` / `on_path` keys were supplied)

| # | Item | Bucket | Evidence |
|---|---|---|---|
| 1 | architecture = the parts that are expensive and hard to change later | **solid** | exit-ticket pass, closed-book |
| 2 | distinct readings of 'non-functional': still-running/unreliable vs never-starts/nothing-functioning | **solid** | fresh-surface repair close passed this session; learner restate: "so nothing is funcioning means not running completely while non-functional means unreliable" |
| 3 | with architecture → maintainable AND functional software; otherwise → non-functional (unreliable) | **suspect** | folds "functional" into the presence of architecture; exit-ticket tail, untested |

## Attacks

**Closed this session** (implied by the triage evidence; no per-attack log was carried in the handoff):

- the free-recall placement attack on "non-functional" — FAIL, then repaired fresh-surface → PASS.

**Open (dependency order — one attack, `on_path: true`):**

1. **`counterexample`** · `on_path: true` · **gap:** the *with-architecture → functional / otherwise → non-functional* tail of v1 · **plan (verbatim):** "A case that satisfies the learner's sentence as written and still breaks it: pick a system with solid architecture that fails at its core job, or one with poor architecture that still does exactly what it was asked to do — test both halves of 'otherwise → non-functional (unreliable)'. Do not reveal before the prediction turn."

No attacks were in flight at the pause.

## Attempts ledger (4 graded attempts, recorded in `Attempts.json` 2026-11-06)

| # | Concept | Qtype | Verdict | Confidence | Hints | PoW | Miss class | Evidence |
|---|---|---|---|---|---|---|---|---|
| 1 | Software Architecture — failure-list placement of 'non-functional' | free-recall | **fail** | hunch | 0 | counterexample | cue | learner abstained on placing never-starts under reading (A) or (B) |
| 2 | Software Architecture — failure-list placement of 'non-functional' | micro-check | **pass** | hunch | 0 | fresh-surface repair close | — | learner mapped "nothing is functioning" → not-running vs "non-functional" → unreliable in own words |
| 3 | Software Architecture — intro | free-recall | **pass** | sure | 0 | pause exit ticket | — | core architecture beat held closed-book |
| 4 | Software Architecture — intro | micro-check | **fail** | sure | 0 | pause exit ticket | structural | "i am confident in all of it" — no least-sure part, no breaking case; illusion-of-competence signal banked |

`Attempts.json` after the writes: `… — failure-list placement …` `interval_index` 1, `consecutive_correct` 1, mastery 0.62, `next_review` **2026-11-13** · `… — intro` `interval_index` 0, `consecutive_wrong` 1, mastery 0.38, `next_review` **2026-11-09**. Both `type: concept`, `feynman: null`.

## Mistakes banked

1. **Placement of "non-functional" — `structural`, `[miss: cue]`, status `graduated`** (repaired fresh-surface this session; the learner abstained rather than asserting a wrong reading).
2. **`Software Architecture — intro` — `metacognitive`, `[miss: structural]`, status `active`** — exit ticket: blanket "confident in all of it" next to a same-session fail. Deliver no confidence claim without a named weakest part.

## Dependency events

**None** — the handoff carries no `just_tell_me` / `told_repair` / `declined_generation`, so no `Dependency:` line is set.

## Notes for resume (handoff, verbatim)

> "Confidence flag is top of the resume queue: /continue opens with the counterexample trap on the v1 tail, then re-checks calibration before any further attack. Session already exercised error-detect (counterexample/source clash); perturbation and sabotage remain unexercised for the intro concept."

## Open questions

- Does the v1 tail survive the counterexample on **both** halves (solid architecture failing at its job; poor architecture still doing the job)?
- Calibration: can the learner name a least-sure part and a breaking case *before* answering? (The exit ticket says no as of 2026-11-06.)
- Which quality attributes can be generated unprompted beyond "reliable"? (The label is broader than the learner's instance.)

## Handoff integrity — surfaced, not merged

- **No `Learning System/Core/Pending Ingest.json`** and **no `Lessons/Lesson — software-architecture-*.md`** and **no Learning Record** exist on disk for this topic. The handoff arrived inline with the ingest task; this ingest reconciled state from that inline payload and wrote the session note itself. The Tutor's lesson file, learning record and `Pending Ingest.json` were **not** present, so their `Status:` / `Resume from:` fields could not be cross-checked against the handoff (nothing to disagree — nothing to merge).
- **No Scout digest** exists for this slug (`.tmp/context-*-software-architecture-intro-non-functional.json` absent) — consistent with a learner-surfaced, off-curriculum branch; no digest was consumed, deleted or invented.
- Attempts were recorded under the handoff's `attempts[]` order with the session date 2026-11-06 (the handoff carried no explicit date).
- `resume_from` ("Checkpoint: open attack queued…") carries no `Checkpoint N/M` fraction, so the L10 position-pointer check is unaffected.
