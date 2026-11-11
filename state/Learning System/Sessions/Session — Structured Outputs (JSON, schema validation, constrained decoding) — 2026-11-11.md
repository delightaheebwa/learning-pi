# Session — Structured Outputs (JSON, schema validation, constrained decoding) — 2026-11-11

- **Type:** Resume interrogation (session 3; resumed from the 2026-11-10 pause at the array-length seam, top of the queue)
- **Scope invariant (learner directive, 2026-11-10, still in force):** attacks target ONLY the Problem + Concept sections of the raw source; Build-It code and row 7 stay banked out of scope.
- **Difficulty signal (recorded 2026-11-09, repeated 2026-11-10, repeated again this session):** keep each new item to ~1 source return; the masking/ownership regime was again over the edge for self-repair — all three repairs needed a just-tell-me patch after the hint ladder was exhausted.
- **Exit ticket:** **declined** (third consecutive decline; offered once, not pressed).

## What was attacked (single seam, four parts, all CLOSED by end of session)

**The array-length seam** — the learner's v1 lump ("array length [?], too long or too small array length") dropped the resolving clause: *"Schemas support minItems and maxItems, but not all providers enforce them at the decoding level."*

1. **Where decode-level enforcement acts** — predict: enforcing provider → "error message" ✗ (validate-and-retry rung attached to the wrong tier); non-enforcing provider → "the invalid array" ✓. Press: the array dies at the **constrained-decoding arrow** ✓ (`sure`).
2. **What remains for downstream checks on the enforcing path** — three failed candidates ("checks for hallucinated values" — inverting their own November legality-vs-truth closure; "the big picture"; "not sure"), then a just-tell-me patch: the post-sampler legality validator is a **no-op** on that path; value truth is checked, if at all, **outside the output path**. Fresh surface (invoice `"total": 299.99` vs $348) passed after a detector-placement self-clash: *"the ground truth comparison will have to sit after the post sampler validator step."* **CLOSED.**
3. **What the enforcing mask must carry** — counterexample trap: flags × schema identical at the positions after items 1/2/3, yet `]` legality differs. Five failed candidates ("tracking the flags and the schema" → "tracking `]`" → "`, vs ]`"), then a just-tell-me patch: the mask carries a **counter** — `]` legal iff `count ≥ minItems`, `,` legal only while `count < maxItems` — "a number, not a boolean." Fresh surface in the maxItems direction: *"the counter says 2 which means , is invalid while ] is valid"* ✓ (`sure` earned). **CLOSED.**
4. **Whose property the failure is** — predict: "the violation is a property of constrained decoding" ✗ (both apps run the same rung — eliminated; OpenAI base-vs-fine-tuned path + Anthropic `minItems` 0/1 handed as source returns); "it is the provider's property" ✗ (owner correct, why-clause owed — graded fail). Transfer press: "null and void" / "it doesnt land, still no-op" on the non-enforcing path ✗✗ (contradicting their own "the array is in an invalid state" one sentence apart) → patch: **the no-op is a property of the PATH, not of the validator** (mask guarantees → validator idle; mask absent → the validator is the **only catcher** of length legality). Closed on the two-blank fill: *"enforced path, non-enforced"* ✓. **CLOSED.**

## Learner model — patches this session (verbatim)

- (repair 1) *"the ground truth comparison will have to sit after the post sampler validator step"* — on the enforcing path the validator is a no-op for legality; truth-checking lives outside the pipe.
- (repair 2) *"the counter says 2 which means , is invalid while ] is valid"* — the mask carries a counter of items emitted in this array; numeric state, not a boolean flag.
- (repair 3) *"enforced path, non-enforced"* (into "the validator is idle on the ___ path and catching on the ___ path") — the no-op is path-dependent, not a property of the validator.
- Ownership: *"it is the provider's property"* — whether the length keywords become decode-time grammar state is decided by the provider.

Evolution scar: v1 lump ("array length [?]…" with no owner) → v2 catchability axis (2026-11-10) → v3 (2026-11-11): pipeline = raw distribution → constrained decoding (flags **+ counter**) → sampler; validator's role flips by path; the provider's compile coverage decides whether the mask exists; truth is nobody's job inside the pipe.

