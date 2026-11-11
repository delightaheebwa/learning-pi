<!-- provenance: status=synthesis (`## My understanding` block status=learner-note) | source=raw/sources/2026-11-09 - structured-outputs - rohit.md (Step 3 simulator) + outlines-paper.md + outlines-github.md + xgrammar.md + lmql.md + guidance.md + openai.md + anthropic-structured.md | verified-by=— (review gate pending; the 2026-11-10 v2 and 2026-11-11 v3 additions are unreviewed) | date=2026-11-11 -->

# Constrained Decoding (parser-state masking)

**Insight:** at every step the sampler does not pick from the whole vocabulary — the decoder asks a **parser** *"given the state I am in, which tokens keep the string inside the grammar?"*, sets every other token's probability to **zero**, and renormalises over the survivors. The answer is a property of the **state transition** (state × token → new state), not of the string's last character. So "masking" is not "check the output afterwards" and not "look at the tail of the prefix": it is a lookup in a machine that has been reading the prefix all along and remembers what it has not finished. Rohit's own Step-3 simulator is a *last-character rule*, and the whole discrimination this page exists to teach is **rule vs decider** — the rule happens to be right at most structural positions and is wrong at exactly the positions that matter: a value that just closed, a literal in progress, and a schema that is still missing a required key. **2026-11-10:** that discrimination closed, and the same page now carries the per-rung answer to *which rung kills an out-of-enum string* — the masking rung deletes it before the sampler, the prompting rung only lowers its probability. **2026-11-11:** the state is not only flags. `minItems`/`maxItems` need a **counter** of items emitted in the current array — numeric state, not a boolean — because the flag tuple is literally identical at positions where `]` legality differs.

## My understanding

> status=learner-note — the learner's own words, verbatim, preserved in order. Never paraphrased, polished, or merged below. The first three are in-session repair fragments from 2026-11-09 (that session paused before a v2 was captured); **v2** was added 2026-11-10 from the resumed session and is scoped to the enum rung and the pipeline order; **v3** was added 2026-11-11 and is scoped to the array-length counter. None of it is polished: the evolution scar is the point.

**Fragment 1 — the flag read** (at `{"product": "in_stock": tru`, after one delivered nomenclature patch):

> "the flag which is up is “a boolean in progress“"

**Fragment 2 — the decider side** (after the ladder repair; the phrasing fuses the model-distribution layer in and was corrected the next turn):

> "we simply hand the sampler e. … in this scenario, it is just e that has high probability. Otheriwse the rest are masked."

**Fragment 3 — the rule side** (derived correctly mid-session, then fused again):

> "the else part catches u. the rule gives the sampler ["any"] hence at that point tht llm is free to pick whatever has high probability from the distribution at that point."

**Annotation (the AI's, not the learner's words):** fragment 2 is *right about the masked set* and *wrong about the reason* — `e` does not have "high probability" because the model likes it; it has **all** the probability because everything else was zeroed and the survivors were renormalised. Fragment 3 is *right about the rule* — `["any"]` really is what Rohit's simulator returns at `tru` — and is the correct entailment the learner produced that day. Keeping both fragments is the point: the fusion between the three layers (flag layer, rule layer, distribution layer) is the live gap, and the closing fresh-surface check on it **failed** (see `## What is still open`).

**Difficulty readout carried with the fragments (not learner words):** the repair ladder consumed R3+ source returns on this gap and the spend exceeded budget — the diagnosis regime (last-char rule internals) sat over the edge for self-repair. Recorded as a difficulty signal, not as a learner failing.

**Version 2 — the enum seam and the pipeline order** (2026-11-10, resumed session; verbatim. This is a *patch*, not a consolidation of the page — it covers the enum rung and the order of the pipeline only).

*The masking-rung chain* (enum `["in_stock","out_of_stock","preorder"]`, off-enum candidate `"available"`):

> "constrained decoding masks \"available\" and hence high probability for \"in_stock\", \"out_of_stock\", \"preorder\" to be sampled from. constrained decoding is the one that hands the valid distribution to the sampler"

*The prompting rung, first attempt* (graded `fail`, `[miss: structural]`, repaired by perturbation):

> "the prompt lowers \"available's probability"

— patched in-session to **lowered ≠ zero**, so the sampler can still emit it. The component that would have zeroed it — **FSM/CFG** — is the one this rung does not have, and the learner named it in their own v1 vocabulary.

*The pipeline order* (after resolving a clash with their own earlier words):

