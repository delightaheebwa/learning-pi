# Learning Record 0014 — UMAP's manifold assumptions + the patch-glue-match mechanism — 2026-10-13

**Date:** 2026-10-13 · **Lesson:** Phase 1 L10 Dimensionality Reduction (CP5 mini 1) · **Source(s):** UMAP docs (`Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap.md`); umap-paper (McInnes & Healy, `…- umap-paper.md`); umap-faq "How UMAP can go wrong" (`…- umap-faq.md`); Rohit P1 L10 (`…- rohit.md`). Fresh resume re-scout, digest audited PASS.

## What was learned

- **CP5 mini 1 (Bloom: Understand → Apply):** UMAP commits to a geometric model where t-SNE commits to none: the data is assumed to lie **uniformly on a locally connected Riemannian manifold with a locally constant metric**. The mechanism falls out patch by patch: each point's neighborhood is a small connected patch where distance is honest; the patches overlap through shared neighbors and glue into one global fuzzy structure; the embedding is the low-dimensional arrangement whose fuzzy structure best matches that glued one. "Manifold learning" = learn the surface patch by patch, then glue.
- **Manifold = a local property, not a dimension count (Bloom: Remember→Understand):** a straight line is a perfectly good 1-D manifold and a flat plane a 2-D one, so "any shape of dimension 2D or higher" is not the criterion; what defines a manifold is that every sufficiently small patch looks like ordinary flat space. The learner's elicitation instinct — "each layer is a plane" — was this same idea under a wrong frame ("many folds").
- **Stitching = overlap, not distinctness (Bloom: Evaluate):** patches are glued into one surface precisely where they share; two patches with zero overlap cannot be sewn honestly. What the method needs is continuity — the **locally connected** assumption. The docs' failure page shows the extreme break: a point maximally far from all others gets a **random** set of k nearest neighbours, all treated as maximally similar, and the optimizer drags them together, shredding the map around them; `disconnection_distance` exists to cut such edges and let the orphan sit outside the surface.
- **Contrast banked for later:** t-SNE states no data assumptions — it matches pairwise neighbour probabilities non-parametrically. UMAP's geometric stake is what licenses it to claim more (global structure) and fail differently — the Rohit-vs-umap-faq "better global structure" contradiction is queued for a later CP5 mini.

## Evidence

- Elicitation (ungraded): manifold = "an area of the plot whereby there are many folds (like our swiss roll example)"; assumption = "each layer of the fold is a plane."
- State rung ×2 (partial, corrected in-session without attempt rows): "A manifold is simply whatever shape is of dimension 2D or higher" · "There must be no sharing of points hence there must be distinct neighborhoods."
- Check-and-extend: fact-check PASS 8/8, four-beat foundation complete; the two inversions (dimension-count, distinctness) named as frames, not dishonesty — both had the right machinery underneath.
- Exit ticket: quiz-audit PASS (after a strawman-distractor replace and a two-clause length-parity rebuild on X3); grade-audit agreed 3/3, all `sure` — X1 C (local flatness), X2 B (patch→glue→match with t-SNE/PCA near-miss distractors), X3 A (random maximally-similar k-NN + `disconnection_distance`).
- CP4 recall warm-up: 3/3 all `sure` before any new material (sizes-meaningless, Student-t map kernel, escape-fine explosion) — CP4 fully banked.

## Learning notes

- The learner's recurring shape: his instincts are right one layer down (plane-patches, patch sharing) and the frames around them are what slip ("2D or higher", "distinct neighborhoods"). Today both corrections were accepted in one pass with no re-probe friction.
- Highest Bloom demonstrated: Evaluate (the stitching-honesty inversion reasoned from his own patch picture).

## Dependency

- No opt-outs: no `just_tell_me`, no `told_repair`, no `declined_generation` — both State-rung generations were made (2 guiding questions given on the mini, budget spent; hints 2 recorded on the exit-ticket attempt).