## Attempts (24 graded items across 19 learner replies; 8 pass / 16 fail; full metadata in the handoff)

Passes (8): turn-1 part 2 (non-enforcing → invalid array); arrow press (`sure`); clash resolution — "the validator checks if it breaks the schema" (`hunch`); detector placement — "after the post sampler validator step"; counterexample column fill (no/no/yes); maxItems counter check (`sure`); part-1 invalid-state (`sure`); two-blank path fill (`sure`). The owner answer "it is the provider's property" is NOT a pass — owner correct but the why-clause was owed, and the verifier graded it fail.

Fails (16): "error message" on the enforcing provider; circular "output the user gets"; "not sure" (cue); "validator checks hallucinated values"; "big picture"; "nowhere is it caught" (`sure` on a half-answered check — **illusion-of-competence signal**); "detector at constrained decoding"; "flags × schema"; "tracking `]`"; "`, vs ]`" (counter gap); "property of constrained decoding"; "provider's property" (owner right, why-clause owed); "null and void"; "it doesnt land, still no-op" (non-enforcing path); "checks whatever else… enforced upstream" (inverted); deleted-validator scenario (idle/catcher swap).

All fails repaired in-session; the three repairs closed on fresh surfaces in the learner's own words.

## Mistakes logged (all `review` status after in-session repair; transfer-check at next `/review`)

1. Decode enforcement → "error message" (deviation / discrimination) — repaired.
2. "Validator simply checking for hallucinated values" (deviation / discrimination — inverted own legality-vs-truth closure) — repaired.
3. Detector placed at the mask (application / discrimination — mask never sees ground truth) — repaired.
4. Flags × schema suffices for length; "tracking `]`"; "`, vs ]`" (structural / discrimination-then-execution — no counter in the state) — repaired with the counter patch.
5. "Violation is a property of constrained decoding" (deviation / discrimination — rung attached instead of provider) — repaired.
6. "Null and void" / "it doesnt land, still no-op" on the non-enforcing path (deviation / discrimination — path-dependence collapsed) — repaired, closed on the two-blank fill.
7. `sure` on the half-answered invoice check (metacognitive — illusion of competence) — noted; both subsequent `sure` tags were earned.

## Concepts Status After Session

| Concept | Previous Status | New Status | Notes |
|---------|----------------|------------|-------|
| Structured Outputs (JSON contract) | developing | developing | **row 5 array-length seam CLOSED** (ownership = provider; validator path-dependent; truth outside the pipe); attempts now ~13 total (2 in s2 + 11 this session); mastery advisory; graduation battery still owed (sabotage untouched) |
| Constrained Decoding (parser-state masking) | developing | developing | **counter state added to the flag model** ("a number, not a boolean") — flags × schema model extended, fresh-surface pass in the maxItems direction; the flags tuple still never run closed-book as a whole |
| JSON Schema Validation & Retry (Pydantic + Instructor) | developing | developing | no graded attempt of its own yet; this session gave its **path-dependence half**: idle where the mask enforces, the only catcher (incl. length legality) where it doesn't — learner's own words |

## Open Questions (next session queue)

- [ ] **A+1n — nested-object depth (4+ levels):** one perturbation probe; `full_teach` candidate on the stack (per-frame required-sets) if the one-flag-set model collapses.
- [ ] **A+1o — optional-field omission:** legal-by-default; remedy is authoring (`required` + explicit `null`), not enforcement.
- [ ] **Graduation:** entailment check → naive-student clone on the v3 pipeline model → battery remainder (sabotage untouched).
- [ ] Exit ticket has now been declined three times — offer once at next pause, do not press.
- [ ] Does `hunch` stay honest as difficulty rises? This session: `hunch` items went 3 pass / 4 fail — mixed, unlike session 2's 2/2.

## Interleaving

