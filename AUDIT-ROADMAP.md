# Audit & Improvement Roadmap — learning system

> **Status:** living document. Updated as each stage lands.
> **Scope:** the integrated system formed by `learning-system` (durable state, wiki, philosophy,
> skills) and `learning-pi` (pi/control/runtime layer).
> **Audience:** future agents and humans working on either repo. Read this before proposing changes
> to teaching behavior, the verification gate, learner state, or the Knowledge Wiki.

---

## 0. How to use this document

- The **objective** is durable human learning and independent capability, not conversational quality.
  Every change is judged by: *does the learner become more capable and more independent?*
- Changes follow the **two-door rule** in `CONTRACT.md`: an *update door* never touches
  `contracts/` or `test/`; a *revise door* edits the contract first, in the same commit as the tests
  and the implementation.
- Work is staged **P0 → P3**. Do not start a lower stage before the higher stage is done and verified.
- Each landed stage records: what changed, which files, how it was verified, and the commit.
- **Do not commit learning state from `learning-pi`.** State lives in `learning-system`. The pi layer
  commits only its own resources. Runtime changes need a pi `/reload`.

---

## 0b. Cascade orchestration (Herdr)

This roadmap is executed by a **cascade of Herdr agents**, one per remaining stage, then a review
phase, then final end-to-end testing:

```
P1 → P2 → P3* → REVIEW → E2E
                ├── R-P0..R-P2 (Muse Spark, one per checkpoint, parallel)
                └── aggregate + implement fixes (default model)
```
`*` P3 is deferred (no-op forwarder) — see the P3 section.

- Full audit (canonical capture): [`docs/AUDIT-2026-10-08.md`](docs/AUDIT-2026-10-08.md).
- Orchestration + per-stage briefs: [`docs/roadmap/`](docs/roadmap/README.md).
- Each stage agent implements its stage, verifies (`learn-check --no-load --with-sidecars`), commits
  and pushes both repos, updates this file, then spawns the next stage with
  `bash docs/roadmap/spawn-stage.sh <next>`.
- `REVIEW` spawns one **Muse Spark** reviewer per checkpoint (`R-P0`..`R-P2`, review-only), waits for
  them, aggregates findings, implements the fixes (default model), and only then spawns `E2E`.
  See [`docs/roadmap/reviews/`](docs/roadmap/reviews/README.md).
- The final `E2E` agent runs full end-to-end verification and writes
  `docs/roadmap/E2E-REPORT.md`.

See `docs/roadmap/README.md` for the ground rules every agent follows.

## 1. Verdict (condensed from the deep audit)

The engineering is strong; the target was wrong. The system made excellent *conversations* but could
not prove the learner was becoming capable. Three structural defects:

1. **Interaction.** The end of each mini-checkpoint was the Tutor's clean statement. The learner
   accepted it. The learner did not form his own words → cognitive offloading.
2. **Computation.** The verification gate checked word overlap; the Tutor chose which claims to
   check. A wrong claim could stay outside the list. `fact-check PASS 4/4` meant *4 of 4 listed
   claims*, not *all load-bearing claims are true*.
3. **State.** `Attempts.json` stored dates and pass/fail only. No confidence, no help-used, no
   unaided-skill. Nothing ever tested the learner without AI, so independence could not be measured.

Additional findings:

- The Knowledge Wiki (AI-synthesized) is declared **Trusted**; raw sources (primary evidence) are
  declared **"Verify before acting on"**. Trust flows the wrong way (`learning-system/AGENTS.md:230-235`).
- LLM verification is not independent verification: the same-process verifier accepts a claim by the
  regex `"verdict":"PASS"`; the judge only sees what the verifier says; the Open WebUI path has no
  model separation at all.
- Mastery is an advisory recency-weighted quiz score (`ops.py:239-252`). All live Concepts stay
  `developing`; `Consolidated: 0`.
- "Just tell me" was always honored with no record and no compensation.

### What is genuinely good (protect it)

`ops.py` deterministic SRS + queue; retrieval-first reviews; the hint protocol (method only, hand the
arithmetic back); diagnose-first repair with **detectors**; the Mistakes ledger with self-attribution;
raw-source immutability + hashing + contradiction surfacing; the `CONTRACT.md` invariant↔test pattern.

