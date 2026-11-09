# SESSION: Structured Outputs — JSON, Schema Validation, Constrained Decoding (Phase 11 L03, branch) — 2026-11-09

> **Purpose:** record of the interrogation up to the pause, and the provenance of everything ingested from it. Written by the pause-time ingest (Clerk) from the Tutor's inline handoff — **no lesson file, no learning record and no `Pending Ingest.json` existed on disk at that moment** (surfaced, not merged; there was nothing to disagree with). **Amended 2026-11-09 by the finalize `/ingest`:** the Tutor subsequently wrote the lesson file (`Learning System/Lessons/Lesson — Structured Outputs — 2026-11-09.md`, commit `7e38b5b`) and the `/pause` marker (`Learning System/Core/Pending Ingest.json`). Both were read at finalize and **agree with this note**: lesson-file `Status: PAUSED — mid-repair (partial close)` ↔ handoff `status: paused`, and lesson-file `Resume from:` ↔ handoff `resume_from` (the row-4 fresh-surface discriminator at `{"product": "Sony", "price": 348}`). Nothing disagreed, so nothing was merged; the marker was consumed and cleared, the lesson stays **in-progress**, the Scout digest is kept.

## Session Info

- **Date:** 2026-11-09
- **Topic:** Structured Outputs: JSON, Schema Validation, Constrained Decoding — `https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/03-structured-outputs` (Rohit), Further Reading: OpenAI structured-outputs docs, Outlines (paper + repo), XGrammar, LMQL, Anthropic tool use + native structured outputs, Instructor, JSON Schema spec.
- **Track:** `aiefs` (branch — off the sequential curriculum position, which remains Phase 1 L10)
- **Prerequisites Reviewed:** next-token distribution & decoding; tokenization / subword vocabulary; JSON Schema semantics; `Prompt Engineering` (the conditioning-mass model, reused rather than re-taught).
- **New Concepts Introduced:** `Structured Outputs (JSON contract)`; `Constrained Decoding (parser-state masking)`; `JSON Schema Validation & Retry (Pydantic + Instructor)`.
- **Status at pause:** **PAUSED (partial)** — `battery_withheld`: row 4 repair not closed (`NO_REPAIR_RECEIPT`), row 5 untouched, graduation/clone never reached.
- **Resume from (Tutor's words, verbatim):** "Fresh-surface closing check OPEN: decider-vs-rule discrimination at `{"product": "Sony", "price": 348}` (rule early-exits on parseable prefix; decider requires separator only). Next step on resume: finish the row-4 repair closure — a new fresh-surface check on the discriminator, then the rest of the battery. Then attack row 5 (failure-mode lump), then graduation."
- **Dependency events:** none recorded (`just_tell_me` / `told_repair` / `declined_generation` all absent) — no `Dependency:` line. The exit ticket was **declined** by the learner (recorded as an exit-ticket outcome, not as a dependency opt-out).

---

## What We Covered

- **Entry gate + closed-book spine check** (`free-recall`, confidence `sure`) — the learner reproduced Rohit's whole spine from their handwritten page: apps speak JSON / LLMs emit free text; prompting breaks ~90% of the time (fences, preamble); *it is a decoding problem*; the four-rung ladder; the failure-mode list; Pydantic → schema, Instructor → validate-and-feed-back. PASS. This is `learner_model.v1`, preserved verbatim on [[Structured Outputs (JSON contract)]].
- **Triage** of that model into seven rows (3 solid / 3 suspect / 1 missing — the full table is on the spine page). The session then attacked row 4, the one that decides whether "masking" is a mechanism the learner owns or a phrase they can recite.
- **The repair ladder on row 4 (why it consumed the session).** Three prediction probes failed first: rule output at `{"product": "Sony"` (answered "a comma or a closing bracket" — the *decider's* answer), "what class of positions does the rule break at" (`structural` miss), and two presses on the decider's two terms. Repair then went one rung at a time: nomenclature patch ("a boolean in progress" read correctly off the flags), the `tru`/`e` surface (re-posed rule-side and passed as the learner's own entailment), the flag-read check (failed, `execute`), re-own after the patch (passed), then two contrast rounds — both fused the rule layer, the flag layer and the distribution layer (`"the flag is any; e has high probability"`). Source returns exceeded the ladder budget; recorded as a **difficulty signal** (diagnosis regime over the edge for self-repair), not as a learner failure.
- **Closing fresh surface** at the discriminator `{"product": "Sony", "price": 348}` — 1 pass / 2 fail on the three parts (`,` right; *why-legal* and *granted/withheld* both answered from the last-char rule, including "string" where the decider's `required_left` is the point). **Row 4 stays OPEN.**
- **Never reached:** the row-5 attack (failure-mode catchability split), any schema-mode subset attack (row 7), graduation (`naive-student` clone), exit ticket (declined).

## Concepts Status After Session

| Concept | Previous Status | New Status | Mastery Type | Notes |
|---------|----------------|------------|--------------|-------|
| Structured Outputs (JSON contract) | — (new) | developing | concept (Feynman/clone owed) | 1 attempt, 1 pass; `interval_index` 1; next review 2026-11-16; spine solid, failure-mode split unattacked |
| Constrained Decoding (parser-state masking) | — (new) | developing | concept (Feynman/clone owed) | 13 attempts, 3 pass / 10 fail; `interval_index` 0, `consecutive_wrong` 3; next review **2026-11-12**; row 4 repair OPEN |
| JSON Schema Validation & Retry (Pydantic + Instructor) | — (new) | developing | concept (Feynman/clone owed) | no graded attempt; row 6 triaged solid from v1; next review 2026-11-12 (+3d) |

## Demonstrations of Understanding

- **Concept:** Constrained decoding — the decider (parser state × schema → legal token set)
  - **Confidence before evaluation:** `sure` (spine check and first predict probe), then `hunch` from round 2 on.
  - **Explanation:** "we simply hand the sampler e. … in this scenario, it is just e that has high probability. Otheriwse the rest are masked." / "the else part catches u. the rule gives the sampler ["any"] hence at that point tht llm is free to pick whatever has high probability from the distribution at that point."
  - **Assistant evaluated:** **Fail.** The masked-set claim is right; the *reason* fuses the distribution into the decoder (`e` has all the mass because everything else is zeroed, not because the model likes `e`), and the rule answer was handed the decider's answer on the closing surface.
  - **Mastery type:** pending_mastery (no Feynman/clone).
- **Concept:** Structured outputs — the problem and the ladder
  - **Confidence before evaluation:** `sure`.
  - **Explanation:** `learner_model.v1`, item 1–3 (verbatim on the spine page).
  - **Assistant evaluated:** **Pass** on the spine check; unchanged by anything later in the session.
  - **Mastery type:** pending_mastery.

## Open Questions

- [ ] **Row 4 closure (top of the queue):** a new fresh-surface check on the decider-vs-rule discriminator — the flags × schema mask read at a position where the prefix parses but the schema is not finished.
- [ ] **Row 5 (after row 4):** split the failure-mode lump by catchability — which failures enforcement tiers can catch (enum, array length, missing required) and which they cannot (a hallucinated value: type correct, value wrong).
- [ ] **Row 7 (off-path):** the schema-mode subset limitation — composition keywords unsupported, all fields must be required on OpenAI, numeric/string constraints stripped on Anthropic. Never surfaced to the learner.
- [ ] Does the flag set get run closed-book as a whole tuple at one position? Every flag was pressed separately; the tuple never was.

## Gaps & Misconceptions

- [ ] **Decider vs rule (row 4)** — three fusion episodes in one session: (i) round 1 attributed `e` to Rohit's rule after deriving `["any"]` correctly mid-session; (ii) round 2: "the flag is any … e has high probability"; (iii) the closing fresh surface, where the rule was handed the decider's answer. `miss_class: discrimination`; ledgered in `🧯 Mistakes.md`.
- [ ] **Calibration** — `sure` at the spine check, then 9 of 11 attack/check items graded fail: illusion-of-competence signal; ledgered as `metacognitive`.
- [ ] **`[?]` blanks in v1** — three blanks (`[?] of JSON` ×2, `ways to [?]`) were never re-worded by the learner; preserved as blanks on the page, deliberately not filled in by the AI.

## Open attacks (dependency order, as carried by the handoff)

Preserved here because the `/pause` marker that carried them (`Core/Pending Ingest.json`) was consumed and cleared at the 2026-11-09 finalize ingest. Nothing was in flight at the pause.

1. **row 4 closure** — decider-vs-rule fresh-surface discriminator. `miss_class: discrimination`, `requires: null`, `on_path: true`. **Open:** the 2026-11-09 closing check at `{"product": "Sony", "price": 348}` graded `,` correct and both reasons wrong. Resume rung: a **new** fresh surface after a flags × schema mask re-cap, then an own-words restatement.
2. **row 5** — split the failure-mode lump on catchability (a hallucinated value — "type correct, value wrong" — escapes every enforcement tier). `requires: ["row 4 closure"]`, `on_path: true`. **Not yet attacked.**
3. **row 7** — OpenAI schema mode supports only a subset of JSON Schema (composition keywords unsupported; `strict` requires all fields required). `requires: null`, `on_path: false`. **Recorded, off-path this session, never surfaced to the learner.**

Full triage rows 1–7 with buckets, quotes and the `requires`/`on_path` columns live on `Knowledge Wiki/wiki/Structured Outputs (JSON contract).md` → `## Interrogation record (2026-11-09)` (that table was **not** lost with the marker).

## Next Steps

`/continue` resumes this branch at the **open fresh-surface discriminator** (row 4 closure), then row 5, then graduation (clone + exit ticket). The Phase 1 L10 pointer (Checkpoint 6/6, mini 1/3) is untouched — it remains the sequential curriculum position.

---

## Interleaving

Single-concept session: the three new concepts are one lesson spine (contract → mechanism → guard), interleaved only by question type (free-recall → predict probes → contrast rounds → fresh surface). `Constrained Decoding` is the retrieval target for the next review; the other two are on the same 3-day clock but have no failed items yet.

## Provenance

- **Tutor handoff:** inline (task payload) — `learner_model.v1` verbatim, `triage[]` (7 rows with buckets, `requires`/`on_path`), `open_attacks[]` in dependency order, `attempts[]` (14 items), `mistakes[]` (2), `battery_withheld`, `resume_from`. **Absent from disk:** `Lessons/Lesson — structured-outputs — *.md`, `Learning Records/Record — Structured Outputs — *.md`, `Core/Pending Ingest.json`. Nothing was invented to fill those; the session note is this ingest's reconstruction of the inline handoff. **Reconciled 2026-11-09 (finalize ingest):** the lesson file now exists (`Lessons/Lesson — Structured Outputs — 2026-11-09.md`, commit `7e38b5b`) and the `/pause` marker existed and has been cleared; the lesson file's `Status:` / `Resume from:` agree with the handoff verbatim. Still **owed:** the learning record (`Learning Records/Record — Structured Outputs — *.md`) — a paused lesson does not close one.
- **Scout digest:** `Learning System/.tmp/context-01a1bf90-c0bf-74e9-ae87-6014964ff653-structured-outputs.json` (fetched 2026-11-09, 11 raw bodies live-fetched, `failed_refs: []`, no drift — first digest for this slug). **Kept** (partial close, inside its 7-day TTL).
- **Raw sources:** 12 files `Knowledge Wiki/raw/sources/2026-11-09 - structured-outputs - *.md`.
- **Attempts:** 14 recorded from the handoff in order (1 spine pass on `Structured Outputs (JSON contract)`; 13 on `Constrained Decoding`, 3 pass / 10 fail).