> "raw distibuton → constrained decoding(fsm/cfg) → sampler"

*The no-op argument* for putting the zeroing anywhere after the sampler:

> "its zeroing wouldnt be worth anything since the impure distribution has already been sampled from."

**Annotation around v2** (the AI's, not the learner's words): the pipeline claim is the one that fixed the session's worst slip. "it sits after the sampler" contradicted the learner's own "hands the valid distribution to the sampler", and the no-op sentence above is the reason the contradiction matters — a mask applied after sampling deletes nothing. Two other slips in this stretch were **agent swaps**, not model gaps ("the sampler can still mask it to zero"): the sampler samples, the decoder masks.

**Version 3 — the counter** (2026-11-11; verbatim, in the order the session produced them. Scoped to array length: what the enforcing mask must carry for `minItems`/`maxItems`).

*Failed candidates first* (each graded fail, each narrowing the gap):

> "it has to be tracking the flags and the schema"   (tagged `sure`)

> "it is tracking ]"

> ", vs ] is the difference"

*The patch, and the fresh-surface answer that closed it* (`maxItems: 2` after item 2):

> "the counter says 2 which means , is invalid while ] is valid"

**Annotation around v3** (the AI's, not the learner's words): the three failed candidates share one shape — each names a **token** (or a token pair, or the flag tuple) where the answer is a **property of the prefix**: how many items this array has emitted so far. `]` had not been emitted at any of the counterexample positions, so "it is tracking `]`" is circular; the flags really are identical there, so "flags and the schema" cannot be the whole state. The patch is one clause — *a number, not a boolean* — and it is the first place in this branch where the model needed state that is neither a flag nor a set of literals.



## The decider, spelled out

The parser carries a state; the state answers one question per step. For a JSON-schema grammar the state is (at least) this tuple:

| Component | Values while scanning a prefix | What it decides |
|---|---|---|
| `in_string` | open / closed | whether a `"` **closes** a string or **opens** one — and therefore whether the characters inside may be letters at all |
| `expect` | `key-or-close` · `colon` · `value` · `separator-or-close` | which punctuation is grammatical *next* (`{` → key or close; after a key → `:`; after `:` → a value; after a value → `,` or `}`) |
| `required_left` | the set of required properties not yet written | whether the object may close at all — the flag that makes `<EOS>` or `}` illegal while `in_stock` is still missing |
| `literal` | `t` / `tr` / `tru` · `f` / `fa` / `fal` / `fals` · `n` / `nu` / `nul` · number-in-progress | which single character continues the literal; whether `.`/`-`/`e` are legal |
| `depth` / stack | array/object nesting | which closer is legal |

**The decider's rule:** legal set = `{ t ∈ V : δ(state, t) is defined }`, where `V` is the tokenizer's vocabulary and `t` is a **multi-character string**, not a character. Two consequences fall straight out — the legal set is a *set of tokens*, and each accepted token **advances the state**, so the next question is asked of a new state, not of the new suffix.

