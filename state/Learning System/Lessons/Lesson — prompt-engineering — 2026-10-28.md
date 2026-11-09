# Lesson — Prompt Engineering (Phase 11 L01, LLM Engineering)

**Date:** 2026-10-28
**Status:** Completed 2026-10-29 — all five triage rows closed; graduation complete (v2 captured, entailment check banked, naive-student clone pass, sabotage battery closed). Continuation record: § Resume session — 2026-10-29.
**Source:** https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/01-prompt-engineering (fetched live 2026-10-28; Scout digest `Learning System/.tmp/context-01a1823e-0f24-70c3-b793-e78c1d3019a9-prompt-engineering.json`, scout-audit PASS; 9 raw files under `Knowledge Wiki/raw/sources/2026-10-28 - prompt-engineering - *.md`)
**Flow:** [[FLOW:teach]] — learner-supplied material + handwritten notes
**Material read by learner:** the lesson up to the "build it" part (learner-reported)

## Material

- Lesson core: "Prompt engineering is not dead… What changed is that it became table stakes. Every serious AI engineer needs it."
- Intro frame: "every token you send is an instruction, and the model follows instructions literally. Write better instructions, get better outputs."
- Core pattern set: role, context, constraints, output format.
- Vague vs engineered prompt: "The first prompt activates a generic distribution… the second activates a narrow, high-quality slice." / "Every ambiguity in your prompt is a branch point where the model guesses." / "constrains output space. Fewer valid outputs means higher probability."
- Role prompting limit: "If the role is so specific that few training examples match, the model will hallucinate."
- Learning objectives include: "Implement a prompt testing harness that evaluates prompt changes against a set of expected outputs."
- Temperature/sampling section (learner has not read past "build it"): temp 0.0 = deterministic / top token; "Test with temperature=0 first to isolate prompt quality from sampling randomness."
- Externals: Anthropic (eval-first: success criteria + empirical tests + first draft BEFORE tweaking; "Not every success criterion or failing eval is best solved by prompt engineering"), Wei et al. (CoT emergent ~100B+, small models get *worse*), OpenAI (instructions parameter, developer>user priority), DAIR (temperature/top-p mechanisms), PE2 meta-prompting.
- Scout-flagged contradictions: assistant prefill availability (Rohit vs Anthropic docs — real, version-bounded); CoT benefit unconditional "10–40%" (Rohit) vs conditional ~100B (Wei et al.) — real; prompt-engineering scope (Rohit vs Anthropic) and role-mechanism wording — apparent.

## Learner model (v1) — verbatim, handwritten photo, transcribed + confirmed

> "Prompt engineering is very much alive. It has just become table stakes for all AI engineers. The usual structure is role, context, constraints, output. Prompt engineering consists of clarity, patterns, anti-patterns, context window, constraints, role, output format. Models take your prompts literally — here we need to be precise. Prompt engineering is the process of tweaking the prompt in order to get the desired quality results."

(The one unreadable word was filled in by the learner as "clarity." Confidence tag: **sure**.)

## Triage

| # | Claim (verbatim) | Bucket | Reason / evidence |
|---|---|---|---|
| 1 | "Prompt engineering is very much alive… table stakes for all AI engineers." | solid | matches source ("not dead… became table stakes") |
| 2 | "The usual structure is role, context, constraints, output." | solid | source names exactly these four as the core pattern |
| 3 | "Models take your prompts literally — here we need to be precise." | suspect → **REPAIRED (closed)** | vague — no mechanism; repaired via fork-arm/mass picture (see Repair mode) |
| 4 | "the process of tweaking the prompt in order to get the desired quality results" | missing → **REPAIRED + CLOSED (2026-10-29)** | no measurement layer: nothing says how "desired quality" is known; Anthropic puts success criteria + tests + first draft *before* tweaking |
| 5 | (absent) failure regime | missing → **REPAIRED + CLOSED (2026-10-29)** | model names no case where better-structured prompting hurts; sources contain two (CoT below ~100B hurts — Wei et al.; over-specific role hallucinates — Rohit) |

