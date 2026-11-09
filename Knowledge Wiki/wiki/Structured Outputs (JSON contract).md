<!-- provenance: status=synthesis (`## My understanding` block status=learner-note) | source=raw/sources/2026-11-09 - structured-outputs - rohit.md + openai.md + anthropic-structured.md + anthropic-tool-use.md + instructor.md + jsonschema.md + jsonschema-object.md + outlines-paper.md + xgrammar.md + lmql.md + guidance.md | verified-by=— (review gate pending) | date=2026-11-09 -->

# Structured Outputs (JSON contract)

**Insight:** a language model finishes a turn having produced a *string*; the application downstream wants a *value of a type*. Structured output is the contract that closes that gap, and the useful question is never "which library" but **where the constraint acts**: on the prompt (it only shifts probability mass), on the parse (JSON mode: the text parses, nothing more), or on the next-token distribution itself (masking: the illegal continuations are deleted at every step, so the string cannot leave the grammar). Rohit's own framing is the load-bearing one — *"This is not a prompt engineering problem. It is a decoding problem"* — because a 90%-reliable prompt plus a retry loop does not converge to a reliable API: it converts a syntax failure into a *consistency* failure, since the retry may return different data. Riding every tier is one more boundary that no tier covers: schema conformance is a claim about **shape**, and the model will happily invent a value that has the right type. Only an outside check — an eval harness holding the source document, or a cross-field consistency rule — can catch that.

## My understanding

> status=learner-note — the learner's own words, verbatim, preserved. Never paraphrased or polished below. Version 1 only: the lesson was paused before graduation, so no v2 exists. Annotations *around* the text are the AI's; the `[?]` blanks are the learner's and are left exactly as written.

**Version 1** — 2026-11-09, first closed-book model from the learner's handwritten/typed page (confidence `sure`; the exit ticket was declined):

> "1. Applications communicate via JSON, but LLMs by nature produce free-form text, hence we are bound to break the [?] of JSON. This [?] by nature — i.e. the problem can't be fixed by simply prompting 'Respond in JSON', because even though it might [get it right] 90% of the time, it fails mainly [e.g.] markdown fences added to JSON, preamble, etc. (2) This is a decoding problem, and the solution is constrained decoding. This is where FSM/CFG — we mask tokens that would break the JSON schema, hence allowing only valid tokens to be sampled from. 3. Here are ways to [?]: Prompting → JSON mode → Schema mode → Constrained decoding. 4. Some failure modes include: hallucinated values, array length [?], too long or too small array length, [?] fields, enum confusion. 5. JSON is the control language. Pydantic makes JSON schemas automatically from data models typed in Python, and Instructor is what validates the schema generated and feeds the errors back into the LLM automatically for it to self-correct."

