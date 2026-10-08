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

#### [ ] P0.2 — Deterministic claim extraction + exact-draft receipt binding
- **Goal:** the generator can no longer curate its own exam, and a receipt binds the exact emitted
  bytes, not a bag-of-words overlap.
- **Where:** `learning-pi/.pi/extensions/learning-gate/gate-core/primitives.ts` (+ `engine.ts` if the
  binding call sites need it), `contracts/learning-core.json`, `test/gate_test.mjs`,
  `test/golden/golden_test.mjs`.
- **Design:**
  - Extract load-bearing claims from the draft in **code** (numbers, formulas, definitions, causal
    assertions, URLs) instead of trusting `claims[]`. Compare the extracted set to the submitted
    `claims[]`; missing load-bearing claims become a withholding condition.
  - Bind a receipt to a hash of the exact emitted draft (canonicalised whitespace), replacing the
    `coverage ≥ 0.85` whole-draft and `bindingMatches` bag-of-words staleness checks.
  - Remove the "empty binding binds anything" back-compat branch.
  - Keep the change behind the revise door: update the contract first, add/replace tests in the same
    commit.
- **Verify:** `learn-check --no-load` green with updated contract + golden tests; new tests for
  (a) reordered/paraphrased emission no longer auto-binds, (b) an omitted load-bearing claim is
  caught, (c) an empty binding refuses.

#### [ ] P0.3 — Persist claim-level verification verdicts
- **Goal:** verification becomes auditable, not a prose tally.
- **Where:** gate writes (or `review-clerk` at close) → `Learning System/Reviews/Quality Gates/`;
  `learning-pi/.pi/skills/learning-review/SKILL.md`; possibly a small writer helper.
- **Design:** for every `fact_check` / `quiz_audit` / `grade_audit` the gate mints, persist a JSON
  artifact: `{gate, agent, model, at, draft_hash, verdict, claims:[{id, verdict, explanation,
  corrected_claim}], evidence:[...]}`. Today only `review`-gate JSONs are stored.
- **Verify:** a teach/review run produces verdict JSON on disk with the draft hash; `learn-check`
  unaffected.

#### [ ] P0.4 — Multi-dimensional mastery + independence gate
- **Goal:** mastery means demonstrated capability, not recent quiz correctness.
- **Where:** `learning-system/scripts/ops.py`, `scripts/learner_history.py`; then
  `Attempts.json` schema; skill text in `learning-pi/.pi/skills/learning-system/SKILL.md`.
- **Design:** per concept track six dimensions (recall, conceptual, procedural, transfer,
  independence, stability). Proposed shape: keep the existing `attempts[]` and add optional fields
  `confidence`, `hint_count`, `independent` (bool). `compute_mastery` becomes a multi-dimension
  report. `solid` requires recall + explain-back + independence + no open misconception + stability
  window. `consolidated` additionally requires a delayed transfer pass and a 90-day unaided pass.
  Grandfather existing concepts as *activity-history only, mastery unproven* — never retroactively
  grant `solid`.
- **Verify:** extend `ops_test.py`; `learn-check --with-sidecars` green; a migration dry-run on a
  copy of `Attempts.json`.

#### [ ] P0.5 — `/solo` AI-free flow
- **Goal:** measure what the learner can do without the AI; make it veto mastery.
- **Where:** new `.pi/prompts/solo.md` (`[[FLOW:solo]]`), `learning-gate` engine
  (`primitives.ts` flow enum + `engine.ts` branch: block `claims`/hint turns in solo), new skill text,
  `.pi/settings.json` only if needed, contract + tests.
- **Design:** a closed-book review drawn from the deterministic queue, `mode:solo`. The gate forbids
  `[[TURN:claims]]` in a solo flow, so the Tutor cannot hint or teach. The learner submits final
  answers in one message; grading is deterministic for MCQ and LLM-only for free recall. Solo result
  is the headline independence signal; a quiz-pass + solo-fail is a dependency alarm.
- **Verify:** gate test that a `claims` turn in solo is withheld; `learn-check` green; optional e2e
  solo scenario.

#### [ ] P0.6 — Knowledge-Wiki provenance + trust inversion
- **Goal:** stop contamination compounding; trust flows from sources.
- **Where:** `learning-system/Knowledge Wiki/*`, `Knowledge Wiki/AGENTS.md`,
  `learning-pi/.pi/skills/llm-wiki/SKILL.md`, `learning-system/AGENTS.md:230-235`.
- **Design:** every wiki claim/page carries `source`, `verification-status`
  (`verified | synthesis | learner-note | unverified`), `verified-by`, `date`. Flip the trust order:
  raw source > human-verified claim > AI synthesis (labeled) > learner note (labeled). Mark all
  existing pages `unverified-synthesis` until re-checked. Add a retraction/correction note convention
  and propagate to dependent pages.
- **Verify:** a provenance linter (new) reports 100% of pages carry a status; a sampled re-check of
  existing pages; wiki index consistent.

### P1 — High impact (after P0)

- P1.1 Feynman/teach-back mandatory for graduation; re-elicited in reviews (end the `feynman: none`
  pattern).
- P1.2 Deterministic MCQ grading in code; enforce a `q_type` enum (currently any string is accepted).
- P1.3 Prerequisite edges in live state; refuse downstream teaching over a `fuzzy` prerequisite.
- P1.4 Store per-attempt confidence; produce a calibration report.
- P1.5 Transfer dimension with periodic far-transfer items.
- P1.6 Withhold load-bearing unverified claims (stop rendering `⛔ UNVERIFIED` content as if fine).
- P1.7 Learner-authored wiki "my understanding" sections; Clerk verifies/indexes, does not ghost-write.
- P1.8 Seeded-error red-team harness (false-pass / false-block) as a standing e2e scenario.
- P1.9 Fading hint budgets tied to independence level.

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
