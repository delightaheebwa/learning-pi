# Learning Record 0011 — t-SNE false neighbors + the anomaly-detector tangent — 2026-10-08

**Date:** 2026-10-08 · **Lesson:** Phase 1 L10 Dimensionality Reduction (CP4 mini 1 + anomaly tangent) · **Source(s):** Rohit P1 L10 (`Knowledge Wiki/raw/sources/2026-09-25 - dimensionality-reduction - rohit.md`); Wattenberg et al., *How to Use t-SNE Effectively* (Distill).

## What was learned

- **CP4 mini 1 (Bloom: Analyze):** A linear projection can only shrink or preserve pairwise distances, never enlarge them — so a straight squash of a curved manifold (Swiss roll / carpet-roll) never tears true neighbors apart, but it collapses distinct regions onto each other, manufacturing **false neighbors**: "non-neighbors can become neighbors in the flatten" (learner's own words, sealing the elicitation). The flatten is a smeared shadow of the sheet, not the unrolled sheet. t-SNE's job: rearrange points in 2D so the pairwise-neighborhood **probability pattern** holds (Rohit's mechanism: near = high prob, far = low prob, find the arrangement matching it); it is non-linear and "can unfold complex manifolds that PCA cannot."
- **Attribution precision (Bloom: Understand):** the pairwise-probability mechanism is already in Rohit's source; Distill's distinctive contribution is the interpretation-caution layer (dramatic clusters in pure noise at low perplexity; cluster sizes/distances can mislead) — not the probability framing.
- **Anomaly-detector tangent (Bloom: Evaluate):** (1) **Shape vs depth** — reconstruction error = shape mismatch, measured only across the dropped axes; displacement along a kept axis lies inside the subspace and contributes ≈ 0 error; far-along-the-subspace outliers therefore need a stacked depth-style check (kept-coordinate vs training range; standard practice pairs the Q/SPE statistic with Hotelling T² / Mahalanobis depth). (2) **Unit vs signal** — every residual lives in the dropped subspace by construction (that is the unit, like Celsius); the flag reads its **length** against the threshold set from training residual magnitudes. (3) **Directions get dropped, points never do** — the compression discards every point's across-coordinate identically; residual size decides flagged/not-flagged, never keep/drop.
- **Warm-up repair (Bloom: Apply):** frame-inversion slip — asked which point *escapes* the flag, the learner reused the flagged-outlier signature (huge dropped-axis coordinate = the loudest alarm, not an escape). Detector: on "escapes/gets missed" questions, restate what the detector measures first.

## Evidence

- Warm-up: grade-audit-agreed 2/3 (W1 ✓ round-cloud 90% max-kept; W2 ✗ frame-inversion, repaired; W3 ✓ concentration = blur). Micro-check "flagged or missed?" → **missed**, sure.
- Tangent: check-backs answered — "big residual = outlier vs normal data" (pass, sharpened to shape); cloud micro-check A=(500, 0.1) vs B=(3, 5) discussed via detector logic.
- CP4 mini 1: E1 prediction ("flat 2D plane; neighbors stay neighbors") → two guiding questions → learner's false-neighbor conclusion in own words; consolidation fact-checked PASS 4/4; check-back confirmed the why-now.
- Pause exit ticket: grade-audit-agreed 3/3, all sure (false neighbors · error = residual length off the kept subspace · stacked depth check needed).
- Highest Bloom demonstrated: **Evaluate** (the wrong-answer repair, the vice-versa deduction, and the shape-vs-depth arbitration across the whole tangent).

## Learning notes

- The learner reasons by frame-flipping: when a previously-learned answer is reused on an inverted question, the fix that stuck was restating *what the detector measures* before choosing an option.
- Feynman-rubric explain-back was not run today (mid-checkpoint pause per protocol, not lesson end).
