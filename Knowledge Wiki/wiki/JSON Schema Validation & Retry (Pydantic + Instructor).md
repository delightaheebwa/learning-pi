<!-- provenance: status=synthesis (`## My understanding` block status=learner-note — a verbatim excerpt of the same v1 block carried on [[Structured Outputs (JSON contract)]]) | source=raw/sources/2026-11-09 - structured-outputs - rohit.md + instructor.md + jsonschema.md + jsonschema-object.md + openai.md + anthropic-structured.md + anthropic-tool-use.md | verified-by=— (review gate pending) | date=2026-11-09 -->

# JSON Schema Validation & Retry (Pydantic + Instructor)

**Insight:** a validator is a **predicate over the keywords it implements**, not a proof of correctness — `validate(data, schema) == []` means "no rule I know about was violated", and a keyword the implementation never looks at is silently satisfied. The whole layer has two jobs that are easy to confuse. **Pydantic** authors the contract: a typed Python class *generates* the JSON Schema, so the schema and the parser can't drift. **Instructor** closes the loop: it validates the returned object and, on failure, puts the `ValidationError` back into the conversation as context for a retry. That loop is a *repair*, not a guarantee — it costs an extra call and the retried answer is a fresh sample, so it can return **different data** for the same input. The consistency problem Rohit opens the lesson with is the price of the retry loop, which is why the strong form of the answer is to stop needing it (schema/constrained mode) while still keeping a validator against your *original* schema, because every provider silently narrows the schema it actually enforces.

## My understanding

> status=learner-note — the learner's own words, verbatim. This is **item 5 of the same v1 page** preserved in full on [[Structured Outputs (JSON contract)]]; it is quoted here because this page is its concept. Not rewritten, not polished, and not a second model.

> "5. JSON is the control language. Pydantic makes JSON schemas automatically from data models typed in Python, and Instructor is what validates the schema generated and feeds the errors back into the LLM automatically for it to self-correct."

