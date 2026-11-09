<!-- provenance: status=synthesis (`## My understanding` block status=learner-note) | source=raw/sources/2026-10-28 - prompt-engineering - rohit.md + anthropic.md + cot-wei.md + openai.md + dair.md + dair-cot.md + dair-settings.md + prompt-engineer.md + claude-best-practices.md + johnny.md | verified-by=— (review gate pending) | date=2026-10-29 -->

# Prompt Engineering

**Insight:** a prompt executes nothing — it conditions each next-token distribution. Every ambiguity the text leaves is a fork the model must sample from, so a vague prompt spreads probability mass over many candidate continuations while a precise one deletes arms and piles the same mass onto a few survivors. "The model takes your prompt literally" therefore means the model takes *the conditioning the text implies* seriously, not that it obeys instructions. The other half of the discipline is the ruler: "desired quality" is only measurable against a harness that holds a fixed case set **with human-authored expected outputs** and re-runs on every prompt change, so a regression on an already-passing case is visible before the next tweak ships — and the ruler must sit *outside* the system being judged, since a model grading itself re-authors "what is good" every run. Narrowing is not unconditionally safe either: an over-specific role points the conditioning at an intersection with little matching training text (confident fabrication), and chain-of-thought below ~100B pollutes its own context with fluent-but-unfounded steps that later steps then condition on, so one-shot wins there. The headline "10–40%" CoT payoff is scale-conditional, not a flat bonus.

## My understanding

> status=learner-note — the learner's own words, verbatim, preserved in order. Never paraphrased, polished, or merged below. Versions are the learner's; annotations between them are the AI's.

**Version 1** — 2026-10-28, first closed-book model (handwritten notes, transcribed and confirmed; one unreadable word filled in by the learner as "clarity"; confidence `sure`):

> "Prompt engineering is very much alive. It has just become table stakes for all AI engineers. The usual structure is role, context, constraints, output. Prompt engineering consists of clarity, patterns, anti-patterns, context window, constraints, role, output format. Models take your prompts literally — here we need to be precise. Prompt engineering is the process of tweaking the prompt in order to get the desired quality results."

