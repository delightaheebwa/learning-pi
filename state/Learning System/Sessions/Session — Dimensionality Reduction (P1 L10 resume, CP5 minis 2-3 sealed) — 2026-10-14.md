# Session — Dimensionality Reduction (P1 L10 resume, CP5 minis 2–3 sealed) — 2026-10-14

**Session:** Tutor (learning-teach, resume flow) · **Date:** 2026-10-14 · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Position reached:** paused at Checkpoint 5/6 — **CP5 minis 2–3 sealed** (mini 1 sealed 2026-10-13). Resume: **CP5 (UMAP) mini 4 — the 'better global structure' claim + the ⚠️ Rohit-vs-umap-faq contradiction.**
**Verification state:** continuing on the fresh 2026-10-13 digest (audited PASS, in TTL) · warm-up + both elicitation batches quiz-audited · tie-down + repairs fact-checked · check-and-extend/idea turns fact-checked with four-beat foundations (two ISSUES→fix cycles on mini 2, one on mini 3) · exit ticket quiz-audited, grade-audit re-batched after one agrees:false, final agreement 1/3 · this batch tutor-audited at handoff.

## Flow

1. **Recall warm-up (CP5 mini 1, graded 3 MCQs; quiz-audit PASS cycle 2; grade-audit agreed 3/3, all `sure`):** W1 D (manifold = every small patch looks like ordinary flat space) · W2 C (patch gene per point, glue overlaps, find the matching 2-D layout) · W3 A (max-far point: random k-NN read as maximally similar, pulled together before `disconnection_distance`). Attempt: UMAP pass (discriminative, sure, 0 hints).
2. **CP5 mini 2 — the `n_neighbors` dial (sealed):**
   - **Elicitation (quiz-audit PASS):** learner: small k → "small local neighborhoods per point", large k → "large local neighborhoods".
   - **Guiding/repair ×2 (fact-check PASS; two ISSUES verdicts fixed en route — the packing-mechanism half of the turn was misattributed and pulled out to min_dist, and an unsupported default-k teleology was dropped):** hard integer k, one fixed list length per run, vs perplexity (per-point soft 2^H; Rohit's "similar to perplexity" = same role, different object). Patch-size half confirmed; the compact/spread half diagnosed as an invert-slip.
   - **State rung (learner's own words):** the leaf zoom analogy — stomata-resolved/whole-leaf-lost at small k, reversed at large k. Accepted, extended with the mechanism (k = chart coverage → overlap; no separate global module; σᵢ sums memberships to log₂(k)) and the two contrasts (min_dist, perplexity).
3. **CP5 mini 3 — the `min_dist` dial (sealed):**
   - **Elicitation (quiz-audit PASS):** learner prior put min_dist on the INPUT side ("how far a point should be from another to be deemed a neighbor"; 0.0 → "each neighborhood has 1 citizen" → fragmented map).
   - **Tie-downs ×2 (grade-audit agreed 2/2, all `sure`):** T3a B (0.0 removes the output-side floor → crowding allowed) · T3b A (fragmentation = charts failing to overlap, not a spacing effect). Neighbour-threshold prior named and discarded.
   - **Idea turn (fact-check PASS 8/8 — claims incomplete re-dispatch once, `0.99` sweep endpoint added):** min_dist = minimum distance apart allowed in the low-D representation; default 0.1, sweep 0.0 → 0.99; floor = repulsion below, attraction packs down to it; graph untouched; a fragmented graph stays fragmented.
   - **Check-and-extend on the box-packing analogy (fact-check PASS 7/7):** accepted with one refinement — permissive floor ("may never pack closer than this"), not a target; added mechanism: min_dist translated into the low-D attraction/repulsion curve via $a$, $b$ fitted from min_dist and `spread` (same force-balance shape as t-SNE); raised end keeps broad shape while packing detail softens. One claim flagged UNVERIFIED (an evenly-spaced-cloud gloss) was dropped from the emitter and re-verified in the second dispatch.
   - **Learner's closing generation (verbatim, complete-correct):** "it kicks in when two points try to go lower than the floor in terms of distance between them."
   - **Sources disagreement surfaced (learner-visible ⚠️):** how hard the floor is — docs: "quite literally, the minimum distance apart that points are allowed to be"; paper Definition 11/Algorithm 5: the piecewise rule is only approximated by a smooth force curve, so sub-floor placements are penalized, not vetoed. Resolution: practical reading = the optimizer strongly resists packing below min_dist; mechanism = gradient penalty.
4. **Pause exit ticket (quiz-audit PASS cycle 3 — X2 stem-vocabulary leak and X3 A length outlier fixed; grade-audit: first dispatch disagreement on X1, second re-batched dispatch returned agreement):** X1 A ✗ fail (gains-only; the trade — fine local detail blurs away — was the asked half) · X2 D ✓ pass (input side: charts stop overlapping → components and singletons float) · X3 B ✗ fail (min_dist put on the input side again — the tie-down slip resurfacing under pressure).
5. **Learner chose to bank the X3/X1 repair for a later warm-up** instead of repairing in-session; the pause was requested immediately after grading.

## Attempts this session (ops.py)

- UMAP (Dimensionality Reduction) pass — discriminative, sure, 0 hints (warm-up).
- UMAP (Dimensionality Reduction) fail — applied, sure (X1: trade-off half omitted).
- UMAP (Dimensionality Reduction) pass — discriminative, sure (X2).
- UMAP (Dimensionality Reduction) fail — applied, sure (X3: input-side min_dist).
- Result: UMAP mastery 0.45, interval_index 2, consecutive_wrong 1, next_review 2026-10-28.

## Mistakes / dependencies

- **Mistake candidate (one row, both fails in it):** the knob-crossing slip — min_dist used where n_neighbors is asked for; the two dials' sides of the pipeline are not yet separated under pressure. Application-type; self-attribution not yet elicited (learner banked the repair for later); prereq named: t-SNE (Dimensionality Reduction).
- **Dependency events:** none — no opt-outs; every State-rung generation was made.

## Position

- Lesson file: paused at Checkpoint 5/6 — CP5 minis 2–3 sealed 2026-10-14; resume **CP5 (UMAP) mini 4 — the 'better global structure' claim + the ⚠️ Rohit-vs-umap-faq contradiction**.
- Pending Ingest.json written (partial): resume_from CP5 mini 4; concepts ×1 (UMAP); mistakes ×1 (the knob-crossing row); dependency_events ∅; three verbatim learner_understanding entries for the wiki page's `## My understanding` block.
- Standing rule in force: paper walks / graded MCQ batches only; no code writes as a learning-system task (learner, 2026-10-05).