**Reading** (annotation, not the learner's words): both halves are correct and both were triaged `solid`. Two things the sentence does not yet carry — *what the validator actually checks* (below) and *what the retry loop costs* (below). Neither was attacked before the pause.

## Pydantic: the contract is written once

```python
from pydantic import BaseModel

class Product(BaseModel):
    product: str
    price: float
    in_stock: bool
    categories: list[str] = []
```

This *is* the schema on the previous page — same object/`required`/types — generated mechanically. That is the whole value: the type the application parses into and the schema sent to the provider come from one declaration, so the classic bug (validator says one thing, decoder enforces another) is designed out. OpenAI's SDK and Instructor both accept the class directly:

```python
product = client.chat.completions.create(..., response_model=Product)   # instructor
```

Rohit's from-scratch equivalent is a `SchemaField` + `model_to_schema` pair that maps `str→"string"`, `int→"integer"`, `float→"number"`, `bool→"boolean"`, `list→{"type":"array","items":{...}}`, hoists `enum`/`minimum`/`maximum`, and collects `required` from the fields marked required — a twelve-line version of the same idea, useful precisely because it shows there is no magic in it.

## The validator: a structural recursion

`validate(data, schema)` walks `(instance, subschema)` pairs carrying a **path** (`""`, `".price"`, `"[2]"`, `".categories[0]"`) so every error names where it happened. Three keyword families do all the work:

| Family | Keywords | Question answered |
|---|---|---|
| **type membership** | `type` | is this instance in the named branch of JSON's type lattice? |
| **presence** | `required`, `minItems`, `maxItems` | is the shape *complete*? |
| **closure** | `additionalProperties`, `patternProperties` | may unlisted keys exist at all? (the only pruning family) |

Everything else — `minimum`/`maximum`, `enum`, `pattern`, `oneOf`/`anyOf`/`allOf`, `$ref` — is a further predicate layered on those three. The implementation discipline that follows is blunt: **any keyword you do not implement is silently satisfied**, and "my validator passed" is only evidence about the keywords in the list above.

## Python's type lattice is not JSON's

Rohit's own `validate_schema` demonstrates the trap in the sources:

```python
{"product": "Test", "price": True, "in_stock": True}   # → [] (PASSES) against price: {"type":"number","minimum":0}
```

`isinstance(True, (int, float))` is `True` in Python — `bool` is a subclass of `int`. JSON's lattice puts `boolean` and `number` in **disjoint** branches, so a boolean where a number is required is a type violation that the Python-flavoured predicate cannot see. (The `integer` branch of the same function *does* exclude `bool`; the `number` branch does not — the asymmetry is the bug, and it is the kind of bug that survives code review because both branches "look right".) The repair is to test the JSON lattice explicitly, not Python's: `not isinstance(v, bool)` before any numeric check.

## Closure: the default is "extra keys allowed"

The JSON Schema spec allows properties not listed in `properties` unless `additionalProperties: false` is set. Every provider's strict mode therefore *injects* that `false` everywhere, and every hand-written schema that omits it is looser than its author believes. This is why the closure family is mandatory in a validator rather than optional: without it, `{"product": "x", "price": 1, "in_stock": true, "internal_cost": 12}` validates cleanly and the leak is silent. It is also why Anthropic rejects `additionalProperties` set to anything other than `false` — the tier's guarantee is defined over a *closed* object.

## The retry loop (Instructor) and what it costs

```python
client = instructor.from_openai(OpenAI())
product = client.chat.completions.create(model=..., response_model=Product, max_retries=3, messages=[...])
```

On a `ValidationError`, Instructor serialises the error and sends it back as conversation context — "your output failed these checks, fix it" — and resamples, up to `max_retries` (the docs' example uses 3). Rohit: *"If the first attempt fails validation, it sends the errors back to the model as context and asks it to fix the output. This works with any provider, not just OpenAI."*

Three properties worth stating plainly:

1. **It repairs, it does not guarantee.** The terminal state after exhausting retries is a failure the caller must handle; the loop does not converge, it just tries again.
2. **It can mutate the data.** Attempt 2 is a new sample conditioned on an error message, so a value that was right in attempt 1 can come back different — which is exactly the *consistency* problem the lesson's intro names ("The retry sometimes produces different data"). Anything downstream of the extraction inherits that non-determinism.
3. **It is the seam where syntax and subset failures get fixed.** Which is why it belongs to the third of three guards, not to all of them.

## Three guards for three failure classes

| Failure class | Guard | Who owns it |
|---|---|---|
| syntax / grammar | JSON mode, or masking, or Instructor's retry | the decoder or the SDK |
| **schema subset mismatch** — you asked for `minimum: 0`, the provider sent a schema without it | a client-side validator against the **original** schema, after the provider's transform | **you** |
| semantics — right type, wrong value | an eval harness over labelled cases, cross-field checks, re-extraction agreement | **you** |

The middle row is the one that surprises people: `client.messages.parse()`-style SDK helpers *revalidate* locally after transforming the schema, precisely because the guarantee held only over the transformed copy. Rohit's "No retries needed. No validation needed." is true of the syntax class under strict mode and overstated for the subset class; the page on [[Structured Outputs (JSON contract)]] keeps the disagreement visible.

## Open questions

- Does a single `max_retries=3` loop reliably converge for a **semantic** failure (a hallucinated value)? It cannot — the error message says nothing about the document — but the number of pipelines that still try is the lesson's practical warning. Unattacked; it is the row-5 attack (`requires: row 4 closure`).
- Where should the validator live when the schema is generated from a Pydantic model *and* transformed for the provider — validate against the model (authoritative) or the sent schema (what the grammar enforced)? Standard answer is the model; not yet discussed with the learner.
- `oneOf` (exactly-one) vs `anyOf` (at-least-one) as a discriminated-union pattern, and why OpenAI rejects a root-level `anyOf` — banked as an exercise from Rohit's Exercise 1.

## Sources

- `raw/sources/2026-11-09 - structured-outputs - rohit.md` — Step 1 validator, Step 2 model→schema converter, Step 4 validate-and-retry pipeline, `## Use It` Instructor section.
- `raw/sources/2026-11-09 - structured-outputs - instructor.md` — retry defaults (`max_retries = 3`), `ValidationError → context` loop.
- `raw/sources/2026-11-09 - structured-outputs - jsonschema.md`, `… - jsonschema-object.md` — the spec: `additionalProperties` default, type lattice, keyword families.
- `raw/sources/2026-11-09 - structured-outputs - openai.md`, `… - anthropic-structured.md`, `… - anthropic-tool-use.md` — subset rules, SDK transform + revalidation, stripped constraints.
