# Lesson — Structured Outputs: JSON, Schema Validation, Constrained Decoding

- **Date:** 2026-11-09
- **Track:** aiefs · Phase 11 · L03
- **Source:** https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/03-structured-outputs (raw: `Knowledge Wiki/raw/sources/2026-11-09 - structured-outputs - rohit.md`; secondary: `... - openai.md`)
- **Session:** `Learning System/Sessions/Session — Structured Outputs (JSON, schema validation, constrained decoding) — 2026-11-09.md`
- **Status:** PAUSED — mid-repair (partial close)
- **Resume from:** fresh-surface closing check of the row-4 repair — decider-vs-rule discrimination at `{"product": "Sony", "price": 348}`. On resume: re-anchor the two deciders on a NEW surface, close the gap with a fresh-surface pass + own-words restatement, then attack row 5, then graduation.

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

## Next session queue

1. Close row 4 (fresh-surface discriminator, then own-words restatement of "flags × schema → mask + renormalize, ≠ last-char rule").
2. Attack row 5 (failure-mode lump split: what constrained decoding can/cannot catch — hallucinated values escape; "type correct, value wrong").
3. Consider row 7 (schema-mode subset limits; OpenAI composition keywords; strict all-fields-required).
4. Graduation: entailment check → naive-student clone on the repaired decider model; battery remainder (perturbation/sabotage) for untouched dimensions.

Wiki pages for the three concepts are live (`Knowledge Wiki/wiki/…`); `/ingest` re-sync if wiki/state drift is suspected.
