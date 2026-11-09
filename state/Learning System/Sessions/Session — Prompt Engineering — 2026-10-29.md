# Session — Prompt Engineering (Phase 11 L01, interrogation) — 2026-10-29

**Type:** Teach (stress-test) — resume of the 2026-10-28 pause; session completed (graduation reached, no exit ticket needed — graduation serves as the close)
**Source:** aiengineeringfromscratch.com Phase 11 L01 — Prompt Engineering; Scout re-ran (purpose: resume) — all 10 raw sources re-fetched live 2026-10-29, Rohit body **byte-identical** to 2026-10-28 (sha256 match → no upstream drift)
**Learner material:** continuation only — no new notes; learner had already read the lesson up to "build it"

## What happened (timeline)

1. **Resume at row 4** (harness unpacking, re-posed). First answer proposed a wrong ruler — pile/spread of output mass as the quality measure (FAIL, structural). Broken by the learner's own contradiction with their banked temp-0 verdict; concession accepted (comparison ≠ concentration; "temperature … piles but says nothing about goodness").
2. Harness assembled after one R0 rung (learning-objectives pointer): holds expected outputs + actual outputs, runs on every prompt change, compare to see the regression (PASS, learner words verbatim banked).
3. Fresh-surface close (v5 "never include any numbers", three held articles): FAIL — old-vs-new diff substituted for the expected-output verdict, no run/cases named; one careless verbatim re-paste (FAIL); R0 redirect into their own sentence landed → **ruler deployed** (compare v5's output against article 2's expected; the no-numbers instruction carries the degradation blame). Row 4 closed.
4. **Row 5, prediction first** (closed-book): yes — narrowing can hurt; super-specific role → few matching training examples → mass piles on few likely-wrong arms → hallucination; matches Rohit's role-limit line. Regime 1 banked.
5. **CoT synthesis clash** (⚠️ real, surfaced): learner initially said "no genuine disagreement … Rohit is right," edge-case framing, plus a mechanism half that only re-described sampling (FAIL, structural). Pollution trace produced at first press (flawed step 1 conditions later steps → "pollutes the rest of the response" → one-shot better for small models; PASS). Scope stitched: 10-40% holds for ~100B+; below that, mass piles on fluent unfounded arms (PASS). Row 5 closed.
6. **Graduation:**
   - Entailment check: why-half passed (fixed ruler distinguishes step forward from backward); breaking half failed twice (ruler-malfunction misread; then label-only "one-off"); machinery completed on the third attempt (one-off = single judgment event; repeated versions need the fixed anchor). Banked.
   - "Reproducibility" wording check: comparison kind selected; determinism-is-repeatability-not-quality distinction intact.
   - **v2 captured verbatim** (closed book, typos as written):

     > "So, what's the problem with prompt engineering? The problem is that to get good, non-generic outputs out of these models, we need to do some prompt work. That prompt work is prompt engineering—the process of tweaking prompts to get the desired quality of response. That is measured based on the drift between the output we get and the output we expected or wanted. The mechanism of prompt engineering is that when you send a prompt, it conditions the models for generation. For each token it makes, and for each focus point, it distributes the probability mass across various forking paths. If the prompt is vague, it will distribute the probability mass more evenly over those paths; otherwise, the mass is concentrated over just a few choices. Now, why do we need a measurement layer like a ruler and a harness? When we are creating more than one prompt version, we need a way to track the drift and track progress. If version one gives a bad output, we need a way to measure whether version two will make an even worse output or make it better. That's why we need the measurement layer when we want to make multiple prompt versions. For just a one-off prompt, we don't need it. However, there are two failure regimes when comparing versions like V1, V2, and V3. Failure regime number one: For chain-of-thought, when you tell the model to think step-by-step, it is ideal not to do that for models with less than approximately 100 billion parameters. That actually hurts their performance. The generated paths for certain tokens can be fluent but unfounded, and the next generation of paths will just be polluted by this previous context, which ruins the rest of the response. So it's better for smaller models to generate in one shot. The second failure regime is when we make our prompt too specific—like telling the model it is an expert in a very, very specific niche with 20 years of experience. Because the model has little data on that, it will hallucinate because it doesn't know what to tell you and will just make things up. So when we get too specific, problems arise as well. What neighboring technique would I reach for besides the ruler to measure drift? i'd reach for the harness."
   - **Naive-student clone: PASS** on a 7B-ticket-classifier proposal (expert persona + step-by-step): both constraints rejected from v2 alone; "sharper is better" licensed only conditionally; version comparison routed through the ruler. Seeded "more constraints always help" refuted twice. Blind spots honestly reported and banked as an active Mistakes row.
   - **Battery remainder — sabotage:** automated self-judge at temp 0. FAIL (discrimination — attacked judge noise, not ruler independence); seam press passed ("the model writes what it sees as a good, expected output … poisons the rest of the chain of versions"); fresh-surface variant (bigger temp-0 judge, no human expected outputs) passed ("the part that is still missing is what the human actually wants"). Battery closed — all three weapons exercised across the session (counterexample, source-clash, perturbation, mechanism press, sabotage).
