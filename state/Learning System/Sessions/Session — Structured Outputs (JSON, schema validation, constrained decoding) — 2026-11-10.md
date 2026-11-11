# SESSION: Structured Outputs — JSON, Schema Validation, Constrained Decoding (Phase 11 L03, branch) — 2026-11-10 (session 2)

> **Purpose:** record of the **second** interrogation session on this branch — the one that closed triage row 4, opened and half-closed row 5 (the catchability axis), and paused at the array-length seam. **Provenance of this note:** written by the pause-time ingest (Clerk) from the Tutor's **inline handoff** (task payload), because **no 2026-11-10 lesson file, no `Core/Pending Ingest.json` and no learning record existed on disk** at that moment. Nothing was invented to fill those; the inline handoff is the only source and every learner quotation below is verbatim. **Disagreement surfaced, not merged:** the on-disk lesson file is the 2026-11-09 one, whose `Status:` / `Resume from:` describe session 1 (row 4 open). It now disagrees with this handoff (row 4 closed, resume at row 5) — see `## Handoff vs lesson file`. The 2026-11-09 session note (`Sessions/Session — Structured Outputs (JSON, schema validation, constrained decoding) — 2026-11-09.md`) remains the record of session 1 and was not rewritten.

## Session Info

- **Date:** 2026-11-10
- **Topic:** Structured Outputs: JSON, Schema Validation, Constrained Decoding — `https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/03-structured-outputs` (Rohit). **Declared read scope for this session (learner directive):** the source's **Problem** and **Concept** sections only.
- **Track:** `aiefs` (branch — off the sequential curriculum position, which remains Phase 1 L10, Checkpoint 6/6 mini 1/3)
- **Prerequisites in play:** next-token distribution & decoding; tokenization / subword vocabulary; JSON Schema semantics; `Prompt Engineering` (conditioning-mass model, reused not re-taught)
- **New Concepts Introduced:** none — session 2 is a continuation of the three rows opened 2026-11-09 (`Structured Outputs (JSON contract)`, `Constrained Decoding (parser-state masking)`, `JSON Schema Validation & Retry (Pydantic + Instructor)`)
- **Status at pause:** **PAUSED (partial, second consecutive pause)** — row 4 closed, row 5 half-closed, two source failure modes never reached, graduation (`entailment check` → `naive-student` clone → battery remainder) never opened
- **Resume from (Tutor's words, verbatim):** "Row 5, next attack: the array-length seam — learner's lump dropped the provider condition ('Schemas support minItems and maxItems but not all providers enforce them at the decoding level'); attack asks whether array-length failure is a property of the mode or of the provider choice. Then the two unlisted modes (nested-object depth, optional-field omission). Then graduation for the catchability axis: entailment check ('why must hallucinated values escape any schema-side gate?') → naive-student clone → battery remainder."
- **Dependency events:** none (`just_tell_me` / `told_repair` / `declined_generation` all absent) — no `Dependency:` line. The exit ticket was **declined** (an exit-ticket outcome, not a dependency opt-out), **second consecutive** decline.
- **Exit ticket:** **declined (banked without)**.

---

## Handoff vs lesson file (surfaced, not merged)

| Source | `status` | `resume_from` |
|---|---|---|
| Handoff (2026-11-10, inline) | paused, partial, session 2 | **row 5, the array-length seam** → then nested-depth + optional-omission → then graduation |
| Lesson file on disk (`Lessons/Lesson — Structured Outputs — 2026-11-09.md`) | `PAUSED — mid-repair (partial close)` | the **row-4** fresh-surface discriminator at `{"product": "Sony", "price": 348}` |
| Session note on disk (2026-11-09) | "PAUSED (partial) — `battery_withheld`" | the row-4 discriminator (its open attack #1) |

**They disagree, and the disagreement is not merged.** The lesson file and the 2026-11-09 session note are session-1 artifacts describing state that session 2 has moved: row 4 is now **closed** (the concept-level model was repaired and restated in the learner's own words; the one item that still failed tested Build-It grains outside the learner's declared read scope and is **banked out of scope**, not re-issued). The Clerk did **not** rewrite the Tutor-owned lesson file's `Status:` / `Resume from:`. **Owed (as recorded at the pause):** a 2026-11-10 lesson file (or a status update on the 2026-11-09 one) and the **learning record** — a second paused lesson still does not close one.

**Reconciled at the 2026-11-10 `/ingest`** (the pause-time reading above is kept as history — it is not rewritten): the Tutor took the status-update option on the 2026-11-09 lesson file. It now reads `Status: PAUSED — partial (session 2 banked 2026-11-10; second consecutive pause, exit ticket declined)` and `Resume from: row 5, next attack — the array-length seam …`, so the two artifacts **agree** and the disagreement documented above is superseded — not merged: the lesson file is the Tutor's artifact and the Clerk rewrote none of it. The Tutor also put the `/pause` marker on disk (`Core/Pending Ingest.json`: `partial: true`, the same `status`/`resume_from`, plus the scope-recalibration invariant); this ingest **consumed and cleared** it, kept the lesson `in-progress` and kept all three Scout digests. **Still owed: the learning record.** Two caveats left standing on the Tutor's lesson file, surfaced not edited: its `Session:` header still cites only the 2026-11-09 note (this note is the session-2 record), and its `Source:` line cites the 2026-11-09 `rohit` snapshot while session 2's declared read scope was the 2026-11-10 re-fetch (`Pending Ingest.json` `source_file`).

## Scope recalibration (learner directive — session invariant, verbatim)

> "all mental-model attacks target ONLY the Problem and Concept sections of the source site; the Build-It code and row 7 (provider-doc rules: all-fields-required, schema subset) are OUT of attack scope permanently for this lesson."

Carried as an **invariant**, not a preference: any future item on this lesson must be grounded in the Problem/Concept text, and no rule-side check from the Build-It section may be re-issued. Row 7 (provider schema subset) therefore stays recorded-and-off-path for the life of this lesson.

---

## learner_model

### v1 (2026-11-09, verbatim — unchanged; full text with its `[?]` blanks is on [[Structured Outputs (JSON contract)]])

The rows as recorded there; **triage row 5 = v1 item 4**, the failure-mode **lump**:

> "Some failure modes include: hallucinated values, array length [?], too long or too small array length, [?] fields, enum confusion."

### v2 patches this session (verbatim, each with the surface it answered)

1. **Catchability axis** (attack: where does `299.99` slip through? Then the Instructor retry on a schema-valid hallucinated price):

   > "the machine knows the schema and legal set. what it would have to know is the exact value for the price key of this particular json object. it slips through since it is a valid entry(number)."

   > (Instructor) "what it validates against is whether this breaks the schema or not. the info needed to flag this output doesnt exist anywhere in that loop."

2. **Enum seam** (attack: `"available"` against `["in_stock","out_of_stock","preorder"]`, rung by rung):

   > "constrained decoding masks \"available\" and hence high probability for \"in_stock\", \"out_of_stock\", \"preorder\" to be sampled from. constrained decoding is the one that hands the valid distribution to the sampler"

   Prompting rung, first attempt: > "the prompt lowers \"available's probability" — **patched in-session** to *lowered ≠ zero*, so the sampler can still emit it; the **absent component named**: FSM/CFG.

3. **Pipeline order** (after resolving a clash with the learner's own earlier words):

   > "raw distibuton → constrained decoding(fsm/cfg) → sampler"

   No-op reasoning for putting the mask after the sampler:

   > "its zeroing wouldnt be worth anything since the impure distribution has already been sampled from."

The three patches are **not** a whole-page v2: they cover the catchability seam, the enum rung and the pipeline order. The failure-mode lump's remaining members (array length, nested depth, optional-field omission) were not reached, so the lump is **half-split**.

---

## Triage as carried (dependency order)

| # | Item | Bucket | Evidence (verbatim from the handoff) | Queue |
|---|---|---|---|---|
| 1 | hallucinated values named without its fate | `missing` → **closed** | "closed this session: catchability axis established (schema-side gates see legality, never truth)" | done |
| 2 | enum confusion rung-blind | `suspect` → **closed** | "closed this session: per-rung verdict owned (mask pre-sampler vs no FSM/CFG at prompting rung)" | done |
| 3 | array length without the provider condition | `suspect` | "OPEN — next attack. Source: 'not all providers enforce them at the decoding level'" | **next** (`on_path: true`, `requires: null`) |
| 4 | nested-object depth, optional-field omission | `missing` | "OPEN — two source modes absent from v1 entirely" | after #3 (`on_path: true`, `requires: ["array-length seam"]`) |
| 5 | rows 1–3, 6 | `solid` | "banked, do not re-attack" | closed |
| 6 | row 4 concept-level | `solid` | "machine-side repaired; build-it-dependent grain out of scope per recalibration" | closed |

## What the session attacked, in the order it ran

1. **Row 4 closure (the resume point from 2026-11-09).** A **new** fresh-surface both-sides check at a fresh prefix, then the own-words restatement "flags × schema → mask + renormalise, ≠ the last-char rule". The concept-level model **closed**. One item still failed — and that one item tested **Build-It** grains (`part 1 execution-incomplete (garbled set, question-side not assertion-side); part 2 cue/unread-source`) that sit **outside the learner's declared read scope**; it is **banked out of scope** per the directive above and must **not** be re-issued. `miss_class: execution` was recorded with the item for the ledger; it is not a live gap.
2. **Row 5 — the catchability axis (the session's real content).** Two graded items, both `pass`, both on the learner's own articulation *before* any reveal: (a) predict where a schema-valid invented price (`299.99` against a $348 source) escapes the mask machine; (b) the same question re-posed through Instructor's validate-and-retry loop. The axis the learner now owns: **schema-side gates decide legality; nothing inside the loop holds the source document, so truth is undecidable there.** Their words are preserved verbatim on the wiki (below).
3. **The enum rung, per rung.** Seven graded items. Closed the rung-blindness: at the **masking** rung the legal enum set is a grammar fact and `"available"` is masked *before* the sampler; at the **prompting** rung the prompt only **lowers** its probability (lowered ≠ zero) and the component that would have made it zero — **FSM/CFG** — is absent, so the sampler can still emit it. Two slips on the *agent* and the *position* ("the sampler can still mask it to zero"; "it sits after the sampler") were repaired in-session, the second resolved against the learner's own clause "…hands the valid distribution to the sampler", ending in the sealed pipeline order and the no-op argument.
4. **Never reached:** the array-length seam, nested-object depth (4+ levels), optional-field omission, and the whole of graduation (entailment check → `naive-student` clone → battery remainder).

## Attempts (as carried, in recording order)

| # | Concept | Item | Verdict | Q type | Conf. | Miss class | Note |
|---|---|---|---|---|---|---|---|
| 1 | `structured-outputs-row4-closing` → `Constrained Decoding (parser-state masking)` | fresh-surface both-sides check | fail | micro-check | — | execution | "part 1 execution-incomplete (garbled set, question-side not assertion-side); part 2 cue/unread-source" — **BANKED OUT OF SCOPE** by learner directive (Build-It section unread); do not re-issue |
| 2 | `structured-outputs-catchability` → `Structured Outputs (JSON contract)` | predict: where does 299.99 slip through the mask machine | pass | micro-check | hunch | — | the learner's own articulation of the seam before any reveal |
| 3 | same | Instructor retry on a schema-valid hallucinated price | pass | micro-check | hunch | — | |
| 4 | `structured-outputs-enum-rung` → `Constrained Decoding (parser-state masking)` | masking-rung chain: enum consulted, `available` zeroed, mass handed to sampler | pass | micro-check | — | — | |
| 5 | same | `'the prompt lowers available's probability'` | fail | error-detect | — | structural | repaired via perturbation: lowered ≠ zero |
| 6 | same | prompting-rung number — answered with the masking-rung `0` | fail | micro-check | — | discrimination | R0 hint; rung fusion |
| 7 | same | absent component named: FSM/CFG (own v1 vocabulary) | pass | micro-check | — | — | |
| 8 | same | `'sampler can still mask it to zero'` — agent swap | fail | micro-check | — | execution | R0 hint |
| 9 | same | `'it sits after the sampler'` — position claim | fail | micro-check | — | execution | resolved via a within-session `source_clash` against the learner's own "hands the valid distribution to the sampler" |
| 10 | same | pipeline order raw → mask → sampler **+** the no-op reasoning | pass | micro-check | — | — | |

Recorded in `Core/Attempts.json` on the canonical rows (`Constrained Decoding (parser-state masking)` ×8, `Structured Outputs (JSON contract)` ×2). The handoff's three slugs are **facets of existing concepts**, not new concepts, so **no new Active Concepts rows were opened**.

## Mistakes (as carried — appended to `🧯 Mistakes.md`)

| Concept | error_type | `[miss: …]` | Evidence (verbatim) |
|---|---|---|---|
| `Constrained Decoding (parser-state masking)` | `deviation` | `structural` | "'the prompt lowers available's probability' — prompt mistaken for an enforcement mechanism; patched to lowered ≠ zero (source: 'Prompt-based approaches do not')" |
| same | `deviation` | `discrimination` | "prompting-rung answered with masking-rung value 0 — rung fusion; closed via R0 redirect + own-premise restate" |
| same | `application` | `execution` | "'it sits after the sampler' contradicted learner's own 'hands the valid distribution to the sampler'; resolved by no-op reasoning + corrected pipeline order" |

The row-4-closing fail opened **no** mistake row: it is the banked, out-of-scope Build-It item.

## Open attacks (dependency order, as carried — verbatim)

1. **A-next — array-length seam.** "is the failure a property of the mode or the provider choice? Learner must attach the enforcement condition to the mode." Source line it turns on: *"Schemas support minItems and maxItems but not all providers enforce them at the decoding level."*
2. **A+1 — nested-object depth (4+ levels) and optional-field omission.** "never listed by learner; missing rows, `full_teach` candidates after one perturbation probe."
3. **A+2 — graduation for the catchability axis.** "entailment check, naive-student clone, battery remainder (perturbation/sabotage on untouched dimensions)."

## Concepts Status After Session

| Concept | Previous Status | New Status | Mastery Type | Notes |
|---------|----------------|------------|--------------|-------|
| Structured Outputs (JSON contract) | developing | developing | concept (Feynman/clone owed) | 3 attempts total (1 in session 1 + **2 today, both pass**); `interval_index` **3**, `consecutive_correct` 3, `next_review` **2026-12-10** — scheduler-derived from two same-session passes; **advisory only**: the open seams (array-length, two unlisted modes) and the graduation battery, not the review clock, gate the resume; mastery 1.00 advisory (row-5 surface only) |
| Constrained Decoding (parser-state masking) | developing | developing | concept (Feynman/clone owed) | 21 attempts (13 in session 1 + **8 today, 3 pass / 5 fail**); `interval_index` **1**, `consecutive_wrong` 0, `next_review` **2026-11-17**; mastery 0.50 advisory; **row 4 CLOSED**, enum rung closed per rung, pipeline order sealed; the flags tuple still never run closed-book |
| JSON Schema Validation & Retry (Pydantic + Instructor) | developing | developing | concept (Feynman/clone owed) | no graded attempt yet (its next_review stays **2026-11-12**); the learner's v2 Instructor clause — the loop validates legality, not truth — is preserved verbatim on its page |

## Demonstrations of Understanding

- **Concept:** Structured outputs — catchability of failure modes (triage row 5)
  - **Confidence before evaluation:** `hunch` (both items — appropriately hedged after session 1's `sure`/9-of-11-fail calibration signal).
  - **Explanation:** "the machine knows the schema and legal set. what it would have to know is the exact value for the price key of this particular json object. it slips through since it is a valid entry(number)." / "what it validates against is whether this breaks the schema or not. the info needed to flag this output doesnt exist anywhere in that loop."
  - **Assistant evaluated:** **Pass** (both items). The impossibility is stated as an *information* claim — the loop holds the schema, not the document — which is exactly the entailment the graduation check will press.
  - **Mastery type:** pending_mastery (no Feynman/clone on this branch yet).
- **Concept:** Constrained decoding — which rung kills an out-of-enum value
  - **Confidence before evaluation:** not carried per item.
  - **Explanation:** "constrained decoding masks \"available\" and hence high probability for \"in_stock\", \"out_of_stock\", \"preorder\" to be sampled from. constrained decoding is the one that hands the valid distribution to the sampler" / "raw distibuton → constrained decoding(fsm/cfg) → sampler" / "its zeroing wouldnt be worth anything since the impure distribution has already been sampled from."
  - **Assistant evaluated:** **Pass** on the chain and the order after two in-session repairs (agent swap, position claim). The prompting-rung answer needed an R0 redirect: `lowered ≠ zero`.
  - **Mastery type:** pending_mastery.

## Open Questions

- [ ] **Array length (top of the queue):** does `minItems`/`maxItems` hold at decode time on the models in use? The source attaches the caveat to **providers**, not to the mode — so is the failure a property of the mode or of the provider choice? Never asked.
- [ ] **Nested-object depth** and **optional-field omission** — both listed by the source, neither listed by the learner; `full_teach` candidates after one perturbation probe each.
- [ ] **Graduation for the catchability axis:** the entailment check ("why must hallucinated values escape any schema-side gate?"), then the `naive-student` clone, then the battery remainder (perturbation/sabotage on untouched dimensions).
- [ ] Does the flag set get run closed-book as a whole tuple at one position? Every flag was pressed separately across two sessions; the tuple never was.
- [ ] Calibration: does `hunch` stay honest as difficulty rises? Session 2's confidences were hedged and both `hunch` items passed — a first data point in the other direction from session 1.

## Interleaving

Single-concept branch, second session: interleaved by question type only (fresh-surface check → predict probes → error-detect → micro-checks → order/argument). `Constrained Decoding` is again the retrieval target for the next review (2026-11-17); `Structured Outputs` rides to 2026-12-10 and `JSON Schema Validation & Retry` to 2026-11-12.

## Provenance

- **Tutor handoff:** inline (task payload), `mode: pause_handoff`, `partial: true` — `learner_model` (`v1` reference + 4 `v2_patches_this_session` verbatim), `triage[]` (6 rows with buckets + evidence), `open_attacks[]` (3, dependency order), `attempts[]` (10), `mistakes[]` (3), `exit_ticket: declined`. **Absent from disk:** `Lessons/Lesson — *Structured Outputs* — 2026-11-10.md`, `Core/Pending Ingest.json`, `Learning Records/Record — Structured Outputs — *.md`. Nothing was invented to fill those; the one on-disk lesson file is the 2026-11-09 artifact and its `Status:`/`Resume from:` **disagree** with this handoff (surfaced above, not merged — **resolved at the 2026-11-10 `/ingest`:** the Tutor's status update landed on that same file, so it now agrees with the handoff; see `## Handoff vs lesson file`).
- **Scout digests:** three are on disk for this slug and **all three are kept** (partial close; inside their 7-day TTL): `context-01a1bf90-…-structured-outputs.json` (2026-11-09), `context-01a1c444-…-structured-outputs.json` (fetched 2026-11-10T07:10Z) and **`context-01a1c4bb-…-structured-outputs.json`** (fetched 2026-11-10T12:25+03:00 — the newest, and the one this session and its graph extraction used; `roadmap_wiki_sha256` unchanged at `721ebb31…`).
- **Raw sources:** the 12 `raw/sources/2026-11-09 - structured-outputs - *.md` snapshots plus **a full 2026-11-10 re-fetch of the same 12** (different body hash for `rohit` / `openai` — a re-extraction, not a content drift: the Problem/Concept prose this session used is unchanged; the outer markdown scaffolding differs). Both snapshot sets are kept; the learner's declared read scope was the Problem + Concept sections of the 2026-11-10 `rohit` snapshot.
- **Attempts:** 10 recorded from the handoff in order (8 on `Constrained Decoding (parser-state masking)`, 2 on `Structured Outputs (JSON contract)`).
- **Dependency events:** none, so no `Dependency:` line was written.