**The lesson's rule** (`raw/sources/2026-11-09 - structured-outputs - rohit.md`, Step 3 `next_valid_tokens`) is a much simpler machine: `json.loads` the prefix; if it parses, return `["<EOS>"]`; otherwise switch on `last_char` and return a *category list* — `['"', "}"]` after `{`, `['"', "0-9", "true", "false", "null", "[", "{"]` after `:`, `["a-z", '"']` after `"`, `["0-9", ".", ",", "}", "]"]` after a digit, and `["any"]` in the `else` branch. It is a **simulator for teaching**, and it is honest about only one thing: what a *character* may be. It has no `required_left`, no `in_string`, and no `literal` counter.

## Why the rule cannot be the decider — three breakdowns

These are the exact probes this session was built on. Each one is a position where the last character does not determine the state:

| Partial prefix | Rohit's rule returns | Actually legal | What the rule cannot see |
|---|---|---|---|
| `{"product": "Sony"` (a value just closed) | `['a-z', '"']` | `,` or `}` | the string **closed** — `in_string` flipped; letters are no longer "inside a string", they would follow a complete value |
| `{"product": tru` | `["any"]` | `e` (only `e`) | `literal` state — two of five characters consumed |
| `{"product": "Sony", "price": 348}` | `["<EOS>"]` (it parses!) | `,` (then `"in_stock"`) — **not** EOS | `required_left` is non-empty; the prefix parsing is not the schema being finished |

And the discriminator the session's closing check landed on, at `{"product": "Sony", "price": 348}`:

- the **rule** early-exits on `json.loads(prefix)` succeeding — "it parses, so we are done, EOS";
- the **decider** first reads `expect = separator-or-close` (the number just closed) *and* `required_left = {in_stock}` — so the legal set is `,` **only**; `}` and `<EOS>` come back into play only once `required_left` is empty.

Both sides agree on the character `,` at that position *for different reasons*, which is exactly why the item discriminates: the reason is the thing being graded. The closing check marked the `,` correct and the two reasons wrong.

## The mechanism: mask, then renormalise

For a state `s` and logits `z ∈ R^|V|`:

```
p(t | s) = softmax( z + m_s )_t     where  m_s[t] = 0 if δ(s,t) defined, else −∞
```

- The masked token's probability is **exactly 0**, not "small" — this is why "the rest are masked" is stronger than "the model is less likely to do it".
- Renormalisation is over the survivors, so the surviving distribution is a genuine distribution; the argmax often *stays* the same token the unconstrained model would have picked, which is the unglamorous truth about masking: it is a safety net, not a rewriter.
- It deletes arms from the distribution rather than shrinking them — the same vocabulary as the learner's earlier model of prompting (see [[Prompt Engineering]]: vague prompt → mass split across arms; precise prompt → arms deleted). Masking makes the deletion *hard*: an arm that would leave the grammar has probability zero no matter how attractive the model finds it.

## Characters vs tokens: the indexing problem (why this is engineering, not a one-liner)

The grammar is defined over **characters**; generation emits **tokens**. One token can carry several structural characters (`":{"`), and one character can straddle a token boundary. Validity is therefore a property of the transition, and the naive implementation — for each step, test all `N ≈ 100k+` vocabulary tokens against the automaton — is `O(N)` per token generated:

- **Outlines** (Willard & Louf 2023) compiles the schema/grammar into an **FSM** and then builds an **index over the vocabulary**, so the set of non-zero-probability tokens at a state is retrieved in `O(1)` average time instead of rescanning the vocabulary.
- **XGrammar** handles **context-free** grammars: a byte-level **pushdown automaton** (one stack per recursive rule; parallel stacks when the grammar is ambiguous), then splits the vocabulary into **context-independent** tokens — decided by the stack *top* alone and precomputed into an adaptive token-mask cache — and **context-dependent** tokens that need the whole stack at runtime. For JSON grammar on Llama-3.1 the context-dependent share is **under 1%** (1134 of 128k tokens), and end-to-end overhead is **under 40 µs/token** for JSON Schema/CFG-JSON (< 200 µs for XML and Python DSL).
- **LMQL** is the soundness counterpart: constraints are evaluated **eagerly and partially**, and where a constraint's satisfaction is not decidable from the prefix the mask is **over-approximate** — the decoder may still need **backtracking**, because "this token might still be fine" and "this token is fine" are different claims.
- **Cost is a real constraint, not a footnote.** Anthropic's native tier compiles the schema into a grammar artifact on first use, caches it for 24 hours, and rejects excessive complexity with `400 "Schema is too complex for compilation"` or a 180-second compile timeout. Compile-time cost is why a schema-shape change (not a `name`/`description` change) invalidates the cache.

⚠️ **Source-reading note (a real error in the lesson's Further Reading):** Rohit's blurb for XGrammar says the paper reports masking "at ~100 ns / token". The paper reports **under 40 µs / token** — a ~400× gap, i.e. a nanosecond-vs-microsecond unit slip. Read the source, not the citation, when the number is the point.

## What masking cannot do

It enforces the **grammar**, which is exactly the class of failure it was built for: syntax, missing required keys, extra keys when `additionalProperties: false`, enum membership, array length where the provider enforces it. It says nothing about the **value**: a grammar has no opinion about whether `348` appears in the document being extracted. And it only enforces the subset the provider accepts — a constraint silently dropped before compilation (Anthropic's `minimum`/`maxLength`) is invisible to the mask. Both limits are spelled out on [[Structured Outputs (JSON contract)]] and [[JSON Schema Validation & Retry (Pydantic + Instructor)]].

## Where the mask sits — the enum seam, rung by rung

The enum is the cleanest place to see that the ladder is *where the constraint acts*, not a list of four equal tricks. Same schema (`in_stock` ∈ three legal strings), same off-enum candidate (`"available"`):

| Rung | What happens to `"available"` | Why | Source |
|---|---|---|---|
| Prompt-based ("respond in JSON", "use one of these three values") | its **probability is lowered**, not zeroed — it remains samplable | a prompt re-weights the distribution; it cannot delete an arm | rohit: *"Prompt-based approaches do not"* prevent enum confusion |
| JSON mode | nothing specific — the text still only has to *parse* | no schema, so no allowed set | — |
| Schema mode / constrained decoding | **masked to exactly 0 before the sampler runs**, so the survivors are the three legal strings and the renormalised mass sits on them | the enum is a finite language; membership is decidable from the grammar | rohit: *"Good constrained decoding prevents this"* |
| Validator / Instructor retry | catches it **after** generation and repairs by resampling — legality, not truth; costs a call; can return different data | the validator's oracle is the schema | [[JSON Schema Validation & Retry (Pydantic + Instructor)]] |

## Pipeline order — why the mask must precede the sampler

The learner's own words, 2026-11-10: **"raw distibuton → constrained decoding(fsm/cfg) → sampler."**

The order is load-bearing, and the no-op argument proves it: **"its zeroing wouldnt be worth anything since the impure distribution has already been sampled from."** If the zeroing sat after the sampler, the token would already be drawn from the unrestricted distribution and deleting it afterwards changes nothing about what was emitted. So masking is not a post-filter, a repair, or a validity check on the *output*: it is a modification of the *input to the sampler*. That is also why an off-enum string is impossible at the masking rung rather than unlikely — the arm does not exist by the time the sampler looks.

⚠️ Two agent confusions this seam produces, both observed and both repaired in-session (2026-11-10): *"the sampler can still mask it to zero"* (the sampler samples; the decoder masks) and *"it sits after the sampler"* (which the learner's own "hands the valid distribution to the sampler" already refuted).

## Array length: why flags × schema is not enough (2026-11-11, CLOSED)

Rohit's caveat — *"Schemas support minItems and maxItems, but not all providers enforce them at the decoding level"* — hides a state question. Take `{minItems: 3, maxItems: 5}` on an array and look at three positions:

| Position | `in_string` | `expect` | `required_left` | `literal` | Legal set for the next token? |
|---|---|---|---|---|---|
| after item 1 | closed | separator-or-close | unchanged | none | `,` **and** `]` — too short, so `]` is illegal |
| after item 2 | closed | separator-or-close | unchanged | none | `,` **and** `]` — too short, so `]` is illegal |
| after item 3 | closed | separator-or-close | unchanged | none | `,` **and** `]` — **`]` just became legal** |

Every flag in the tuple is identical at all three positions, and the legal set changes underneath it. No boolean can express that, so the mask needs one more piece of state:

- a **counter** of items emitted in this array;
- `]` is legal **iff** `count ≥ minItems`;
- `,` is legal **only while** `count < maxItems` (which is also why the `maxItems` direction is the cleanest probe: `"the counter says 2 which means , is invalid while ] is valid"`).

The learner's own summary of the step: *"a number, not a boolean"*. Two consequences worth keeping:

- **It is state, not a check.** The counter lives in the mask's own bookkeeping — incremented on each completed item, read before each separator/close decision — so it is part of what makes `"the rest are masked"` true, not an after-the-fact review of the emitted string.
- **Its existence is a provider property.** A keyword the provider does not compile never becomes grammar state, so the counter is only there when the provider compiled `minItems`/`maxItems` at all. That is the bridge to [[Structured Outputs (JSON contract)]] and [[JSON Schema Validation & Retry (Pydantic + Instructor)]]: where the counter exists the validator is idle; where it does not, the validator is the only catcher. See the session-3 chain on the first of those pages.

The counterexample trap is what separated a real state model from a slogan: five candidates failed before the patch (flags × schema, "tracking `]`", "`, vs ]`"), and the patch then held on a fresh surface in the untouched `maxItems` direction.

## What is still open

- **Row 4 repair is CLOSED (2026-11-10).** The resumed session ran a **new** fresh-surface both-sides check on the decider-vs-rule discrimination and then the own-words restatement of *"flags × schema → mask + renormalise, ≠ the last-char rule"*. The one closing item that still failed tested **Build-It** grains (`part 1 execution-incomplete (garbled set, question-side not assertion-side); part 2 cue/unread-source`) — outside the learner's declared read scope — so it is **banked out of scope** and must not be re-issued. Ledger for this concept after 2026-11-10: 21 graded items, 6 pass / 15 fail, `interval_index` 1, `consecutive_wrong` 0, `next_review` 2026-11-17, mastery 0.50 advisory. **2026-11-11: the array-length seam closed on this page's state** — six graded items on the counter question (2 pass / 4 fail), including the `maxItems` fresh-surface pass that closed it. Ledger after the session: **27 graded items, 9 pass / 18 fail, `interval_index` 2, `consecutive_wrong` 0, `next_review` 2026-11-25**, mastery 0.50 advisory. The model now carries **flags + counter**.
- **The flag set has never been run closed-book as a whole.** `in_string`, `expect`, `required_left`, `literal` were each pressed separately (one pass, several fails); no item has yet asked for the full tuple at one position — and the counter now sits beside the flags, so the state that has never been run as one object is **flags × counter**, not just the flags.
- **Calibration.** Confidence was `sure` at the spine check and the first predict probe, yet 9 of 11 attack/check items failed — an illusion-of-competence signal recorded in `🧯 Mistakes.md`. **2026-11-10 second data point:** both row-5 catchability items were tagged `hunch` and both **passed** — the first evidence in the other direction (hedged confidence tracking the item). Whether it holds once the array-length seam and the two unlisted failure modes raise the difficulty is still unanswered, and the flags tuple has not been run closed-book at all. **2026-11-11 — third data point, and it complicates the picture:** across the session's 24 graded items, `sure` went 4 pass / 3 fail, `hunch` 1 pass / 6 fail, untagged 3 pass / 7 fail. Both `sure` tags that closed a repair were earned (the counter, the two-blank path fill); one `sure` on the half-answered invoice check was not. Hedged confidence is tracking the items better than unhedged confidence, but neither is calibrated enough to trust as a substitute for the trace.

### Row-4 repair log (2026-11-09, reconciled from the Tutor's lesson file)

What was tried on this gap, in order, so the resume does not repeat it:

- **Predict probe** at `{"product": "Sony"` — predicted `,` / `}` (the decider's answer) where the rule returns `['a-z','"']`; the schema-side read was correct.
- **Mechanism press** — the same trailing `"` demands `:` after a key and `,` after a value, so legality is not a function of the tail.
- **Three schema-only repairs failed** ("next token distribution" → "keys and values" → naming rounds) → **repair mode entered**: a structural gap has nothing to cue.
- **Repair step 1 — flag bookkeeping** over the emitted prefix: landed after 4 naming rounds + a nomenclature patch; re-owned by the learner as *"a boolean in progress."*
- **Repair step 2 — mask + renormalise** from flag-state × schema-progress: the decider side landed (*"we simply hand the sampler e … the rest are masked"*).
- **Contrast rounds 2/2 fail** — the three layers fused again (*"the flag is any; e has high probability"*).
- **Closing fresh surface 1/3** at `{"product": "Sony", "price": 348}` — `,` right, both reasons taken from the rule.