7. Learner: "no questions. close it out." Handoff written; wiki ingest + review gate run at close.

## Verdicts ledger (graded attempts, in order, 2026-10-29)

| Attempt | Item | Qtype | Verdict | Confidence | Hints (rungs) |
|---|---|---|---|---|---|
| 13 | concentration-ruler answer (harness re-pose) | discriminative | fail | hunch | 0 |
| 14 | piled-vs-temp-0 reconciliation | micro-check | pass | hunch | 1 |
| 15 | harness assembled (hold/run/see) | micro-check | pass | hunch | 1 |
| 16 | v5 fresh-surface walk-through | micro-check | fail | hunch | 0 |
| 17 | ruler-question re-paste | micro-check | fail | hunch | 0 |
| 18 | article-2 ruler deploy | micro-check | pass | hunch | 1 |
| 19 | row-5 failure-regime prediction | micro-check | pass | hunch | 0 |
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

`Attempts.json` — 30 total attempts (17 pass / 13 fail), `interval_index` 3, `consecutive_correct` 3, `next_review` **2026-11-28**, `feynman` pass.

## Mistakes banked / updated (for /review)

1. **2026-10-28 eval-layer row → `review` (retries 2):** repaired + closed today (harness assembled; v5 discrimination crack patched in-session; two correct recalls).
2. **2026-10-28 mechanism row (`active`) + pause exit-ticket row (`active`):** untouched today; v2 capture was not a self-location, so the ticket stays unproven.
3. **NEW 2026-10-29 CoT synthesis row → `review` (retries 1):** unconditional 10-40% + sampling-redescription fail, repaired (pollution trace + scope stitch).
4. **NEW 2026-10-29 sabotage row → `review` (retries 1):** ruler-independence miss under an automated judge, repaired (model-authors-the-expectation + fresh-surface scorer/ruler split).
5. **NEW 2026-10-29 clone blind-spots row → `active`:** too-specific threshold/advance test; regime coexistence; vague↔specific middle — priority drill for the next review.

## Model state

- **v2 captured verbatim** (see lesson file § Model v2 content in § Resume session — 2026-10-29). All five triage rows closed. No formal v3.
- Remaining curriculum: learner has not read past "build it" — the lesson's harness code section, temperature/top-p mechanics, prefill contradiction, PE2 limits, and Rohit's Johnny citation error are still untaught and available as later lesson material.

## Resume pointer

**No in-progress attack.** Interrogation complete; next is either the Phase 11 L02 curriculum target (`/lesson`) or the Phase 1 L10 branch already paused at Checkpoint 6/6, mini 1/3 — Curriculum position untouched by this session (branch rule honored).