---

## 2. Current objective function

| Optimized for | Should optimize for |
|---|---|
| Conversation integrity (every turn has a receipt) | Learner capability (every mastery claim is evidence-backed) |
| State bookkeeping correctness | Knowledge truth + provenance |
| Learner satisfaction ("just tell me" always wins) | Durable learning (struggle is protected) |
| Curriculum throughput (checkpoints sealed) | Transfer + retention + independence |

**Tradeoff to keep in view:** near-zero hallucination and maximal learner struggle genuinely
conflict. Resolve by splitting the layers — the **epistemic layer** (what the system asserts as true)
must be strictly verified and provenance-marked; the **pedagogical layer** (what the learner is asked
to do) must be allowed to be hard. Verification must never smooth the struggle; struggle must never
excuse an unverified claim.

---

## 3. Roadmap

Legend: `[x]` done · `[~]` in progress · `[ ]` pending.
Each item lists **Goal · Where · Design · Verify**.

### P0 — Critical

> **P0 complete (2026-10-08).** All six critical items landed: learner-authored consolidation,
> deterministic hard-fact completeness + tail-bound binding, always-on claim-level verdict ledger,
> per-dimension mastery + independence gate, the `/solo` AI-free flow, and wiki provenance + trust
> inversion. Each was verified (`learn-check`) and committed. P1 can begin.

#### [x] P0.1 — Learner-authored consolidation + dependency-event logging
- **Goal:** the learner states each idea in his own words; the Tutor checks it and adds only what is
  missing. "Just tell me" stays honored but is logged and still closes with one minimal generation.
- **Where:** `learning-pi/.pi/skills/learning-teach/SKILL.md`, `.pi/APPEND_SYSTEM.md`,
  `.pi/prompts/{teach,lesson,continue}.md`, `.pi/agents/clerk.md`.