Ladder spend exceeded budget (the branch table and `else → ["any"]` were handed over) — a **difficulty signal** about the diagnosis regime, not a learner verdict. Resume rung: a **new** fresh surface after a flags × schema mask re-cap, then an own-words restatement of *"flags × schema → mask + renormalise, ≠ the last-char rule"*. **Executed 2026-11-10 and CLOSED** — the resumed session ran exactly that rung (new fresh surface → own-words restatement), and the one item that still failed tested Build-It grains outside the learner's declared read scope (banked out of scope, never to be re-issued). See `## What is still open`.

## Sources

- `raw/sources/2026-11-09 - structured-outputs - rohit.md` — the spectrum's decoding rung, the Step-3 `next_valid_tokens` simulator and its `["any"]` catch-all (the rule this page contrasts).
- `raw/sources/2026-11-10 - structured-outputs - rohit.md` — the 2026-11-10 re-fetch; its Concept section's enum and pipeline wording ("Good constrained decoding prevents this. Prompt-based approaches do not.") is the source for the per-rung table above.
- `raw/sources/2026-11-09 - structured-outputs - outlines-paper.md`, `… - outlines-github.md` — FSM compilation + vocabulary index, `O(N)` naive baseline.
- `raw/sources/2026-11-09 - structured-outputs - xgrammar.md` — byte-level PDA, adaptive token mask cache, <1% context-dependent tokens, <40 µs/token, parallel stacks.
- `raw/sources/2026-11-09 - structured-outputs - lmql.md` — eager partial evaluation, over-approximate masks, backtracking as the completeness price.
- `raw/sources/2026-11-09 - structured-outputs - anthropic-structured.md` — compile cost, 24-hour grammar cache, complexity errors.
