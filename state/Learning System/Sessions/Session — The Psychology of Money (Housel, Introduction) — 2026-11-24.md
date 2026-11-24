# SESSION: The Psychology of Money (Housel, Introduction) — 2026-11-24

> **Purpose:** Capture what happened in this learning session. The assistant uses this to update the Knowledge Base at the end of the session.

## Session Info

- **Date:** [[2026-11-24]]
- **Topic:** The Psychology of Money — Morgan Housel, *The Psychology of Money: Timeless Lessons on Wealth, Greed, and Happiness*, **Introduction** (learner-supplied PDF + learner-authored mental model)
- **Mode:** standalone ingest (off-curriculum, no Tutor interrogation, no lesson file, no `Pending Ingest.json`)
- **Prerequisites Reviewed:** none — nothing was retrieved, graded, or repaired in this ingest
- **New Concepts Introduced:** `Psychology of Money (soft skill)` · `Personal Experience Shapes Financial Beliefs`

---

## What We Covered

This ingest consumed material the learner brought directly: a **self-authored Mermaid mental model** of what drives financial outcomes, plus three **verbatim passages** from Housel's Introduction offered as the model's support.

- The model: `Psychology`, `History`, `Personal experiences` and `Emotions` all feed **human behaviour with money**; **financial knowledge** points at *better financial behaviour* with the label **"Does not guarantee"**; behaviour feeds through to **financial outcomes**. Its shape is a **causal graph with one negated edge**, not a budget equation — the outcome variable is at the end of a behavioural chain.
- Passage 1 (*"financial success is not a hard science. It's a soft skill, where how you behave is more important than what you know."*) grounds the negated `FK → FB` edge and supplies the concept of money as a **soft skill**: execution is not discharged by knowing the rules.
- Passage 2 (*0.00000001% of what's happened in the world vs maybe 80% of how you think the world works*) grounds `EXP → HB`: the evidence base for a money worldview is negligible and its weight is overwhelming, which is why equally smart people disagree in good faith.
- Passage 3 (*"every financial decision … checks the boxes they need to check … that story has been shaped by their own unique experiences"*) grounds `HB → FB → OUT`: behaviour is **story-driven**, so outcomes are evidence about behaviour rather than about knowledge.

**Method notes (no teaching, no grading):** no items were asked, so there are no verdicts, no `Attempts.json` attempt records, no Mistakes rows and no calibration readout. Both rows are `developing` with `attempts: []` — the scheduler dates are stubs, and mastery is **unknown**, not zero.

---

## Concepts Status After Session

| Concept | Previous Status | New Status | Mastery Type | Notes |
|---------|----------------|------------|--------------|-------|
| Psychology of Money (soft skill) | — (new) | developing | pending / unknown — no attempt recorded | next review 2026-11-27; wiki page created with the learner's full model verbatim under `## My understanding` |
| Personal Experience Shapes Financial Beliefs | — (new) | developing | pending / unknown — no attempt recorded | next review 2026-11-27; wiki page created with the learner's `EXP → HB` edge verbatim |

---

## Demonstrations of Understanding

None. This was an ingest of learner-supplied material, not an interrogation: no closed-book item, no micro-check, no Feynman explain-back, and no `grade-audit` ran. Nothing here should be read as evidence that either concept is held.

---

## What the model gets right, and what it leaves open

- **Right, and load-bearing:** the negated arrow. `Financial knowledge → behaviour` is drawn as a *non-guarantee* rather than as an absence, which is the correct logical strength and the sentence the source actually makes.
- **Right, and easy to lose:** outcomes sit **downstream of behaviour**, so a good outcome is not evidence of good knowledge — and a bad outcome is not evidence of bad knowledge.
- **Added by the learner, not by the quoted passages:** the `PSY`, `HIS` and `EMO` edges into behaviour. Only `EXP → HB`, the negated `FK → FB`, and `HB → FB → OUT` are evidenced by the three quotations supplied. Flagged on both wiki pages, not removed.
- **Left open:** what actually moves the soft skill (imitation, feedback, pre-commitment, or nothing teachable); whether history/emotion enter *through* experience or as separate inputs; and the failure regime where the knowledge term dominates (single-shot, fully computable decisions such as fee arithmetic — "it's just psychology" is a misapplication there).

---

## Session Outputs

- **Wiki (2 new pages):** `Knowledge Wiki/wiki/Psychology of Money (soft skill).md`, `Knowledge Wiki/wiki/Personal Experience Shapes Financial Beliefs.md` — both `status=synthesis` with a `status=learner-note` `## My understanding` block (the learner's model, verbatim, never polished).
- **Raw source note (new):** `Knowledge Wiki/raw/sources/2026-11-24 - psychology-of-money - housel-introduction.md` — the model and the three quotations preserved as supplied, with the provenance limit recorded (the PDF is not in the repo; the chapter was not otherwise read).
- **Active Concepts:** 2 new rows, both `aiefs` track (carried there so a plain `review` reaches them), `concept` / `developing`, `last_reviewed` 2026-11-24, `next_review` 2026-11-27 (+3d), `Last Q Type` `definitional`. **Live concepts 47 → 49.**
- **Attempts.json:** 2 stub entries with `attempts: []`, `interval_index` 0, no consecutive counters, `feynman: null` — the row exists for scheduling, and the absence of attempts is preserved rather than papered over.
- **Mistakes:** none — nothing was answered wrongly, because nothing was asked.
- **Position:** unchanged. `MISSION.md`, `CURRICULUM.md`, the Learning Profile and the Active Concepts pointers still name **Phase 1 L10 — Dimensionality Reduction, paused at Checkpoint 6/6, mini 1/3** as the curriculum resume; this ingest added an off-curriculum pair and moved no pointer.
- **Out of focus, surfaced not decided:** this content sits outside the AI-engineering mission entirely. It was ingested because the learner brought the model and the source, and it is filed beside the other off-curriculum branch rows (prompt engineering, software architecture, structured outputs) rather than folded into the curriculum. Whether a money/behaviour track gets any standing in the learning system is the learner's call, not this ingest's.

---

## Reading-mode retrofit — 2026-11-25

The reading mode (benchmark brief, free recall, fixed +1d/+1w/+1m retrieval) landed after the 2026-11-24 ingest. This section records the retro-integration of the session's retrieval layer.

- **Benchmark ingested.** The learner's separate ChatGPT session (share id `6b05d698-a7bc-83e9-b17b-c6affa3f92f9`, generated 2026-11-23 from the attached PDF extract) produced an Introduction-only benchmark: 15 questions, 5 low / 5 mid / 5 high, targets 90 / 80 / 70 from memory. It is seeded as `Psychology of Money (Introduction) — benchmark` (type `benchmark`, `interval_index` 0, session date 2026-11-24) via `ops.py benchmark`; the questions and levels live in `Learning System/Core/🎯 Benchmarks.json`, the row sits in `Active Concepts`, and the ladder is fixed: **+1d 2026-11-25 (due), +1w 2026-12-01, +1m 2026-12-24** — one attempt per shot, result-agnostic, a miss re-appears without moving the dates.
- **Free recall.** Not performed on 2026-11-24; the feature did not exist yet. The +1d retrieval session opens with the closed-book dump of the Introduction *before* the questions — that dump is the retrieval practice this session owed, one day late rather than skipped.
- **Keywords.** The final short list the learner asked for (20 terms) is preserved verbatim in `Knowledge Wiki/raw/sources/2026-11-25 - psychology-of-money - chatgpt-benchmark.md`. No groupings were recorded; connecting stayed with the learner.
- **Model revision trail.** The ingested Mermaid model matches the ChatGPT-suggested final structure. The earlier ASCII v1 and Mermaid v2 exist only in the shared chat; the raw source note of 2026-11-24 remains the anchor for the ingested model.
- **Queue reality.** The benchmark row is due today. The 5-slot queue was full with the overdue backlog (46 due reviews on this track) and draws due reviews by daily shuffle, which would have pushed the shot out by days. Fixed on 2026-11-25: a due benchmark session now rides as an extra slot after the cap and never displaces a due mistake or review, so the +1d shot fires today.
- **Grading requirement.** A retrieval shot graded against the book needs the PDF attached again — the repo holds only the three verbatim passages, so an unquoted check cannot be grounded.

---

## Open Questions

- [ ] If money behaviour is a soft skill, what is the *teachable* unit — rules that pre-commit behaviour (automatic saving, fixed holding periods), exposure to other people's samples, or explicit history/base-rate reading? The source names the difficulty and stops.
- [ ] Is the `EXP → HB` prior correctable, and by what? The Introduction diagnoses experience-shaped belief without prescribing a corrective.
- [ ] Do `PSY`, `HIS` and `EMO` reach behaviour *through* experience (one input with three names) or as genuinely separate inputs? The learner's model draws four arrows; the quoted passages evidence one.
- [ ] Neither concept has been retrieved once — the first `review` that reaches them is their first real test, and a `definitional` item on the negated arrow is the cheapest probe of whether the model was absorbed or merely written down.