Attack order: 3 → 4 → 5. Dependency: 4 and 5 both required row 3's mechanism.

## Pre-attack prediction (row 3)

Prompt: "given p(next|context), no executor — what does your prompt text actually do to the output?"
Learner (verbatim): "i think my prompt text steers the model's next token choices for each token in the output from right left to right" — **correct** (conditioning each next-token distribution, left to right). Recorded as micro-check pass.

## Attacks (in dependency order)

### Attack 1 — row 3, mechanism press ("literally")

Prompt: vague vs precise instruction — what changes at the next-token distribution level, what shows up in output; and what does "taken literally" mean when nothing is executed?
- **Attempt 1 (verdict: FAIL, miss_class cue, confidence sure → illusion-of-competence signal):** "with vague tokens, it conditions the next token distribution in the direction of 'generic tokens' leading to a generic output while with precise tokens… more precise output. so to take your prompt literally would then mean that 'you asked with a generic request, i then gave you a generic response'…" — circular restatement, no distributional middle.
- Rung R3 (source return): "The first prompt activates a generic distribution… the second activates a narrow, high-quality slice." / "Every ambiguity in your prompt is a branch point where the model guesses."
- **Attempt 2 (verdict: FAIL, miss_class structural):** "a vague prompt leaves a lot of ambiguity unresolved for the model and hence it simply fills in the gaps with what is generic… a generic prompt activates a generic distribution" — banned word used twice; model-as-decider agency picture; no spread-vs-peaked middle.
- Push-down nudge: "a model that only computes a probability distribution — what is the stuff it fills gaps with? Name the currency."
- Learner: "tokens with the high probability of coming next in a generic response given the generic prompt" — named probability, still circled.

### Repair mode — row 3 gap (miss_class structural, tactic push_down) — CLOSED

- **Step 1/2 (Socratic, landed):** at a fork the instruction leaves unresolved, where does the mass go, what does the loop emit? Learner: "the probability mass splits. if context favors no candidate, the a token is chosen at random" — check PASS (graded). Sharpening given: the sample respects the split weights, not uniform randomness.
- **Step 2/2 (Socratic, landed):** precise instruction ("exactly 5 bullets, each with a number, no intro") — what happens to fork arms and mass? Learner: "it narrows the number of choices each of those arms has hence more mass piles up on fewer arms compared to other arms." — check PASS (graded); matches source "fewer valid outputs means higher probability."
- **Fresh-surface close (graded PASS):** new case, prompts A ("Summarize this.") vs B ("Summarize this article in exactly 3 sentences, past tense, no numbers, and end with the single most important takeaway.") — chain operated correctly on both.
- **Learner restatement (verbatim):** "A leaves room for more arms and more probability mass is more split amongst those arms leading to generic output since the next tokens are condtioned to come from a wider space. B leaves less room for more arms and less probability mass is split amongst those arms and is piled on to a few leading to more precise output since the next tokens are conditioned to come from a narrower space. Models take prompts literally means that they take what conditioning of the next token distribution they imply seriously."

### Attack 2 — row 4, counterexample trap ("tweak to get desired quality")

- **Prediction attempt (verdict: FAIL, miss_class careless):** "i guess the model produces something mediocre as you've said" — restated the setup; question restated for free.
- Learner: "the next move would then be to simply tweak again" — their definition operating; loop has no end, quality re-decided per run.
- **Counterexample:** v1 passes article 1 → v2 fixes article 2, regresses article 1 → v3 fixes article 1, regresses article 2. Every step satisfies the definition *as written* (desired quality on the case in front) yet the process oscillates forever and can never register v2 worse than v1. Asked: what is missing that would let it *see* the oscillation?
- **Attempt (verdict: FAIL, miss_class structural):** "its missing a way to measure success. so we should set temperature to zero and measure the quality." — diagnosis kernel correct; remedy conflated decoding determinism with a quality measurement.
- Push-down nudge: "what does temp 0 actually change about a run, and does flipping it change whether the output is good?" Learner: "it jsut makes the model pick the top choice in the next token distribution every time. flipping it i think wont change whether the output is good or not." — distinction landed (recorded micro-check pass). Lesson nuance banked: Rohit recommends testing at temp 0 to *isolate prompt quality from sampling randomness* — a cleaner lab bench, not the ruler.
- **Self-repair attempt in progress when paused:** learner half-retrieved "prompt harness" from the lesson (source confirms the term: "implement a prompt testing harness that evaluates prompt changes against a set of expected outputs"). Unpacking question posed — **unanswered**: "A harness: what does it hold, and when does it run — so the article-1 regression gets seen?"

