<!-- provenance: status=synthesis (`## My understanding` block status=learner-note) | source=raw/sources/2026-11-09 - structured-outputs - rohit.md + openai.md + anthropic-structured.md + anthropic-tool-use.md + instructor.md + jsonschema.md + jsonschema-object.md + outlines-paper.md + xgrammar.md + lmql.md + guidance.md | verified-by=— (review gate pending; the 2026-11-10 v2 and 2026-11-11 v3 additions are unreviewed) | date=2026-11-11 -->

# Structured Outputs (JSON contract)

**Insight:** a language model finishes a turn having produced a *string*; the application downstream wants a *value of a type*. Structured output is the contract that closes that gap, and the useful question is never "which library" but **where the constraint acts**: on the prompt (it only shifts probability mass), on the parse (JSON mode: the text parses, nothing more), or on the next-token distribution itself (masking: the illegal continuations are deleted at every step, so the string cannot leave the grammar). Rohit's own framing is the load-bearing one — *"This is not a prompt engineering problem. It is a decoding problem"* — because a 90%-reliable prompt plus a retry loop does not converge to a reliable API: it converts a syntax failure into a *consistency* failure, since the retry may return different data. Riding every tier is one more boundary that no tier covers: schema conformance is a claim about **shape**, and the model will happily invent a value that has the right type. Only an outside check — an eval harness holding the source document, or a cross-field consistency rule — can catch that. **2026-11-11 — ownership, the last seam:** whether a constraint even reaches the grammar is a **provider** property. The provider's compile coverage decides whether the mask exists at all, so the post-sampler validator's role flips with the path — **idle** where the mask already enforced the length rule, the **only catcher** of length legality where it did not — and "the validator is null and void" is only ever true of one of the two paths.

## My understanding

> status=learner-note — the learner's own words, verbatim, preserved. Never paraphrased or polished below. Versioned in order, never merged: **v1** (2026-11-09, the closed-book spine check) → a labeled breaking case → **v2** (2026-11-10, the catchability axis) → a second labeled breaking case → **v3** (2026-11-11, provider ownership + the path-dependent validator). Each version is a *patch*, not a rewrite: v2 patches one member of v1's failure-mode lump, v3 patches the members v2 left open, and neither re-authors the version before it. Annotations *around* the text are the AI's; the `[?]` blanks are the learner's and are left exactly as written.

**Version 1** — 2026-11-09, first closed-book model from the learner's handwritten/typed page (confidence `sure`; the exit ticket was declined):

> "1. Applications communicate via JSON, but LLMs by nature produce free-form text, hence we are bound to break the [?] of JSON. This [?] by nature — i.e. the problem can't be fixed by simply prompting 'Respond in JSON', because even though it might [get it right] 90% of the time, it fails mainly [e.g.] markdown fences added to JSON, preamble, etc. (2) This is a decoding problem, and the solution is constrained decoding. This is where FSM/CFG — we mask tokens that would break the JSON schema, hence allowing only valid tokens to be sampled from. 3. Here are ways to [?]: Prompting → JSON mode → Schema mode → Constrained decoding. 4. Some failure modes include: hallucinated values, array length [?], too long or too small array length, [?] fields, enum confusion. 5. JSON is the control language. Pydantic makes JSON schemas automatically from data models typed in Python, and Instructor is what validates the schema generated and feeds the errors back into the LLM automatically for it to self-correct."

