# Lesson — Structured Outputs: JSON, Schema Validation, Constrained Decoding

- **Date:** 2026-11-09
- **Track:** aiefs · Phase 11 · L03
- **Source:** https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/03-structured-outputs (raw: `Knowledge Wiki/raw/sources/2026-11-09 - structured-outputs - rohit.md`; secondary: `... - openai.md`)
- **Session:** `Learning System/Sessions/Session — Structured Outputs (JSON, schema validation, constrained decoding) — 2026-11-09.md`
- **Status:** PAUSED — partial (session 3 banked 2026-11-11; third consecutive pause, exit ticket declined a third time)
- **Resume from:** the two never-listed modes — nested-object depth (A+1n, depends on the now-closed A-next), then optional-field omission (A+1o) — then graduation for the catchability axis (entailment check → naive-student clone → battery remainder: perturbation partially exercised via the counter's maxItems direction; sabotage untouched). The array-length seam is CLOSED (2026-11-11, see Session 3 log below).
- **Session 2 (2026-11-10) outcome:** scope recalibrated by learner directive — attacks target ONLY the Problem + Concept sections of the source site; Build-It code and row 7 (provider-doc rules) banked OUT of scope permanently. Row 4 CLOSED (concept-level; the build-it-dependent grain banked out of scope). Row 5 half-closed: hallucinated-values seam and enum rung-dependence seam closed in learner's own words (catchability axis + pipeline order raw → FSM/CFG mask → sampler); open attacks logged in the 2026-11-10 session note.

## v1 (learner's model, verbatim, [?] per their page)

1. Applications communicate via JSON, but LLMs by nature produce free-form text, hence we are bound to break the [?] of JSON. This [?] by nature — i.e. the problem can't be fixed by simply prompting "Respond in JSON", because even though it might [get it right] 90% of the time, it fails mainly [e.g.] markdown fences added to JSON, preamble, etc.
2. This is a decoding problem, and the solution is constrained decoding. This is where FSM/CFG — we mask tokens that would break the JSON schema, hence allowing only valid tokens to be sampled from.
3. Here are ways to [?]: Prompting → JSON mode → Schema mode → Constrained decoding.
4. Some failure modes include: hallucinated values, array length [?], too long or too small array length, [?] fields, enum confusion.
5. JSON is the control language. Pydantic makes JSON schemas automatically from data models typed in Python, and Instructor is what validates the schema generated and feeds the errors back into the LLM automatically for it to self-correct.

V1 confidence at writing: **sure** (calibration baseline — later flagged: 9 of 11 attack/check items failed; illusions-of-competence signal logged in Mistakes.md).

## Triage (against rohit + openai raw sources)

| # | Claim | Bucket | Note |
|---|---|---|---|
| 1 | JSON contract break; prompt-only ~90%; fences/preamble | solid | matches source |
| 2 | decoding problem, not prompt-engineering | solid | |
| 3 | Ladder Prompting → JSON mode → Schema mode → Constrained decoding | solid | |
| 4 | FSM/CFG masking — "we mask tokens that would break the JSON schema" | suspect → repaired-in-progress | deciding step taught (2-step repair); closing discriminator OPEN |
| 5 | Failure modes named as one lump | suspect | not yet attacked (row 5) |
| 6 | Pydantic → schema; Instructor validate+retry | solid | |
| 7 | (missing) OpenAI schema mode = subset of JSON Schema; strict requires all fields | missing | off-path this session; banked |

## Attacks & repair log (row 4)

- Predict probe (`{"product": "Sony"`): learner predicted rule outputs `,`/`}` — wrong (rule: mid-string branch → `['a-z','"']`); schema-side read correct.
- Mechanism press: same last char `"` → `:` (after key) vs `,` (after value) → legality is not a function of the tail.
- Failed repairs: schema-only → "next token distribution" → "keys and values" → repair mode entered (structural gap, nothing to cue).
- Repair step 1: flag bookkeeping over the emitted prefix ("you are here" = flags). Landed after 4 naming rounds + one nomenclature patch; learner re-owned: **"a boolean in progress."**
- Repair step 2: legal set = flag-state × schema-progress; mask to zero; renormalize. Learner wrote: "we simply hand the sampler e … the rest are masked." Decider side landed; the **discriminator keeps failing** — three fusion episodes (attributed `e`, then "the flag is any", then the rule's decider's answer at the new surface) all graded fail (`discrimination`).
- Ladder spend exceeded budget (source returns incl. the branch table + `else → ["any"]`) — difficulty signal: diagnosis regime was over the edge for self-repair.
- Closing fresh-surface check at `{"product": "Sony", "price": 348}`: 1/3 pass (decider set `,`), rule-side parts fail (rule early-exits on the parseable prefix → ends generation; does not grant `,`). **OPEN** — first thing `/continue` picks up.

## Attempts (summary; full log in Attempts.json)

14 graded attempts: spine pass (free-recall, sure); predict 3 → pass/fail/fail; mechanism presses → schema-only ✗, distribution ✗, keys-values ✗ (cue → repair); repair step-1 checks ✗/✓(rule-side)/✗/✓(re-own); contrast rounds ✗/✗; fresh-surface ✗. Exit ticket: **declined** (banked without).

## Session 3 (2026-11-11) — the array-length seam CLOSED

Resume probe + attack chain (all grade-audited; 24 graded items across 19 learner replies — 8 pass / 16 fail — this session):

- **Predict (turn 1):** enforcing provider → "error message" ✗ (attached decode enforcement to the validate-and-retry rung); non-enforcing provider → "the invalid array" ✓; "the difference lives in the output the user gets" ✗ (circular — outcomes, not location).
- **Mechanism press:** the array dies at the constrained-decoding arrow ✓ (`sure`, correct); "what is a post-sampler validator working on?" → "simply checking for hallucinated values" ✗ — inverts the learner's own 2026-11-10 closure; source clash posed (November closure vs today's words) → resolved: "the validator checks if it breaks the schema" ✓.
- **Repair 1 CLOSED (just-tell-me patch after ladder exhaustion):** on the enforcing path the post-sampler legality validator is a **no-op**; value truth is checked, if at all, **outside the output path** (eval/reconciliation against the source). Fresh surface (invoice `"total": 299.99` vs $348): first answer "nowhere is it caught" ✗ (`sure` on a half-answered two-part check — illusion-of-competence signal); after the detector self-clash ("detector sits at constrained decoding" ✗ — the mask never sees ground truth), closed: *"the ground truth comparison will have to sit after the post sampler validator step"* ✓.
- **Repair 2 CLOSED (counter patch, just-tell-me after ladder exhaustion):** flags × schema cannot express `minItems` (identical flags at the positions after items 1/2/3, diverging `]` legality — counterexample trap). Five failed candidates: flags × schema → "tracking `]`" → "`, vs ]`" → patch: the mask carries a **counter** of items emitted in this array (`]` legal iff `count ≥ minItems`; `,` legal only while `count < maxItems`) — a **number, not a boolean**. Fresh surface (maxItems: 2 direction): *"the counter says 2 which means , is invalid while ] is valid"* ✓ (`sure` earned).
- **Repair 3 CLOSED (path-dependence patch):** ownership predict "the violation is a property of constrained decoding" ✗ (both apps run the same rung — eliminated; owner handed via OpenAI base-vs-fine-tuned path + Anthropic minItems 0/1); "it is the provider's property" (owner correct, why-clause owed — graded fail); "null and void" / "it doesnt land, still no-op" on the non-enforcing path ✗✗ (self-contradiction with "the array is in an invalid state" one sentence apart) → just-tell-me patch: **the no-op is a property of the PATH, not the validator** (mask guarantees → validator idle; mask absent → validator is the only catcher of length legality). Deleted-validator scenario ✗ (idle/catcher swap) → two-blank fill: *"enforced path, non-enforced"* ✓ — seam closed.

State after session 3: row 4 CLOSED (2026-11-10), row 5 CLOSED (hallucinated values + enum rung 2026-11-10; array-length seam 2026-11-11). Still open: nested-object depth, optional-field omission, graduation battery. Exit ticket declined (third consecutive).

## Next session queue

1. **A+1n — nested-object depth (4+ levels):** one perturbation probe first; `full_teach` candidate on the stack if the one-flag-set model collapses (per-frame required-sets vs one tuple).
2. **A+1o — optional-field omission:** legal-by-default; remedy is authoring (`required` + explicit `null`), not enforcement; one perturbation probe.
3. **Graduation:** entailment check ("why must hallucinated values escape any schema-side gate?" — already answered in the learner's own words 2026-11-10, re-press at graduation) → naive-student clone on the patched pipeline model (raw distribution → mask w/ flags+counter → sampler; validator path-dependent; truth outside the pipe) → battery remainder (sabotage untouched; perturbation partially exercised via the counter's maxItems direction).
4. Row 7 stays banked out of scope (learner directive).

Wiki pages for the three concepts are live (`Knowledge Wiki/wiki/…`); `/ingest` re-sync if wiki/state drift is suspected.