**Breaking case 1** (annotation — not the learner's words, recorded between versions so the evolution scar stays visible):

- Two mechanism presses on *"models take your prompts literally"* produced only circular chains — first a "generic prompt → generic output" restatement with no distributional middle, then the banned word reused with a model-as-decider agency picture. Both failed; the first was tagged `sure`, the illusion-of-competence signal.
- The row-4 counterexample: a prompt v1 that passes article 1, a v2 that fixes article 2 while regressing article 1, a v3 that fixes article 1 and regresses article 2. Every step satisfies the v1 definition *as written* — "tweaking the prompt in order to get the desired quality results" on the case in front — yet the loop oscillates forever and nothing in the definition can register that v2 is worse than v1.

**Version 2 — partial, NOT formally captured** (row-3 middle patched on a fresh surface, 2026-10-28; the learner's own restatement, verbatim):

> "A leaves room for more arms and more probability mass is more split amongst those arms leading to generic output since the next tokens are condtioned to come from a wider space. B leaves less room for more arms and less probability mass is split amongst those arms and is piled on to a few leading to more precise output since the next tokens are conditioned to come from a narrower space. Models take prompts literally means that they take what conditioning of the next token distribution they imply seriously."

**Breaking case 2** (annotation, 2026-10-29): that partial patch covered the mechanism only. Two load-bearing pieces were still absent — the ruler (how "desired quality" is measured across versions) and any failure regime (where narrowing *hurts*). Both were re-attacked on a fresh surface the next day: the harness had to be assembled from its parts, and "narrowing is always safe" had to survive an over-specific role and a small model. The full model was then captured closed-book as v2 below. The partial version above is kept because it is what the learner actually held on 2026-10-28 — v2 did not exist yet.

**Version 2 — formal capture** (2026-10-29, closed-book graduation restatement; typos and the trailing tool-choice sentence preserved as written):

> "So, what's the problem with prompt engineering? The problem is that to get good, non-generic outputs out of these models, we need to do some prompt work. That prompt work is prompt engineering—the process of tweaking prompts to get the desired quality of response. That is measured based on the drift between the output we get and the output we expected or wanted. The mechanism of prompt engineering is that when you send a prompt, it conditions the models for generation. For each token it makes, and for each focus point, it distributes the probability mass across various forking paths. If the prompt is vague, it will distribute the probability mass more evenly over those paths; otherwise, the mass is concentrated over just a few choices. Now, why do we need a measurement layer like a ruler and a harness? When we are creating more than one prompt version, we need a way to track the drift and track progress. If version one gives a bad output, we need a way to measure whether version two will make an even worse output or make it better. That's why we need the measurement layer when we want to make multiple prompt versions. For just a one-off prompt, we don't need it. However, there are two failure regimes when comparing versions like V1, V2, and V3. Failure regime number one: For chain-of-thought, when you tell the model to think step-by-step, it is ideal not to do that for models with less than approximately 100 billion parameters. That actually hurts their performance. The generated paths for certain tokens can be fluent but unfounded, and the next generation of paths will just be polluted by this previous context, which ruins the rest of the response. So it's better for smaller models to generate in one shot. The second failure regime is when we make our prompt too specific—like telling the model it is an expert in a very, very specific niche with 20 years of experience. Because the model has little data on that, it will hallucinate because it doesn't know what to tell you and will just make things up. So when we get too specific, problems arise as well. What neighboring technique would I reach for besides the ruler to measure drift? i'd reach for the harness."

**Source framing:** the curriculum keeps the same mechanism in output terms — "The specific version constrains the output space. Fewer valid outputs means higher probability of getting the one you want." — and never names the sampling loop; v2 supplies the middle the curriculum leaves implicit (per-token/per-focus-point mass across forking paths).

**Missing pieces still visible in v2** (named by the naive-student clone, not filled in here): (a) no *separator* between "concentrated, therefore good" and "too specific, therefore fabrication" — the data-support criterion ("very little high-quality text at that intersection") exists in the sources but is not in the model as an advance test; (b) no statement of whether the two failure regimes compound or merely coexist; (c) no third option between "too vague" and "too specific" when a safe prompt still returns generic output. All three are banked for `/review`.

## Source framing: the two-distribution picture

The curriculum states the mechanism in output terms rather than sampler terms, which is exactly where v1 stalled:

> "The first prompt activates a generic distribution of marketing emails in the model's training data. The second activates a narrow, high-quality slice. Same model. Same parameters. Wildly different outputs." — `2026-10-28 - prompt-engineering - rohit.md`

> "The number one prompt engineering mistake is being vague when you could be specific. Every ambiguity in your prompt is a branch point where the model guesses. Sometimes it guesses right. Sometimes it does not."

> "The specific version constrains the output space. Fewer valid outputs means higher probability of getting the one you want."

**External angle** — the mechanism the learner assembled to make those sentences true (their words in the "Version 2" blocks above): at an unresolved fork the mass splits across all plausible candidate arms and the autoregressive loop samples from that split (respecting the split weights, not uniform randomness); a precise instruction deletes arms, so the same mass concentrates on the survivors. This is the same distribution the model already knew from sampling — see [[Sampling from a Language Model]] and [[Softmax Function]]; a prompt is conditioning applied to that object, never a program handed to an executor.

## Anatomy and the core pattern set (solid at triage)

- Three message slots, in priority order: **system message** ("the invisible hand. It sets the model's identity, behavioral constraints, and output rules. The model treats this as highest-priority context."), **user message** ("the task"), and **assistant prefill** ("the secret weapon" — start the assistant turn with a partial string and the model continues from there). Prefill availability is provider- and version-bounded (see the disagreement note below).
- The curriculum's learning objective names the pattern set the learner already held: "Apply the core prompt engineering patterns (role, context, constraints, output format) to transform vague requests into precise instructions".
- Role prompting, with its limit: "The more specific the role, the narrower the distribution, the higher the quality. But there is a limit. If the role is so specific that few training examples match, the model will hallucinate."

## The measurement layer: the ruler and the harness (repaired + closed 2026-10-29)

Anthropic puts the ruler *before* the tweaking, and the lesson's own build objective is a harness:

> "This guide assumes that you have: A clear definition of the success criteria for your use case; Some ways to empirically test against those criteria; A first draft prompt you want to improve. If not, spend time establishing that first." — `2026-10-28 - prompt-engineering - anthropic.md`

> "Not every success criterion or failing eval is best solved by prompt engineering. For example, you can sometimes improve latency and cost more easily by choosing a different model."

> "Implement a prompt testing harness that evaluates prompt changes against a set of expected outputs" — Rohit, learning objectives; the harness code section sits in the curriculum's "build it" part, past the learner's read point.

**The mechanism, in the learner's words** (2026-10-29, verbatim): *"The prompt harness holds the set of expected outputs and the outputs we actually received, allowing us to compare the two sets for any regression. When we make a change, the prompt runs."* Deployment, same day: *"You compare what you got against what you expected"* on a v5 that silently dropped an article's numbers — *"it degraded the quality of the response."*

Two distinctions the repair produced, and one detour it killed:

- **Determinism ≠ measurement.** Temperature 0 pins the top token on every step, so a run is repeatable; it says nothing about whether the output is good. "Test with temperature=0 first to isolate prompt quality from sampling randomness" / "Temperature=0.0 makes the output deterministic -- the same input produces the same output every time. This is essential for testing and reproducibility." Repeatability is a precondition of comparing, not the comparison.
- **The scorer is not the ruler.** The expected outputs must be human-authored and held outside the system being judged. A model grading each version at temperature 0 re-authors "what is good" every run — the v1/v2/v3 oscillation one level up — and a bigger or different scorer does not fix it; the still-missing part is *what the human actually wants* (learned on the sabotage battery, 2026-10-29).
- **Killed detour:** "the more the probability mass is piled onto a few arms, the better the output" — concentration measures how hard the model was squeezed, not whether the output is right; the learner's own banked temp-0 verdict is what refuted it.
- **When it is needed:** more than one prompt version. A single one-off judgment event needs no fixed anchor; stacked versions do, or "did this get better?" is undecidable. See [[Evaluation Protocol]] for the general shape.

## The two failure regimes (repaired + closed 2026-10-29)

Narrowing is not unconditionally safe. Both regimes are in the sources, and both are now in the learner's model:

- **Regime 1 — too-specific roles fabricate.** "If the role is so specific that few training examples match, the model will hallucinate. 'You are the world's foremost expert on quantum gravity string topology' will produce confident nonsense because the model has very little high-quality text at that intersection." The condition is **data support**, not wording: a persona whose described intersection has little matching high-quality training text leaves the mass on few, likely-wrong arms and the model makes things up rather than narrowing to the right arm.
- **Regime 2 — chain-of-thought can hurt on small models.** "chain-of-thought prompting does not positively impact performance for small models, and only yields performance gains when used with models of ∼ 100B parameters"; "models of smaller scale produced fluent but illogical chains of thought, leading to lower performance than standard prompting"; "chain of thought actually hurts performance for most models smaller than 10B parameters" (Wei et al.). **Mechanism (learner's words, 2026-10-29):** "the next step is built on that shaky foundation … pollutes the rest of the response" → "it would be better for it to answer in one shot" — a fluent-but-unfounded step becomes the conditioning context for every later step, so the error compounds instead of being corrected.

## ⚠️ Sources disagree — the CoT payoff is conditional, not a flat bonus

Both sides, verbatim, kept visible because the conflict is real:

- **Rohit (unconditional):** "Prompting the model to show intermediate reasoning steps, which improves accuracy on math, logic, and multi-step problems by 10-40%", and in Further Reading: "the foundational paper showing that 'think step by step' improves LLM accuracy by 10-40% on reasoning tasks".
- **Wei et al. 2022 (conditional on scale):** "chain-of-thought prompting is an emergent ability of model scale" — "That is, chain-of-thought prompting does not positively impact performance for small models, and only yields performance gains when used with models of ∼ 100B parameters." Table 1 still carries a −4.9-point case even at 137B (LaMDA on AQuA), so the gain is a regime average, not a guarantee.

This is a **real disagreement**, not a wording difference — a prompt-engineering model that only carries "CoT gives 10–40%" is broken at the small-model end.

**How the learner reconciled it (2026-10-29):** the 10–40% figure was scoped to "models greater than approximately 100 billion parameters", and below that line the pollution mechanism above makes step-by-step *worse* than one-shot. The reconciliation narrows Rohit's sentence; it does not delete the conflict — the unconditional phrasing remains false as written.

**Second disagreement (real, version-bounded):** assistant prefill — Rohit presents it as a general "secret weapon" ("Anthropic's API supports this natively", "no other major provider supports it natively"), while the Anthropic docs say "Requests with prefilled assistant messages to these models return a 400 error" starting with Claude 4.6 models. Treat prefill as a dated capability with a migration path (direct instruction, XML tags, structured outputs, tool calling), never a portable pattern. **Untaught so far — flagged, not resolved in the learner's model.**

## ⚠️ Source error — Rohit's "Why Johnny Can't Prompt" citation

Rohit's Further Reading links the paper to `https://arxiv.org/abs/2304.13529`, which resolves to an unrelated astrophysics paper. The cited work is Zamfirescu-Pereira et al., "Why Johnny Can't Prompt: How Non-AI Experts Try (and Fail) to Design LLM Prompts", CHI 2023, DOI `10.1145/3544548.3581388` (abstract saved as `2026-10-28 - prompt-engineering - johnny.md`; the publisher PDF is bot-blocked, so nothing from the body is synthesized). This is a citation error in the lesson, not a disagreement between theories; the paper's finding — non-experts prompt opportunistically rather than systematically, and overgeneralize — is consistent with the lesson rather than in tension with it. **Untaught so far.**

## Not yet taught (available as later attack material)

Temperature / top-p sampling mechanics (DAIR settings), the prefill availability contradiction above, Rohit's citation error above, PE2 meta-prompting and its limits (`prompt-engineer.md`), and the harness code section past the learner's read point. None of these were owed to the learner; they are attack material for a later lesson or `/review`.

## Open questions

- [x] **The eval layer (row 4):** closed 2026-10-29 — the harness is assembled in the learner's words and deployed on a fresh article; the scorer-is-not-the-ruler split closed the sabotage battery.
- [x] **The failure regime (row 5):** closed 2026-10-29 — both regimes named with their mechanisms and the scale condition.
- [x] Formal **v2 capture**: banked 2026-10-29 (entailment check + naive-student clone PASS + battery closed).
- [ ] **Clone blind spots (Mistakes row, `active`):** the too-specific threshold/advance test; whether the two regimes compound or coexist (open in the sources too); the vague↔specific middle. Priority drill for `/review`.
- [ ] **Prefill availability** and **Rohit's citation error** remain source-side flags the learner has not yet met.

## Related

- [[Sampling from a Language Model]] — the sampling loop a prompt conditions
- [[Softmax Function]] — where the next-token distribution comes from
- [[Token]] — the unit of the "narrower space"
- [[Evaluation Protocol]] — the general eval-first shape behind the harness
- [[AI Engineering from Scratch — Roadmap]] — the curriculum this lesson comes from
