# Learning Record 0013 — t-SNE misreading protocol (cluster sizes; cluster distances) + 3b re-walk — 2026-10-10

**Date:** 2026-10-10 · **Lesson:** Phase 1 L10 Dimensionality Reduction (CP4 mini 4 + the 3b re-walk) · **Source(s):** Wattenberg et al., *How to Use t-SNE Effectively* (Distill, `Knowledge Wiki/raw/sources/2026-09-25 - dimensionality-reduction - distill.md`); Rohit P1 L10 (`…- rohit.md`); van der Maaten & Hinton 2008 (JMLR, verified in-session via fact-check fetches).

## What was learned

- **Cost picture re-walk (CP4 3b, Bloom: Apply — learner-requested slow unpack):** the per-pair fine is $P_{ij}\log\frac{P_{ij}}{Q_{ij}}$, a **P-weighted log-ratio, not a product** — walked one pair at a time (data's frozen 0.05; the map's steerable Q; agreement ⇒ ≈0; disagreement 0.05 vs 0.001 ⇒ ratio 50 ⇒ cost ≈ 0.2; Gaussian collapse ⇒ explosion; fat tail ⇒ escape affordable while big-P pairs still pay). The learner then computed the mismatch case himself: P = 0.2, Q = 0.001 → **≈1.529** ($0.2\log_2 200$ bits; nats route ≈ 1.06) — the log-ratio mechanism now has a learner-owned worked number.
- **Cluster sizes meaningless (CP4 mini 4 atom 1, Bloom: Analyze):** apparent cluster size on a t-SNE plot is nothing but the spread of the 2-D coordinates the optimizer produced — one plot shares ONE user-set perplexity target (only σ_i adapts per point), so size differences can't come from the knob; they are map-internal. Sizes shift with perplexity and even re-runs; pure noise at low perplexity still shows dramatic clumps. Distill's misreading #1: never read group size off the plot — check the raw data's counts.
- **Cluster distances meaningless at arbitrary perplexity; somewhat meaningful only tuned (CP4 mini 4 atom 2, Bloom: Analyze):** the KL cost pins *neighborhoods* (pairs with real P weight); cross-cluster pairs carry P_ij ≈ 0 at low perplexity, so their fine is ≈0 under ANY separation — the gap is dictated by the optimizer's arrangement (initialization, other fines, the knob through σ_i), not the data. Tuning perplexity to the data's natural cluster structure gives cross-cluster pairs small-but-real weights and inter-cluster distances become *somewhat* meaningful — fragile (heterogeneous cluster densities may admit no single valid perplexity, and no directional bet is guaranteed).
- **⚠️ Sources disagreement handled:** Rohit's source states unconditionally that distances between clusters in the output are not meaningful; Distill conditions it on tuning. Resolution taught: **both true at their own scope — Rohit is the safe default rule (never trust inter-cluster distances by default); Distill is the fragile exception that only a deliberate tuning experiment can establish.**

## Evidence

- Warm-up (CP4 mini 3/3b recall): grade-audit-agreed 3/3, all sure.
- 3b re-walk micro-check: grade-audit-agreed pass (learner answered ≈1.529 unprompted-correct, log₂ convention self-chosen).
- Mini 4 atom 1: elicitation (hunch-path knob claim) → 2 guiding questions (ownership anchored in sealed mini 2; the same-plot ⇒ same-target squeeze) → correct own-words state ("the 2d coordinates the otpimizer produced in cluster A are further apart than those in cluster B"); no graded attempt (ungraded rungs).
- Mini 4 atom 2: elicitation ("tracking the KL objective" + the reading-isn't-about-the-data implication, right shape) → 2 guiding questions (weightless pair; no guaranteed direction) → both confirmed in own words; check-and-extend fact-check PASS with the contradiction registered by the verifier.
- Highest Bloom demonstrated: **Analyze** (the weightless-pair mechanism; the no-direction-guarantee inference; the source-disagreement scope split).

## Learning notes

- Recurring shape continues: conclusions arrive right while mechanism labels drift (perplexity "owned" by clusters; bespoke directional bets). The repair that keeps working: contrast against a fact the learner just sealed (one shared user-set target) and ask the structural question ("what's left in the cost to dictate this?").
- The 2026-10-09 pacing request is closed: the slow pair-level unpack worked — the learner's first computed fine (≈1.529 bits) came immediately and exactly.
- Feynman-rubric explain-back not yet run for the misreading protocol (mid-checkpoint pause, not lesson end); scheduled with the CP4 practice / lesson-end quiz.
- Dependency: 0 opt-out events (no just-tell-me, no declined generation).