Single-concept branch, third session; interleaved by question type only (predict → mechanism press → source clash → fresh-surface checks → two-blank fill). Retrieval targets for upcoming reviews unchanged: `Constrained Decoding` 2026-11-17, `JSON Schema Validation & Retry` 2026-11-12, `Structured Outputs` 2026-12-10 (advisory).

## Provenance

- **Tutor handoff:** `Core/Pending Ingest.json` (`mode: pause_handoff`, `partial: true`) — learner model v3 patches verbatim, open attacks A+1n/A+1o/graduation, 24 attempts (8 pass / 16 fail), 7 mistakes, 3 dependency events (just_tell_me ×3), exit ticket declined.
- **Scout digest:** `context-01a1c95f-…-structured-outputs.json` (2026-11-11 resume-refresh; all 12 Further-Reading URLs re-fetched live, no upstream drift).
- **Sources:** `raw/sources/2026-11-11 - structured-outputs - *.md` snapshot set (12 files; rohit body hash `34a90614…`).
- **Wiki pages:** unchanged this session (three pages live); `/ingest` will sync the wiki rows with the v3 patches and the closed seam.

## Ingest (Clerk, 2026-11-11) — durable writes from this `/pause` handoff

- **Wiki (3 pages enriched; learner words verbatim, v1 → v2 → v3 in order, nothing merged):** `Structured Outputs (JSON contract)` (v3 block + second breaking case + `### Session 3 attack chain` + array length marked CLOSED), `Constrained Decoding (parser-state masking)` (v3 counter block + `## Array length: why flags × schema is not enough`), `JSON Schema Validation & Retry (Pydantic + Instructor)` (v3 path-dependence block + `## Where the validator's verdict lands — path-dependent`). `index.md` lines updated; see `Knowledge Wiki/log.md` for the full record.
- **Attempts:** the handoff's **24 graded items logged in order** via `ops.py attempt` with their `qtype` (`micro-check`) and `confidence` — 8 pass / 16 fail. Row ledger after: `Structured Outputs (JSON contract)` 21 items, `interval_index` 1, next **2026-11-18**; `Constrained Decoding (parser-state masking)` 27 items, `interval_index` 2, next **2026-11-25**; `JSON Schema Validation & Retry` unchanged (no attempt under its own name).
- **Mistakes:** **7 rows appended**, all `review` (repaired in-session → one post-repair recall each), miss classes preserved as `[miss: …]` (`discrimination` ×5, `execution` ×1, none on the metacognitive calibration row). They are the **transfer checks** for the next `/review`: nothing has yet re-tested the array-length seam cold.
- **Dependency events (verbatim):** three `just_tell_me` calls — (1) enforcing-path validator role / truth outside the pipe; (2) the counter state in the enforcing mask; (3) the path-dependence of the validator's no-op. Each followed ladder exhaustion; all are recorded on the `Structured Outputs (JSON contract)` session-3 chain and in the log. **Dependency: `just_tell_me` ×3 (2026-11-11)** — no learning record exists yet, so this session note is where the line lives until the record is written.
- **Graph:** distilled by `graph-extract` from this lesson file, this note and the three enriched pages, then merged with `graph.py merge` — see the `GRAPH_MERGE` receipt in the Clerk's report and the node/chain lists in `CLERK_WRITES`.
- **Marker / digest:** `Core/Pending Ingest.json` (`partial: true`) consumed and **cleared**; the Scout digest is **kept** and the lesson stays **paused / in-progress** (partial close, per the 7-day TTL rule).
- **Surfaced, not merged:** (a) this note's `## Open Questions` reports `hunch` items going **3 pass / 4 fail**; the 24-row attempt log gives **1 pass / 6 fail** for `hunch`-tagged items (`sure` 4 pass / 3 fail, untagged 3 pass / 7 fail). The attempt log is what `Attempts.json` now carries and what the wiki/state figures were derived from — the note's tally was not rewritten. (b) *"it is the provider's property"* appears in the v3 patch list but was graded **fail** (why-clause owed); it is preserved as a **repaired owner**, not a closed answer. (c) The learning record for this branch is still owed.