**Reading of v1** (annotation, not the learner's words) — what the ten-minute spine check actually carried:

- **Solid (no repair needed).** The ~90% + fences/preamble failure of prompting (row 1); "this is a decoding problem" (row 2); the four-rung ladder (row 3); Pydantic → schema, Instructor → validate-and-feed-back (row 6). Rohit's naive-solution paragraph matches the learner almost clause for clause, including the markdown-fence and preamble examples.
- **Blanks never re-worded.** `[?] of JSON` (twice) and `ways to [?]` were left open on the page and were never filled in by the learner afterwards. They are recorded as blanks, **not** filled in here — the session repaired the *mechanism* (below), not the wording.
- **Suspect, repaired in session (row 4).** "we mask tokens that would break the JSON schema" is the right headline but was attached to a *decider* the learner could not yet run: the collapse into Rohit's last-character rule is documented on [[Constrained Decoding (parser-state masking)]]. The closing discriminator check is still **open**.
- **Suspect, unattacked (row 5).** The failure modes arrive as one lump. The split that matters — which failures an enforcement tier can catch and which it cannot — is in `## Failure modes` below, and was **never attacked** this session (paused before it).
- **Missing (row 7).** "Schema mode guarantees the output matches it" carries an unflagged scope limit: every provider enforces only a *subset* of JSON Schema. Recorded off-path this session.

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

Rohit lists five. Sorted by *what can catch it*, which is the split the learner had not yet made (triage row 5, **unattacked**):

| Failure | Caught by | Why |
|---|---|---|
| **Hallucinated values** — `{"price": 299.99}` where the text says $348 | **nothing in the stack** — only an eval harness, a cross-field rule, or a human spot check | the type is right and the value is wrong; a grammar cannot express "this number is in the document" |
| **Enum confusion** — `"available"` for `["in_stock","out_of_stock","preorder"]` | constrained decoding (the allowed set is a grammar fact); *prompt-based cannot* | the enum is a finite language |
| **Array length** — too many/too few items | `minItems`/`maxItems` **if the provider enforces them at decode**; otherwise the validator | keyword support varies by provider/model tier |
| **Optional-field omission** | `required` + forcing an explicit `null` | presence is decidable from the grammar |
| **Deep nesting (4+ levels)** | nothing reliable — error rate rises with depth | each level is another place to lose the structural state |

The one-line version: **enforcement tiers catch grammar failures, not semantic ones.** That is the misapplication the digest flags for the invoice pipeline — `total` straight into an accounting table because the schema was "guaranteed".

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
| 4 | FSM/CFG masking: "we mask tokens that would break the JSON schema" — deciding step now installed via repair; closing discriminator check still **OPEN** | `suspect` | learner v1 item 2 → [[Constrained Decoding (parser-state masking)]] |
| 5 | Failure modes named as one lump — the lesson splits on catchability: hallucinated values escape schema validation ("type correct, value wrong"); enum confusion is the constrained-decoding-preventable case | `suspect`, `on_path: true`, `requires: ["row 4 closure"]` | learner v1 item 4 vs `## Failure modes` above |
| 6 | Pydantic schema generation + Instructor validate-and-retry loop | `solid` | learner v1 item 5 vs rohit `## The Pydantic Pattern` / `### Instructor Library` |
| 7 | OpenAI Structured Outputs supports only a subset of JSON Schema (composition keywords unsupported; strict mode requires all fields required) — noted from the scout digest, not yet surfaced/attacked | `missing`, `on_path: false` | openai docs vs rohit's "exact keys, types, and constraints" — see ⚠️ above |

**Open attacks, dependency order** (nothing in flight at the pause):

1. **row 4 closure** — decider-vs-rule discrimination. Fresh-surface check at `{"product": "Sony", "price": 348}` **failed** (the learner handed the rule the decider's answer: `1) ','` marked pass, `2)` and `3)` fail). `miss_class: discrimination`. Resume rung: fresh surface again after a flags × schema mask re-cap.
2. **row 5** — split the failure-mode lump into what enforcement tiers can and cannot catch (`requires: ["row 4 closure"]`). `not_yet_attacked`.
3. **row 7** — the schema-mode subset limitation. `recorded, off-path this session`.

**Battery withheld.** No repair receipt for row 4, row 5 untouched, graduation/clone never reached. `/continue` must resume at the open fresh-surface discriminator, not at the start of the lesson.

## Open questions

- ~~Does schema mode mean what the docs say?~~ Resolved above: the guarantee is over the sent subset.
- What is the *right* catch for a hallucinated value in a one-off pipeline — a second extraction and a diff, a cross-field identity, or a human spot check? (Not taught this session; the lesson names an eval suite of hand-labelled pairs.)
- Do `minItems`/`maxItems` actually hold at decode time on the models in use, or only in the validator? Provider- and tier-specific; unchecked.

## Sources

- `raw/sources/2026-11-09 - structured-outputs - rohit.md` — the lesson (spectrum, schema, Pydantic, tool use, five failure modes).
- `raw/sources/2026-11-09 - structured-outputs - openai.md` — supported subset, all-required rule, `additionalProperties: false`, root-object rule, key ordering, refusals/`max_tokens`.
- `raw/sources/2026-11-09 - structured-outputs - anthropic-structured.md`, `… - anthropic-tool-use.md` — native tier, stripped constraints, grammar cache/compile limits; tool use as the earlier surface.
- `raw/sources/2026-11-09 - structured-outputs - instructor.md`, `… - jsonschema.md`, `… - jsonschema-object.md` — retry loop; the spec's defaults.
- `raw/sources/2026-11-09 - structured-outputs - outlines-paper.md`, `… - outlines-github.md`, `… - xgrammar.md`, `… - lmql.md`, `… - guidance.md` — the engine layer behind rung 4.