## Repair steps

| Step | Fact (target) | Rests on | Check | Learner answer | Verdict |
|---|---|---|---|---|---|
| R3-repair 1/2 | mass splits across all plausible candidates at unresolved forks; loop samples from the split | p(next\|context), autoregressive loop, learner's own "probability" currency | where does mass go at the "dogs are…" fork; what does the loop emit | "the probability mass splits. if context favors no candidate, the a token is chosen at random" | pass (graded) |
| R3-repair 2/2 | precise instruction deletes fork arms; mass concentrates on survivors | step 1 + weighted-sampling sharpening | what does "exactly 5 bullets, each with a number, no intro" do to arms and mass | "it narrows the number of choices each of those arms has hence more mass piles up on fewer arms compared to other arms." | pass (graded) |

## Model patch (v1 → breaking case → current state)

- **v1 (verbatim):** the handwritten model quoted above.
- **Breaking case:** the v1/v2/v3 article oscillation (row 4) — definition satisfied at every step, no way to see the regression; plus the two failed mechanism chains on row 3 before the fork-arm repair.
- **Current state (assembled only from the learner's verbatim session words):** v1 with row 3's middle patched by the fresh-surface answer: vague prompt → more arms, mass split wide → generic output; precise prompt → fewer arms, mass piled on survivors → narrower space → precise output; *"Models take prompts literally means that they take what conditioning of the next token distribution they imply seriously."* Row 4 stands at "its missing a way to measure success" + the half-retrieved term "prompt harness," unpacking not yet done.
- **Formal v2 capture:** not yet taken (graduation step not reached).

## Pause exit ticket

- Question (per pause flow): "state the part of your current prompt-engineering model you are least sure about, and one case you think might break it."
- **Unanswered** at learner's explicit instruction (laptop shutdown). Recorded as FAIL, confidence no-idea, miss_class cue. Not softened.

## Resume

1. **Row 4 (open, first):** re-pose the harness unpacking question — "a prompt testing harness: what does it hold, and when does it run, so the article-1 regression gets seen?" Learner holds the noun; the mechanism must be assembled in their words. If the unpacking fails, repair mode on the eval-layer gap (source pointer: Anthropic raw file "Before prompt engineering" list; Rohit harness learning objective; Rohit harness code section is past the learner's read point — "build it" — read on demand at resume).
2. **Row 5 (not attacked):** failure regime — attack (likely counterexample/perturbation) using Wei et al. CoT-below-~100B and Rohit's role-over-specificity hallucination passages.
3. **Graduation:** v2 capture → entailment check → naive-student clone (qualitative target: tool/technique choice, e.g., CoT-on-small-model or prefill decision) → battery remainder (perturbation/sabotage not yet exercised) → consolidation diagram → handoff.
4. Note: temperature/top-p mechanics, prefill contradiction, and the CoT 10–40% conditional-vs-unconditional contradiction have **not** been taught; they are available as later attack material, not owed to the learner.

## Resume session — 2026-10-29 (completed)

**Resume pointer honored:** row 4 first (harness unpacking), then row 5, then graduation. Scout re-ran (purpose: resume) — all 10 sources re-fetched live 2026-10-29, Rohit body byte-identical (no upstream drift); contradictions re-surfaced: prefill (real), CoT payoff (real → actually resolved into a scope stitching below), Rohit's Johnny citation (real source error), prompt scope (apparent), role mechanism (apparent).

### Row 4 — eval/measurement layer (repaired, closed)

- Re-posed the harness unpacking question. First attempt: a wrong ruler — "measuring how the probability mass is distributed among the arms … if it is more piled towards a few, then I think that is better" (FAIL, structural). Killed by the learner's own two-sided clash with their banked temp-0 verdict ("flipping it i think wont change whether the output is good or not") — concession pass: piling measures how hard the model was squeezed, not whether the output is right.
- Re-posed + one R0 rung (objectives pointer). **Harness assembled, learner words:** "The prompt harness holds the set of expected outputs and the outputs we actually received, allowing us to compare the two sets for any regression. When we make a change, the prompt runs." (pass)
- Fresh-surface close (v5 = "never include any numbers" on three held articles): first answer "side outputs from the original and tweaked prompts. That is how we can see whether there was a regression" — FAIL (discrimination): what-runs-and-on-what omitted, old-vs-new diff substituted for the expected-output verdict. One careless re-paste (FAIL). R0 redirect into their own sentence → **ruler deployed (pass, learner words):** "You compare what you got against what you expected" + "it degraded the quality of the response" (instruction carries the blame). Row 4 closed.

### Row 5 — failure regime (repaired, closed)

- **Predict-before-attack** (quiz, context predict): stance = narrowing is NOT always safe; super-specific role → few matching examples → mass piles on few likely-wrong arms → hallucination. Matches the source's role limit ("If the role is so specific that few training examples match, the model will hallucinate … very little high-quality text at that intersection") — regime 1 banked in the learner's words.
- **Synthesis clash (real contradiction surfaced, learner resolved):** "no genuine disagreement … the chain of thought paper simply flags the edge case. Otherwise, Rohit is right" + mechanism half just re-describes sampling (FAIL, structural). Pollution trace produced at first press (pass): "the next step is built on that shaky foundation … pollutes the rest of the response" → "it would be better for it to answer in one shot." **Scope stitched (pass):** 10-40% "for models greater than approximately 100 billion parameters", below that mass piles on fluent unfounded arms and pollutes. Regime 2 banked. Row 5 closed.

### Graduation

- **Entailment check:** why-half produced ("We need to first fix the ruler so we can measure if we are making a step forward or a step backward"); breaking half misfired once ("when we underspecify what the output should look like" — ruler-goes-bad, not ruler-unneeded; FAIL careless) and once label-only ("one-off responses"; FAIL execution); link completed (pass): one-off = a single judgment event, no versions stacking, no held set needed; repeated versions need the fixed anchor to make drift visible. Banked.
- **Consistency check:** "reproducibility" wording inspected against the banked determinism-is-repeatability-not-quality distinction — learner picked the comparison kind ("it is the comparison kind"), distinction intact.
- **Model v2 captured verbatim** (learner's closed-book restatement, 2026-10-29, typos as written):

> "So, what's the problem with prompt engineering? The problem is that to get good, non-generic outputs out of these models, we need to do some prompt work. That prompt work is prompt engineering—the process of tweaking prompts to get the desired quality of response. That is measured based on the drift between the output we get and the output we expected or wanted. The mechanism of prompt engineering is that when you send a prompt, it conditions the models for generation. For each token it makes, and for each focus point, it distributes the probability mass across various forking paths. If the prompt is vague, it will distribute the probability mass more evenly over those paths; otherwise, the mass is concentrated over just a few choices. Now, why do we need a measurement layer like a ruler and a harness? When we are creating more than one prompt version, we need a way to track the drift and track progress. If version one gives a bad output, we need a way to measure whether version two will make an even worse output or make it better. That's why we need the measurement layer when we want to make multiple prompt versions. For just a one-off prompt, we don't need it. However, there are two failure regimes when comparing versions like V1, V2, and V3. Failure regime number one: For chain-of-thought, when you tell the model to think step-by-step, it is ideal not to do that for models with less than approximately 100 billion parameters. That actually hurts their performance. The generated paths for certain tokens can be fluent but unfounded, and the next generation of paths will just be polluted by this previous context, which ruins the rest of the response. So it's better for smaller models to generate in one shot. The second failure regime is when we make our prompt too specific—like telling the model it is an expert in a very, very specific niche with 20 years of experience. Because the model has little data on that, it will hallucinate because it doesn't know what to tell you and will just make things up. So when we get too specific, problems arise as well. What neighboring technique would I reach for besides the ruler to measure drift? i'd reach for the harness."
- **Naive-student clone: PASS** using v2 verbatim only (task_succeeded true, misconception_resolved true, no failure causes). Target task: 7B ticket-classifier proposal (expert persona + step-by-step). The clone rejected it on both regimes (CoT far below the ~100B line via pollution; persona matches the too-specific shape via fabrication), gave "sharper is better" only conditional license, and routed the version comparison through the ruler. Seeded "more constraints always help" refuted twice. Honest gaps reported (logged as Mistakes row 2026-10-29, clone blind spots): no threshold/advance test for too-specific, no regime-coexistence statement, no third option between too vague and too specific.
- **Battery remainder — sabotage:** teammate replaces held expected outputs with the same model grading at temp 0. First answer attacked judge noise/false-positives (FAIL, discrimination — planted break was ruler independence). Seam press: "the model writes what it sees as a good, expected output … poisons the rest of the chain of versions" (pass). Fresh-surface variant (bigger temp-0 judge, no human expected outputs): "still not whole … the part that is still missing is what the human actually wants" (pass). Battery closed: mechanism press (r3), counterexample (r4/r5), source-clash/synthesis (r5), perturbation (r3/r5), sabotage (ruler-independence) all exercised.

### Verdicts ledger (2026-10-29, in order)

| # | Item | Qtype | Verdict | Confidence | Hints |
|---|---|---|---|---|---|
| 13 | concentration-ruler answer | discriminative | fail | hunch | 0 |
| 14 | piled-vs-temp-0 reconciliation | micro-check | pass | hunch | 1 |
| 15 | harness assembled | micro-check | pass | hunch | 1 |
| 16 | v5 fresh-surface walk-through | micro-check | fail | hunch | 0 |
| 17 | ruler-question re-paste | micro-check | fail | hunch | 0 |
| 18 | article-2 ruler deploy | micro-check | pass | hunch | 1 |
| 19 | row-5 prediction | micro-check | pass | hunch | 0 |
| 20 | CoT synthesis + mechanism | discriminative | fail | hunch | 0 |
| 21 | pollution chain trace | micro-check | pass | hunch | 0 |
| 22 | scope stitch (~100B+) | micro-check | pass | hunch | 0 |
| 23 | entailment check v1 | explain-back | fail | hunch | 0 |
| 24 | one-off label only | explain-back | fail | hunch | 0 |
| 25 | one-off link completion | micro-check | pass | hunch | 0 |
| 26 | reproducibility-kind check | micro-check | pass | hunch | 0 |
| 27 | sabotage (judge-noise path) | error-detect | fail | hunch | 0 |
| 28 | sabotage seam press | micro-check | pass | hunch | 1 |
| 29 | sabotage fresh-surface (big judge) | micro-check | pass | hunch | 0 |
| 30 | naive-student clone | explain-back | pass (feynman_pass) | hunch | 0 |

`Attempts.json` — `interval_index` 3, `consecutive_correct` 3, `next_review` **2026-11-28**, `feynman` pass (30 attempts total: 17 pass / 13 fail).

### Open items for `/review`

1. Mistake rows due: the two 2026-10-28 `active` rows (mechanism `[miss: cue]`; pause exit ticket) + new 2026-10-29 `active` row (clone blind spots — priority: the too-specific separator question).
2. Blind spots (from clone): too-specific threshold/advance test; regime coexistence; vague↔specific middle. (b) is an open question in the sources, not owed.
3. Unsurfaced material available for later lessons: temperature/top-p mechanics, prefill contradiction (real, version-bounded), Rohit's Johnny citation error (real), prompt-scope + role-mechanism (apparent), PE2 meta-prompting limits.