**Reading of v1** (annotation, not the learner's words) — what the ten-minute spine check actually carried:

- **Solid (no repair needed).** The ~90% + fences/preamble failure of prompting (row 1); "this is a decoding problem" (row 2); the four-rung ladder (row 3); Pydantic → schema, Instructor → validate-and-feed-back (row 6). Rohit's naive-solution paragraph matches the learner almost clause for clause, including the markdown-fence and preamble examples.
- **Blanks never re-worded.** `[?] of JSON` (twice) and `ways to [?]` were left open on the page and were never filled in by the learner afterwards. They are recorded as blanks, **not** filled in here — the session repaired the *mechanism* (below), not the wording.
- **Suspect, repaired in session (row 4).** "we mask tokens that would break the JSON schema" is the right headline but was attached to a *decider* the learner could not yet run: the collapse into Rohit's last-character rule is documented on [[Constrained Decoding (parser-state masking)]]. The closing discriminator check was still **open when session 1 paused**; it closed at the start of session 2 — the closure (a new fresh surface plus the own-words restatement *flags × schema → mask + renormalise, ≠ the last-char rule*) is recorded on [[Constrained Decoding (parser-state masking)]], not in the v2 block above, which is the row-5 catchability patch.
- **Suspect, unattacked (row 5).** The failure modes arrive as one lump. The split that matters — which failures an enforcement tier can catch and which it cannot — is in `## Failure modes` below, and was **unattacked when session 1 paused**; it was attacked in session 2 and is now half-split (see `### Row-5 attack log`).
- **Missing (row 7).** "Schema mode guarantees the output matches it" carries an unflagged scope limit: every provider enforces only a *subset* of JSON Schema. Recorded off-path this session.

**Breaking case between v1 and v2** (the attack that forced the split, 2026-11-10): the invoice extraction where the source text says **$348** and the object carries `{"price": 299.99}`. The value is a legal `number`, the key set is right, the schema is satisfied — and the number is invented. v1 named "hallucinated values" as a failure mode and said nothing about its fate; the attack asked *where* such a value would be stopped, and nothing in the loop stops it.

**Version 2 — the catchability axis** (2026-11-10, after the row-5 attack; the learner's words, verbatim):

> "the machine knows the schema and legal set. what it would have to know is the exact value for the price key of this particular json object. it slips through since it is a valid entry(number)."

> (through Instructor) "what it validates against is whether this breaks the schema or not. the info needed to flag this output doesnt exist anywhere in that loop."

**Annotation around v2** (the AI's, not the learner's words). v2 is **not** a rewrite of v1's lump: it pins the fate of exactly one member. The claim it makes is an *information* claim, not an effort claim — the loop holds the schema, and the schema is a statement about shape, so "is this the value the document contained?" is not a question the loop can pose. **What v2 does not yet carry:** array length (the source's own caveat is about *providers* enforcing `minItems`/`maxItems` at decode — dropped from the lump), nested-object depth (4+ levels), and optional-field omission. Those three are open; the lump is half-split. The Instructor clause above is the learner's and is also preserved verbatim on [[JSON Schema Validation & Retry (Pydantic + Instructor)]].

**Breaking case between v2 and v3** (the attack that forced the split, 2026-11-11): the array-length seam. v2 said nothing about *length*, and the first probe showed the omission was not a detail — asked where a `minItems`-violating array dies on an enforcing provider, the learner answered **"error message"** (a validate-and-retry rung attached to the decode-level mask), then said the difference between providers **"lives in the output the user gets"** (circular: outcomes, not location). The source's own clause is the missing piece — *"Schemas support minItems and maxItems, but not all providers enforce them at the decoding level"* — a condition attached to **providers**, not to the mode, so the failure's *owner* had never been named.

**Version 3 — provider ownership and the path-dependent validator** (2026-11-11, verbatim, in the order the session produced them):

> "it is the provider's property"

> "the ground truth comparison will have to sit after the post sampler validator step"

> "the counter says 2 which means , is invalid while ] is valid"

> (two-blank fill, into "the validator is idle on the ___ path and catching on the ___ path") "enforced path, non-enforced"

**The failed candidates these patches replaced** (verbatim, in order — the scar is the point; none of these is the learner's final model): `"error message"` → `"the difference lives in the output the user gets"` → `"simply checking for hallucinated values"` → `"big picture vs local issues"` → `"nowhere is it caught"` (tagged `sure` on a half-answered check) → `"the violation is a property of constrained decoding"` → `"checks whatever else besides minItems was enforced upstream"` → `"null and void"` → `"it doesnt land, i guess still no-op"` → `"otherwise it would be idle"`.

**Annotations around v3** (the AI's, not the learner's words):

- **Ownership was graded fail, not pass.** *"it is the provider's property"* names the right owner, but the session's rule was owner **plus** a why-clause; the why-clause — a schema keyword the provider does not compile never becomes grammar state, so nothing at decode time can enforce it — was owed and is still owed. The seam closed on the two-blank fill, not on this sentence.
- **The counter sentence belongs to the mask, not to the validator.** *"the counter says 2 …"* describes what the enforcing mask carries (a numeric count of items emitted in this array — see [[Constrained Decoding (parser-state masking)]]). What it establishes *here* is narrower and is the step that killed the "null and void" reading: length legality is decidable **at decode time only if** the provider compiled `minItems`/`maxItems`; where it did not, the post-sampler validator is the only thing that will ever see the violation.
- **Path-dependence is not another mechanism.** The two-blank fill is a *locational* claim: the validator is the same code on both paths. What differs is whether anything is left for it to catch.

## The gap, in Rohit's own example

> "You ask an LLM: 'Extract the product name, price, and availability from this text.' It responds: `The product is the Sony WH-1000XM5 headphones, which cost $348.00 and are currently in stock.` That is a perfectly correct answer. It is also completely useless to your application." — `raw/sources/2026-11-09 - structured-outputs - rohit.md`

The naive fix is textbook prompt engineering: append "Respond in JSON". It works ~90% of the time; the other 10% delivers the sentence with `{"product": ...}` wrapped in fences, announced by *"Here's the JSON:"*, or with a bracket closed early. Wrapping it in `try/except` + retry buys a second failure mode: *"The retry sometimes produces different data. Now you have a consistency problem on top of a parsing problem."*

## Where the constraint acts — the ladder

| Rung | API shape | Guaranteed | **Not** guaranteed | Typical failure |
|---|---|---|---|---|
| Prompt-based | text: "Respond in JSON" | nothing | everything | fences, preamble, early `}` |
| JSON mode | `response_format: {"type": "json_object"}` | the emitted text **parses** | any adherence to *your* schema (keys, types, required) | extra keys, wrong types, missing fields |
| Schema mode | `json_schema` + `strict: true`; Anthropic tool `input_schema`; Gemini `response_schema` | conformance to the **sent** schema subset | keywords outside that subset; value truth; completion | stripped constraints; invented values; refusals |
| Constrained decoding | the engine under those flags | every sampled token keeps the string inside the grammar | same as above — this is a *mechanism*, not a separate knob | compile cost; masking soundness/completeness |

One correction worth keeping: the ladder is usually printed as four equal rungs, but rung 4 is **how rung 3 is implemented**, not a fourth API you call separately. OpenAI's structured-output mode *is* constrained decoding under `json_schema` + `strict` (Rohit says so directly in `## Use It`: "Every token the model generates is guaranteed to produce output matching the Pydantic schema … The constraint is baked into the decoding process"). The three API-visible rungs are prompt / `json_object` / `json_schema`; masking is the reason the third one is a guarantee rather than a hope. The honest way to teach the ladder is therefore *where the constraint acts*: on the prompt (probability), on the parse (syntax), on the distribution (grammar).

## JSON Schema is the contract language

Every rung from JSON mode upward speaks JSON Schema, and the vocabulary divides into three keyword families (full treatment on [[JSON Schema Validation & Retry (Pydantic + Instructor)]]):

- **type membership** — `string | number | integer | boolean | object | array | null`, with `integer ⊂ number` and `boolean` disjoint from both;
- **presence** — `required`, plus `minItems`/`maxItems` for arrays;
- **closure** — `additionalProperties`, `patternProperties`: the only family that *prunes* unlisted keys.

Rohit's example contract, and the one this session's checks kept re-using:

```json
{"type": "object",
 "properties": {"product": {"type": "string"},
                "price": {"type": "number", "minimum": 0},
                "in_stock": {"type": "boolean"},
                "categories": {"type": "array", "items": {"type": "string"}}},
 "required": ["product", "price", "in_stock"]}
```

Two traps sit inside that eight-line schema and both are load-bearing later: extra keys are **allowed** unless `additionalProperties: false` is set (the spec default), and `minimum` is a constraint *some* providers delete before decoding.

## What "guaranteed" covers — ⚠️ source disagreement, resolved

**Rohit:** "Schema mode: the API takes a JSON Schema and guarantees the output matches it. … The output has the exact keys, types, and constraints you specified." and constrained decoding "guarantees 100% schema compliance".

**OpenAI:** "Structured Outputs supports a subset of the JSON Schema language." Unsupported (strict mode errors out): composition — `allOf`, `not`, `dependentRequired`, `dependentSchemas`, `if`, `then`, `else`; the root must be an **object** and must not be `anyOf` (so a Zod discriminated union that compiles to a top-level `anyOf` simply fails); `additionalProperties: false` must always be set; and *all* fields must be `required`. Fine-tuned models additionally lose `minLength`/`maxLength`/`pattern`/`format`, `minimum`/`maximum`/`multipleOf`, `patternProperties`, `minItems`/`maxItems`.

**Anthropic native structured outputs:** even tighter — recursive schemas, complex types inside enums, external `$ref`, **numerical constraints** (`minimum`, `maximum`, `multipleOf`), **string constraints** (`minLength`, `maxLength`), array constraints beyond `minItems` 0/1, and `additionalProperties` set to anything other than `false` are *not supported*; the SDK's `transform_schema()` strips them and, where possible, moves them into field descriptions.

**Resolution (not a tie):** the guarantee holds over the **schema actually sent**, not over the schema you wrote. `minimum: 0` on Anthropic is deleted before decoding — the model is free to emit a negative price and the grammar will not stop it; only a client-side re-validation against the *original* schema recovers the check. "100% compliance" is true of the subset and silent about the rest. This is the page-1 form of triage row 7.

Two more exclusions that are easy to miss and both documented by OpenAI: **key order** follows the schema's order (not decoration — it is a consequence of compiling the schema into the grammar), and **completion events sit outside every tier** — a safety refusal (`choices[0].message.refusal`) or `finish_reason == "length"` produces a response that is not schema-shaped at all, so the caller must check those before parsing.

## Failure modes, and which tier can catch them

Rohit lists five. Sorted by *what can catch it*, which is the split the learner had not yet made at first writing and **now half owns** (triage row 5: attacked 2026-11-10 — one mode closed, four open; see `### Row-5 attack log` below):

| Failure | Caught by | Why |
|---|---|---|
| **Hallucinated values** — `{"price": 299.99}` where the text says $348 | **nothing in the stack** — only an eval harness, a cross-field rule, or a human spot check | the type is right and the value is wrong; a grammar cannot express "this number is in the document" |
| **Enum confusion** — `"available"` for `["in_stock","out_of_stock","preorder"]` | constrained decoding (the allowed set is a grammar fact); *prompt-based cannot* | the enum is a finite language |
| **Array length** — too many/too few items | `minItems`/`maxItems` **if the provider enforces them at decode**; otherwise the validator | keyword support varies by provider/model tier |
| **Optional-field omission** | `required` + forcing an explicit `null` | presence is decidable from the grammar |
| **Deep nesting (4+ levels)** | nothing reliable — error rate rises with depth | each level is another place to lose the structural state |

The one-line version: **enforcement tiers catch grammar failures, not semantic ones.** That is the misapplication the digest flags for the invoice pipeline — `total` straight into an accounting table because the schema was "guaranteed".

### Row-5 attack log (2026-11-10) — the lump half-split

The catchability split this page already carried was **attacked** in session 2 and the learner now owns it in their own words:

- **Hallucinated values — CLOSED.** Two graded items, both pass, both on the learner's articulation *before* any reveal: predict where the invented price escapes the mask machine, then the same question through Instructor's validate-and-retry loop. The held claim is an information claim: the loop holds the schema, never the source document (v2 verbatim under `## My understanding`). Nothing in the stack catches it — an eval harness holding the document, a cross-field identity, or a human spot check are the only guards.
- **Enum confusion — CLOSED per rung.** At the masking rung the legal set is a grammar fact and the off-enum string is masked *before* the sampler; at the prompting rung the prompt only **lowers** its probability (lowered ≠ zero) and the component that would zero it — an **FSM/CFG** — is absent, so the sampler can still emit it. Source agreement: *"Good constrained decoding prevents this. Prompt-based approaches do not."*
- **Array length — CLOSED (2026-11-11, all four parts).** The source's caveat is attached to **providers**, not to the mode: *"Schemas support minItems and maxItems but not all providers enforce them at the decoding level."* The answer, closed 2026-11-11: the failure is the **provider's** property — whether the keyword becomes grammar state is decided by the provider's compile coverage — and the mask carries a **counter** (`]` legal iff `count ≥ minItems`, `,` only while `count < maxItems`) on the paths where the keyword *was* compiled. The post-sampler validator is a no-op on those paths and the **only catcher** on the others. The learner's lump dropped the condition entirely; the full attack chain is in the session-3 log below.
- **Nested-object depth (4+ levels) — never listed by the learner.** Source: *"deeply nested schemas (4+ levels) produce more errors. Each level of nesting is another place where the model can lose track of structure."*
- **Optional-field omission — never listed by the learner.** Source: *"the model omits fields that are technically optional but semantically important for your use case. Set them as required in the schema … force the model to produce null explicitly."* Note the shape of the source's fix: it is a **schema-side** fix (make it required), which is exactly the catchability axis again — the fix works because presence is decidable from the grammar.

Both unlisted modes stayed **unreached** at the pause; they are `full_teach` candidates after one perturbation probe each. As of the 2026-11-11 pause they are the **next** attacks in dependency order: **A+1n** nested-object depth, then **A+1o** optional-field omission; **graduation** (entailment check → `naive-student` clone → battery remainder) depends on both.

**Scope recalibration (learner directive, session invariant):** mental-model attacks on this lesson cover the source's **Problem** and **Concept** sections only. The Build-It code and the provider-doc rules (triage row 7 — all-fields-required, schema subset) are **out of attack scope permanently** for this lesson and must not be re-issued.

### Session 3 attack chain — the array-length seam (2026-11-11, CLOSED)

Attacks in dependency order, exactly as the Tutor ran them (every item grade-audited):

| # | Attack | Outcome |
|---|---|---|
| 1 | **Where decode-level enforcement acts** — predict the enforcing provider, the non-enforcing provider, and where the difference *lives* | partial: non-enforcing → "the user will get the invalid array" ✓; enforcing → "error message" ✗ (the validate-and-retry rung attached to the mask); "the difference lives in the output the user gets" ✗ (circular). Mechanism press: "the invalid array dies at the constrained-decoding arrow" ✓ (`sure`). |
| 2 | **What is left for the post-sampler validator on the enforcing path** | three failed candidates (`"simply checking for hallucinated values"` — which inverts the learner's own November legality-vs-truth closure; "the big picture"; "not sure") → a `just_tell_me` patch → fresh surface (invoice `"total": 299.99` against a source `$348`): `"nowhere is it caught"` (graded fail, tagged `sure` — illusion-of-competence), detector self-clash ("detector sits at constrained decoding" ✗ — the mask never sees ground truth), closed on *"the ground truth comparison will have to sit after the post sampler validator step"* ✓. |
| 3 | **What the enforcing mask must carry for `minItems`/`maxItems`** | counterexample trap (flags × schema identical at the positions after items 1/2/3 while `]` legality diverges) → five failed candidates (`"flags and the schema"`, `"tracking ]"`, `", vs ]"`) → `just_tell_me` patch: the mask carries a **counter** of items emitted, `]` legal iff `count ≥ minItems`, `,` legal only while `count < maxItems` — a number, not a boolean. Fresh surface in the `maxItems` direction: *"the counter says 2 which means , is invalid while ] is valid"* ✓ (`sure` earned). Full mechanism on [[Constrained Decoding (parser-state masking)]]. |
| 4 | **Whose property the failure is** | `"the violation is a property of constrained decoding"` ✗ (both apps run the same rung — eliminated); `"it is the provider's property"` ✗ (owner right, why-clause owed); `"null and void"` / `"it doesnt land, i guess still no-op"` on the non-enforcing path ✗✗ (self-contradicting their own "the array is in an invalid state" one sentence apart) → `just_tell_me` patch: the no-op is a property of the **path**, not of the validator; deleted-validator scenario ✗ (idle/catcher swapped); closed on the two-blank fill *"enforced path, non-enforced"* ✓. |

**Repair steps** (Tutor-authored one-step patches — never merged into the learner's model, kept with their checks):

| # | Fact delivered | Rests on | Check | Learner's check answer |
|---|---|---|---|---|
| 1 | On the enforcing path the post-sampler legality validator is a **no-op**; value truth is checked, if at all, **outside the output path** | the mask already deleted every illegal continuation, so legality has nothing left to catch; a validator's oracle is the schema, never the source document | invoice with `"total": 299.99` against a $348 source — anything between mask and caller? where does detection live? | *"nowhere is it caught"* (half-answered) → after the detector self-clash, *"the ground truth comparison will have to sit after the post sampler validator step"* |
| 2 | The mask carries a **counter** of items emitted in the array (`]` iff `count ≥ minItems`, `,` only while `count < maxItems`) — numeric state, not a flag | flags × schema are identical at the three positions after items 1, 2, 3, yet `]` legality differs — no boolean tuple can express that | `maxItems: 2` after item 2 — what does the counter read, and are `,` / `]` legal? | *"the counter says 2 which means , is invalid while ] is valid"* |
| 3 | The validator's no-op is a property of the **path**, not of the validator (mask guarantees → validator idle; mask absent → the validator is the only catcher of length legality) | the provider's compile coverage decides whether the mask exists at all | two-blank fill: "the validator is idle on the ___ path and catching on the ___ path" | *"enforced path, non-enforced"* |

**Dependency events (learner opt-outs, carried verbatim):** three `just_tell_me` calls this session, each after the hint ladder was exhausted — (1) the enforcing-path validator role / truth-checking outside the pipe, triggered by three stalls (cue, inversion, big-picture); (2) the counter state in the enforcing mask, triggered by five failed candidates on what the mask tracks; (3) the path-dependence of the no-op, triggered by a self-contradiction one sentence apart. **Exit ticket declined** — third consecutive decline (offered once, not pressed).

**Still open after session 3 (dependency order):** **A+1n** nested-object depth (4+ levels) — never listed by the learner; one perturbation probe (a leaf object closed inside `orders[3].lines[1].modifiers[0]` with `required_left` non-empty), `full_teach` candidate on the stack if the one-flag-set model collapses. **A+1o** optional-field omission — never listed; legal by default; the remedy is **authoring** (`required` + an explicit `null`), not enforcement. **graduation** — the entailment check ("why must hallucinated values escape any schema-side gate?" — answered in the learner's own words 2026-11-10, to be re-pressed), then a `naive-student` clone on the v3 pipeline model, then the battery remainder (sabotage untouched; perturbation only partially exercised, via the counter's `maxItems` direction).



## Three doors to the same contract

- **OpenAI** — `response_format: {type: "json_schema", json_schema: {name, strict: true, schema}}`, or `client.beta.chat.completions.parse(..., response_format=PydanticModel)` which takes the class directly. `tool_choice="required"` is the same machinery wearing a tool's name.
- **Anthropic** — historically **tool use**: the model emits a tool call whose arguments match `input_schema`, so tool *selection* and structured *output* come from one surface (`raw/sources/… - anthropic-tool-use.md`). A native structured-outputs tier now exists beside it, with grammar compilation, a 24-hour compiled-grammar cache, and hard complexity limits (a `400 "Schema is too complex for compilation"`, or a 180-second compile timeout).
- **Pydantic + Instructor** — the authoring layer that makes all of the above one call: define a `BaseModel`, pass the class, get a validated instance. See [[JSON Schema Validation & Retry (Pydantic + Instructor)]].

Tool use is the better door when the model must *choose which* schema applies (ten extraction shapes, pick one); `response_format` is the better door when there is exactly one.

## Interrogation record (2026-11-09)

Handoff carried from the Tutor at the pause. Preserved in dependency order; nothing below was resolved after it was written.

| # | Triage row (as carried) | Bucket | Quote / source |
|---|---|---|---|
| 1 | Prompts-only output ~90% solution; matching tails at 'North&Fences/preamble failure mode', against Rohit's naive-solution case | `solid` | learner v1 item 1 vs *"This works 90% of the time … markdown code fences … preamble"* (rohit) |
| 2 | It is a decoding problem, not a prompt-engineering problem | `solid` | learner v1 item 2 vs *"This is not a prompt engineering problem. It is a decoding problem."* (rohit) |
| 3 | Ladder Prompting → JSON mode → Schema mode → Constrained decoding | `solid` | learner v1 item 3 vs "The Structured Output Spectrum" (rohit) |
| 4 | FSM/CFG masking: "we mask tokens that would break the JSON schema" — deciding step installed by a two-step repair (flag bookkeeping landed — "a boolean in progress"; decider side landed — "we simply hand the sampler e … the rest are masked"); the **decider-vs-rule discriminator is still OPEN** after three fusion episodes, and the closing fresh-surface check graded **fail** | `suspect → repaired-in-progress` | learner v1 item 2 → [[Constrained Decoding (parser-state masking)]] |
| 5 | Failure modes named as one lump — the lesson splits on catchability: hallucinated values escape schema validation ("type correct, value wrong"); enum confusion is the constrained-decoding-preventable case | `suspect`, `on_path: true`, `requires: ["row 4 closure"]` | learner v1 item 4 vs `## Failure modes` above |
| 6 | Pydantic schema generation + Instructor validate-and-retry loop | `solid` | learner v1 item 5 vs rohit `## The Pydantic Pattern` / `### Instructor Library` |
| 7 | OpenAI Structured Outputs supports only a subset of JSON Schema (composition keywords unsupported; strict mode requires all fields required) — noted from the scout digest, not yet surfaced/attacked | `missing`, `on_path: false` | openai docs vs rohit's "exact keys, types, and constraints" — see ⚠️ above |

### Row-4 repair log (reconciled from the Tutor's lesson file, 2026-11-09)

The attacks on triage row 4, in the order they ran — kept because the discrimination they failed is exactly what `/continue` resumes at:

| Step | Probe | Outcome |
|---|---|---|
| 1 | Predict probe at `{"product": "Sony"` — what does the rule hand the sampler? | learner predicted `,` / `}` — the **decider's** answer; the rule returns `['a-z','"']`. Schema-side read correct. |
| 2 | Mechanism press — the same trailing `"` demands `:` after a **key** and `,` after a **value** | legality is not a function of the tail; pressed, then lost. |
| 3 | Three schema-only repairs ("next token distribution" → "keys and values" → naming rounds) | all failed → **repair mode entered** (a structural gap has nothing to cue). |
| 4 | **Repair step 1** — flag bookkeeping over the emitted prefix ("you are here" = the flags) | landed after 4 naming rounds + one nomenclature patch; learner re-owned: **"a boolean in progress."** |
| 5 | **Repair step 2** — legal set = flag-state × schema-progress, mask to zero, renormalise | decider side landed: "we simply hand the sampler e … the rest are masked." |
| 6 | Contrast rounds, rule vs decider | **2/2 fail** — the rule layer, flag layer and distribution layer fused ("the flag is any; e has high probability"). |
| 7 | **Closing fresh surface** at `{"product": "Sony", "price": 348}` | **1/3** — `,` correct; *why-legal* and *granted/withheld* both answered from the rule ("string" where `required_left` is the point). **Row 4 stays OPEN.** |

Ladder spend exceeded budget on this gap (source returns including the branch table and `else → ["any"]`) — recorded as a **difficulty signal** (the diagnosis regime sat over the edge for self-repair), never as a learner verdict. The `## My understanding` fragments above are where the repair stopped and are deliberately left unpolished.

**Open attacks, dependency order** (nothing in flight at the pause):

1. **row 4 closure** — decider-vs-rule discrimination. Fresh-surface check at `{"product": "Sony", "price": 348}` **failed** (the learner handed the rule the decider's answer: `1) ','` marked pass, `2)` and `3)` fail). `miss_class: discrimination`. Resume rung: fresh surface again after a flags × schema mask re-cap.
2. **row 5** — split the failure-mode lump into what enforcement tiers can and cannot catch (`requires: ["row 4 closure"]`). `not_yet_attacked`.
3. **row 7** — the schema-mode subset limitation. `recorded, off-path this session`.

**Battery withheld.** No repair receipt for row 4, row 5 untouched, graduation/clone never reached. `/continue` must resume at the open fresh-surface discriminator, not at the start of the lesson.

## Open questions

- ~~Does schema mode mean what the docs say?~~ Resolved above: the guarantee is over the sent subset.
- What is the *right* catch for a hallucinated value in a one-off pipeline — a second extraction and a diff, a cross-field identity, or a human spot check? (Not taught this session; the lesson names an eval suite of hand-labelled pairs.)
- **Next attack (2026-11-10 pause):** do `minItems`/`maxItems` hold at decode time on the models in use, or only in the validator? The source attaches the caveat to **providers**, so the real question is whose property the failure is — the mode's or the provider choice's. **Resolved 2026-11-11:** the **provider's** (compile coverage), and the validator's role is path-dependent as a consequence. **Next attacks (dependency order):** A+1n nested-object depth → A+1o optional-field omission → graduation (entailment check → `naive-student` clone → battery remainder).

## Sources

- `raw/sources/2026-11-09 - structured-outputs - rohit.md` — the lesson (spectrum, schema, Pydantic, tool use, five failure modes).
- `raw/sources/2026-11-10 - structured-outputs - rohit.md` — the 2026-11-10 re-fetch of the same page; its **Problem + Concept** sections are the learner's declared read scope for this session (the Build-It code is out of attack scope).
- `raw/sources/2026-11-09 - structured-outputs - openai.md` — supported subset, all-required rule, `additionalProperties: false`, root-object rule, key ordering, refusals/`max_tokens`.
- `raw/sources/2026-11-09 - structured-outputs - anthropic-structured.md`, `… - anthropic-tool-use.md` — native tier, stripped constraints, grammar cache/compile limits; tool use as the earlier surface.
- `raw/sources/2026-11-09 - structured-outputs - instructor.md`, `… - jsonschema.md`, `… - jsonschema-object.md` — retry loop; the spec's defaults.
- `raw/sources/2026-11-09 - structured-outputs - outlines-paper.md`, `… - outlines-github.md`, `… - xgrammar.md`, `… - lmql.md`, `… - guidance.md` — the engine layer behind rung 4.