- **Design:** ladder is now **Elicit → Attempt → State (learner) → Check-and-extend**. Rung 3 prompt
  is `[[TURN:none]]` when procedural, `[[TURN:claims]]` when it carries framing. Rung 4 labels each
  addition (`Source framing:` / `External angle:` / `⚠️ Sources disagree`) and never rewrites the
  learner's words. Dependency events `{kind, mini, date}` with `kind ∈ {just_tell_me, told_repair,
  declined_generation}` written to the session note, `Pending Ingest.json`, and the Learning Record
  `Dependency:` line.
- **Verify:** `scripts/learn-check --no-load` → OK (154 gate assertions; 41/41 contract invariants).
  Consistency grep clean.
- **No gate code changed** — the new turns fit existing `[[TURN:none]]` / `[[TURN:claims]]` semantics.
- **Commit:** _see git history_ (`teach: learner-authored consolidation + dependency logging`).

#### [x] P0.2 — Deterministic claim extraction + exact-draft receipt binding
- **Goal:** the generator can no longer curate its own exam, and a receipt binds the exact emitted
  draft, not a loose overlap.
- **Where:** `learning-pi/.pi/extensions/learning-gate/gate-core/primitives.ts` + `engine.ts`,
  `contracts/learning-core.json`, `CONTRACT.md`, `test/gate_test.mjs`,
  `.pi/agents/fact-check.md`, `.pi/skills/learning-teach/SKILL.md`.
- **Design (as landed):**
  - Deterministic hard-fact extraction in code (`extractHardFacts`): URLs, LaTeX/math expressions,
    scientific notation, decimals, percentages, and 3+ digit integers (calendar years excluded).
    A hard fact present in the draft but absent from the submitted `claims[]` withholds the turn as
    `CLAIMS_INCOMPLETE`, so the Tutor must place every number/formula/URL before the verifier.
  - Tightened draft binding (`contentMatches`): coverage raised 0.85 → 0.95, and the old 1.4× length
    ratio replaced by a bounded unverified tail (`extraTokenCount ≤ 12`). Reordering/punctuation are
    still tolerated; appended never-verified prose is not.
  - `fact-check.md` now requires the verifier to independently enumerate the draft's load-bearing
    claims, not trust the submitted list.
- **Deviation from the draft plan (recorded):** kept a *tight fuzzy* bind rather than a byte hash.
  The gate's own history is a catalogue of re-emission deadlocks; a byte hash would withhold any
  tag-strip/punctuation drift and is high-risk in a multi-agent flow. The tail bound removes the
  actual hazard (unverified appended content) without that fragility. Revisit only with e2e evidence.
- **Empty-binding back-compat:** the wrong-shape-envelope case already refuses (`G-receipt-shape-binds`);
  the remaining envelope-less async fallback is a legitimate uncorrelated-notification path, kept.
- **Verify:** `learn-check --no-load` → OK; new invariants `G-claims-complete` (2 tests) and
  `G-draft-tail-bound` (1 test) covered. Tests: unlisted hard fact withheld; listed hard facts
  allowed; unverified tail withheld.
- **Commit:** _see git history_ (`gate: extract hard facts and bound the unverified draft tail (P0.2)`).

#### [x] P0.3 — Persist claim-level verification verdicts
- **Goal:** verification becomes auditable, not a prose tally.
- **Where (as landed):** `gate-core/ledger.ts` (existing), `gate-core/judge/types.ts`,
  `gate-core/primitives.ts`, `gate-core/engine.ts`, `pi-adapter/index.ts`,
  `test/gate_test.mjs`.
- **Design:** the receipt ledger now records, for every verifier receipt, the claim-level verdicts
  parsed from the verifier's own JSON (`claims:[{id, verdict, explanation, correctedClaim}]`) and an
  FNV-1a fingerprint of the exact bound draft (`envelopeHash`). It is **always on** (previously built
  only when a judge was configured), so the judge-less legacy path is auditable too.
- **Deviation from the draft plan (recorded):** the ledger lives under the pi agent dir
  (`~/.pi/agent/learning-gate/receipts.ndjson`, override `LEARNING_GATE_LEDGER_DIR`) rather than in
  the state repo's `Reviews/Quality Gates/`. The extension must not become a state writer (the audit
  flagged state writes outside the flows); the home ledger is the sanctioned extension write path and
  is the same provenance source the weekly audit already reads. An in-repo mirror is deferred.
- **Verify:** `learn-check --no-load` → OK; new assertion `ledger records claim-level verdicts with a
  draft hash` reads the NDJSON and confirms a `fact_check` line with `claims[]` + `envelopeHash`.
- **Commit:** _see git history_ (`gate: always-on claim-level receipt ledger (P0.3)`).

#### [x] P0.4 — Multi-dimensional mastery + independence gate
- **Goal:** mastery means demonstrated capability, not recent quiz correctness.
- **Where (as landed):** `learning-system/scripts/ops.py`, `scripts/learner_history.py`,
  `scripts/ops_test.py`; `learning-pi/.pi/skills/learning-system/SKILL.md`,
  `.pi/skills/learning-teach/SKILL.md`, `.pi/agents/review-clerk.md`.
- **Design (as landed, additive):**
  - `compute_dimensions(entry)` reports six dimensions 0–3: recall, conceptual (Feynman),
    procedural, transfer, independence (last `mode:"solo"` attempt), stability (interval_index).
    A dimension with no evidencing attempt is `None` (unknown), never a false 0.
  - `ops.py attempt` gains optional `--confidence`, `--hints N`, `--mode normal|solo`; the fields are
    recorded only when supplied, so existing attempts and callers are unchanged.
  - `ops.py mastery [TRACK] [--json]` prints the scalar plus all six dimensions.
  - Independence gate: `independence_ok(entry)` is false only when a **failed solo** attempt is on
    record. `learner_history.tag()` cannot return `solid` when it is false. Absence of solo evidence
    is unknown → existing concepts are grandfathered (no mass demotion), and the gate becomes real
    once `/solo` (P0.5) produces data.
- **Deferred:** the full graduation rework (consolidated + 90-day unaided pass) waits on P0.5's solo
  data and P1.2's `q_type` enum; the dimension model now exists to build it on.
- **Verify:** `ops_test.py` 24 tests OK (4 new: dimension split, unknown≠0, independence gate,
  optional-field recording); `learn-check --no-load --with-sidecars` → OK.
  Manual: `ops.py mastery` prints dimensions; `--json` dumps them; `tag()` returns solid for a
  passing solo and neutral for a failed solo behind later passes.
- **Commits:** _see git history_ (`ops: per-dimension mastery + independence gate (P0.4)` in
  learning-system; `skills: document per-dimension mastery (P0.4)` in learning-pi).

#### [x] P0.5 — `/solo` AI-free flow
- **Goal:** measure what the learner can do without the AI; make it veto mastery.
- **Where (as landed):** new `.pi/prompts/solo.md` (`[[FLOW:solo]]`); `gate-core/primitives.ts`
  (flow enum + `FLOW_TAG_RE`); `gate-core/engine.ts` (solo blocks + reuse of the review gates);
  `.pi/agents/review-clerk.md` (`mode:"solo"` pass-through); `.pi/skills/learning-system/SKILL.md`,
  `.pi/APPEND_SYSTEM.md`, `README.md`, `FIELD-GUIDE.md`; `test/contract/check_learning_layer.py`;
  `contracts/learning-core.json` + `CONTRACT.md`; `test/gate_test.mjs`.
- **Design:** `/solo` is a review flow with the AI removed. `[[FLOW:solo]]`; the gate withholds
  `[[TURN:claims]]` (`SOLO_NO_TEACHING`) and `[[TURN:viz]]` (`SOLO_NO_AIDS`) by construction, so the
  Tutor cannot hint or teach. The learner answers one closed-book batch; `grade-audit` grades it;
  `review-clerk` records every attempt with `--mode solo` (feeding P0.4's independence gate); the
  close reuses the `review-session-audit`. `review-scout` supplies the deterministic queue.
- **Verify:** `learn-check --no-load` → OK; invariant `G-solo-no-teaching` covered by 4 assertions
  (teaching withheld, viz withheld, first quiz needs review-scout, closed-book batch allowed); solo.md
  carries `[[FLOW:solo]]`.
- **Commit:** _see git history_ (`gate: add the AI-free solo flow (P0.5)`).

#### [x] P0.6 — Knowledge-Wiki provenance + trust inversion
- **Goal:** stop contamination compounding; trust flows from sources.
- **Where (as landed):** `learning-system/scripts/wiki_provenance.py` (new),
  `Knowledge Wiki/AGENTS.md`, `AGENTS.md`, `Skills/llm-wiki/SKILL.md`, all 220
  `Knowledge Wiki/wiki/*.md`; `learning-pi/.pi/skills/llm-wiki/SKILL.md`.
- **Design (as landed):** every page carries a marker
  `<!-- provenance: status=<verified|synthesis|learner-note|unverified> | source=<ref> | verified-by=<who> | date=YYYY-MM-DD -->`.
  An **unstamped page counts as `unverified`**. All 220 existing pages were stamped
  `status=unverified` (source `legacy`) so nothing is silently trusted; a page is upgraded to
  `verified` only when a verifier checks it against the cited source. The trust order in `AGENTS.md`
  is flipped to **raw source > verified claim > labelled synthesis > learner note**; the
  retraction/correction convention (mark dependents unverified, re-check) is documented in
  `Knowledge Wiki/AGENTS.md`.
- **Verify:** `python3 scripts/wiki_provenance.py --check` → exit 0 (220/220 carry a marker, 0
  missing). Index/files unchanged (the marker is a comment line, no filename change).
- **Note:** the OpenWebUI `Skills/llm-wiki` copy changed too, so `audit_openwebui.py` reports drift
  until the installer re-runs. In-repo wiki pages are the durable artifact; the OpenWebUI path is
  frozen per the earlier scope decision.
- **Commit:** _see git history_ (`wiki: provenance markers + trust inversion (P0.6)` in
  learning-system; `skills: require wiki provenance (P0.6)` in learning-pi).

### P1 — High impact (after P0)

> **P1 complete (2026-10-08).** All nine items landed and were verified
> (`learn-check --no-load --with-sidecars` → OK). Two honest deferrals: the full
> `consolidated` graduation (P1.5) still has no graduation flow to gate, so
> `transfer_ok`/`independence_ok` are wired as the gate it will use; P1.9's
> hint-fade is documented behavior (no deterministic check — the `--hints`
> telemetry makes it measurable later).

#### [x] P1.1 — Feynman/teach-back mandatory for graduation
- **What:** `concept`/`design` items must pass a Feynman explain-back to be `solid`; reviews now
  elicit it as a required graded beat and carry `feynman_pass`/`feynman_fail` in the close envelope;
  `review-clerk` records it (`--qtype explain-back`). `memory`/`procedure` exempt.
- **Where:** `learner_history.py` (already gated — confirmed), `ops_test.py`, `.pi/skills/learning-system/SKILL.md`,
  `.pi/agents/review-clerk.md`, `.pi/prompts/review.md`, `.pi/skills/learning-teach/SKILL.md`.
- **Verified:** `ops_test.py` new `TestLearnerHistoryFeynmanGate` (concept cannot be solid without a
  Feynman pass; memory exempt); `learn-check` OK.
- **Commits:** `829f5b9` (learning-system), `957d735` (learning-pi).

#### [x] P1.2 — Deterministic MCQ grading + a `q_type` enum
- **What:** `ops.py attempt --qtype` validates a canonical enum (legacy aliases normalize; unknown
  rejected); `ops.py grade-mcq --key A,B,C --answers A,C,C` returns per-item pass/fail with no LLM.
  The review flow grades MCQs mechanically where the key is known and sends only free-recall to
  `grade-audit`.
- **Where:** `ops.py`, `ops_test.py`, `.pi/skills/learning-system/SKILL.md`, `.pi/agents/review-clerk.md`,
  `.pi/prompts/review.md`, `.pi/skills/learning-teach/SKILL.md`.
- **Verified:** `ops_test.py` `TestQTypeEnum` (unknown rejected, aliases normalized) + `TestGradeMcq`
  (mixed correct/incorrect letters, empty answer, length mismatch); `learn-check` OK.
- **Commits:** `829f5b9`, `957d735`.

#### [x] P1.3 — Prerequisite edges in live state
- **What:** optional `prereqs:[names]` on `Attempts.json` entries; `ops.py attempt --prereq NAME`;
  `ops.py prereqs "<concept>" [--set ...]` reports each direct prereq's live state with
  `blocks=true` when a direct prereq is `fuzzy`/open-mistake. Teach/review flows refuse to advance
  over a blocking prereq; missing evidence is `unknown` (never blocks). `learner_history.py` surfaces
  the prereq state in its table.
- **Where:** `ops.py`, `ops_test.py`, `learner_history.py`, `Learning System/Core/Learner History.md`,
  `.pi/skills/learning-teach/SKILL.md`, `.pi/skills/learning-system/SKILL.md`, `.pi/APPEND_SYSTEM.md`.
- **Verified:** `ops_test.py` `TestPrereqs` (fuzzy blocks, open mistake blocks, unknown does not
  block, `--set` persists); `learn-check` OK.
- **Commits:** `829f5b9`, `308cd48`, `957d735`.

#### [x] P1.4 — Confidence calibration
- **What:** flows record `--confidence` on every graded attempt; `ops.py calibration [TRACK]` reports
  `sure` vs `hunch` accuracy and an over/under-confidence flag; per-concept `calibration` is surfaced
  in `ops.py mastery --json`.
- **Where:** `ops.py`, `ops_test.py`, `.pi/skills/learning-teach/SKILL.md`, `.pi/agents/review-clerk.md`,
  `.pi/skills/learning-system/SKILL.md`, `.pi/APPEND_SYSTEM.md`.
- **Verified:** `ops_test.py` `TestCalibration` with a synthetic overconfident history (flags
  `overconfident`); `learn-check` OK.
- **Commits:** `829f5b9`, `957d735`.

#### [x] P1.5 — Transfer beyond near-isomorphic
- **What:** `q_type` values `transfer-near`/`transfer-far` feed the transfer dimension; the review
  flow includes a transfer item for `concept`/`design` on a cadence; `transfer_ok()` requires a passed
  far-transfer for `consolidated` graduation (wired, pending a graduation flow). `ops.py mastery`
  surfaces `transfer_ok`.
- **Where:** `ops.py`, `ops_test.py`, `.pi/skills/learning-system/SKILL.md`, `.pi/skills/learning-teach/SKILL.md`.
- **Verified:** `ops_test.py` `TestTransferDimension` (far-transfer pass → transfer 3 + `transfer_ok`;
  fail → 0); `learn-check` OK.
- **Deferred:** the graduation flow itself (consolidated + 90-day unaided check) still does not exist.
- **Commits:** `829f5b9`, `957d735`.

#### [x] P1.6 — Withhold unverified load-bearing claims
- **What:** at the retry cap, a `claims` turn whose draft contains hard facts (`extractHardFacts`) is
  **withheld outright** — banner only, no content — instead of delivered as `⛔ UNVERIFIED`.
  Non-hard-fact prose still degrades gracefully; `G-retry-cap` semantics unchanged for other turns.
- **Where:** `gate-core/engine.ts` (legacy + judge paths), `contracts/learning-core.json` + `CONTRACT.md`
  (new invariant `G-hard-fact-withhold`), `test/gate_test.mjs`, `test/golden/golden_test.mjs`.
- **Verified:** gate test `retry cap withholds a hard-fact claims turn` (banner, no content) and
  `retry cap still delivers non-hard-fact prose`; `learn-check` OK.
- **Commits:** `e297dd6`, `68a70ad`.

#### [x] P1.7 — Learner-authored wiki ("my understanding")
- **What:** concept pages carry a `## My understanding` section in the learner's own words, captured
  at consolidate, preserved/appended (never rewritten) by the Clerk, and marked `status=learner-note`.
- **Where:** `.pi/skills/llm-wiki/SKILL.md`, `.pi/agents/clerk.md`, `Knowledge Wiki/AGENTS.md`,
  `.pi/skills/learning-teach/SKILL.md`, `.pi/APPEND_SYSTEM.md`.
- **Verified:** doc/behavior; sample page shape in `llm-wiki`; `learn-check` OK.
- **Commits:** `2ed8d8e` (learning-system), `957d735`.

#### [x] P1.8 — Seeded-error red-team harness
- **What:** an offline harness injects known-wrong load-bearing content into sandboxed gate flows and
  asserts the gate catches it (`CLAIMS_INCOMPLETE` or `FACT_CHECK_ISSUES`), with clean controls for
  false-blocks. Reports caught/total; wired into `learn-check`.
- **Where:** `test/redteam/redteam_test.mjs` (new), `scripts/learn-check`.
- **Verified:** harness runs and reports `caught 5/5 seeded errors; clean controls 2/2`; `learn-check` OK.
- **Commit:** `c1eac94`.

#### [x] P1.9 — Fading hint budgets
- **What:** the teaching skill reads a concept's `independence`/`stability` dimensions and shrinks the
  guiding-question budget 2 → 1 → 0 as they rise; `--hints N` records the effect.
- **Where:** `.pi/skills/learning-teach/SKILL.md`, `.pi/APPEND_SYSTEM.md`.
- **Verified:** doc/behavior (no deterministic check; `--hints` telemetry makes it measurable later).
- **Commit:** `957d735`.

### P2 — Valuable

- P2.1 Promote `audit_state.py` to blocking on errors (split content gate vs state gate).
- P2.2 Remove the out-of-scope ISSUES→PASS_WITH_FLAGS demotion regex (or whitelist only bookkeeping
  paths).
- P2.3 Enforce Scout TTL — re-scout required, not advisory.
- P2.4 Declare pi canonical; freeze or remove the OpenWebUI pedagogy path to kill skill drift.
  **(Currently open: `learning-system/Skills/learning-teach/SKILL.md` still holds the pre-P0.1 text.)**
- P2.5 Replace `.tmp/gen_review_*.py` state surgery with a first-class `ops.py amend` + audit trail.
- P2.6 Resolve prompt contradictions (Tutor-vs-Clerk Active Concepts writes; one-dispatch-per-turn;
  claims inference) in one direction and delete the stale copies.
- P2.7 Light procedural interleaving in practice sets.
- P2.8 Misconception→prerequisite links in the Mistakes ledger.

### P3 — Nice to have

> **Deferred by user (2026-10-08).** No P3 work performed; resume later. The cascade's P3 stage is a
> no-op forwarder to the review phase. P3.1–P3.4 below are not started.

- P3.1 Repurpose the judge for disputed-claim escalation only.
- P3.2 Instrument the `viz` subsystem's learning ROI, or demote it.
- P3.3 Learning-analytics dashboard (independence trend, hint debt, retention curves).
- P3.4 Learner challenge/dispute workflow for suspect wiki claims.

---

## 4. KEEP / CHANGE / REMOVE / ADD / RETHINK (condensed)

| Component | Action | Reason |
|---|---|---|
| `ops.py` SRS + queue | **KEEP** | Deterministic arithmetic belongs in code |
| `CONTRACT.md` invariant↔test pattern | **KEEP** | The model for every new guarantee |
| Elicit→Attempt→State→Check ladder | **CHANGE** (P0.1 done) | Shift generation to the learner |
| `fact-check` claim list | **CHANGE** (P0.2) | Self-selection is the top hallucination path |
| Receipt binding | **CHANGE** (P0.2) | Exact-draft hash, not token overlap |
| Mastery model | **RETHINK** (P0.4) | Multi-dimensional + independence |
| AI-free assessment | **ADD** (P0.5) | The measurement that decides A vs B |
| Wiki trust order | **CHANGE** (P0.6) | Source > verified > synthesis |
| "Just tell me" policy | **CHANGE** (P0.1 done) | Honored but logged + one closing generation |
| `⛔ UNVERIFIED` renders content | **CHANGE** (P1.6) | Withhold load-bearing claims |
| Out-of-scope demotion regex | **REMOVE** (P2.2) | Silently swallows real issues |
| Empty-binding back-compat | **REMOVE** (P0.2) | Receipts must bind something real |
| Feynman requirement | **CHANGE** (P1.1) | Advancement without explain-back |
| grade-audit for MCQ | **CHANGE** (P1.2) | Code grades mechanical answers |
| Prerequisite graph | **ADD** (P1.3) | Don't teach over a broken foundation |
| Learner-authored wiki | **ADD** (P1.7) | The learner builds durable understanding |
| Duplicate skill copies | **RETHINK** (P2.4) | Two divergent pedagogies drift |
| Bookkeeping triple-audit | **RETHINK** (P2.1) | Over-verifies state, under-verifies truth |

---

## 5. Measurement plan (how we will know it worked)

- **Factual reliability:** hallucination rate on sampled load-bearing claims (<1% target);
  false-verification rate (seeded-error red team); source-grounding rate (verdicts with a quote).
- **Learning:** delayed cold retention at 7/30/90 days; blind-scored transfer; misconception
  persistence (→ 0 after graduation).
- **Cognitive health:** AI-free performance must rise; hint debt per problem must fall;
  "just tell me" frequency must fall; learner-words share of each session must rise.
- **System quality:** gate false-pass/false-block; state integrity (`audit_state.py` errors → 0);
  verification coverage (claim-level receipts → 100%).

---

## 6. Division of labor (north star)

- **Learner does:** predict, attempt, compute, recall, explain, consolidate, diagnose own errors,
  write concept notes, check the AI against sources.
- **AI does:** gather/hash sources, surface contradictions, schedule, sequence prerequisites, generate
  fresh practice, grade mechanical work, flag breaks, provide detectors, bookkeep.
- **AI never without the learner:** produce the learner's explanation; write the learner's durable
  understanding; declare mastery; silently resolve a contradiction.
- **AI sometimes refuses:** answer immediately (hint budget spent); teach over a fuzzy prerequisite;
  assert a load-bearing claim with no source; declare mastery without an independence check.

---

## 7. Frontier (out of this roadmap)

Post-P0 directions not committed: independent (non-LLM) verification tier for high-stakes claims;
spaced interleaving of related procedures in practice sets; a second, differently-trained model for
adversarial verification (still not a truth oracle); a learner-facing uncertainty/provenance view.
