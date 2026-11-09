# Learning Record 0017 — UMAP's pipeline: each stage does what the other can't — 2026-10-17

**Date:** 2026-10-17 · **Lesson:** Phase 1 L10 Dimensionality Reduction (CP5 mini 4 exit ticket + mini 5a) · **Source(s):** umap-faq "Which tool should I use?" + clustering answer (`Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap-faq.md`); umap-paper §3.1 (k-NN graph first stage) (`…- umap-paper.md`); Rohit P1 L10 + CP3 curse-of-dimensionality table (`…- rohit.md`). Digest: fresh 2026-10-13 re-scout (inside TTL).

## What was learned

- **The pipeline (Bloom: Understand → Apply):** for high-dimensional data (300+ features), PCA (~50 dims) → UMAP (~10–20 dims) → HDBSCAN. Practical defaults, not laws; PCA is for very large/high-dimensional data, UMAP runs directly on smaller datasets.
- **Why PCA first (causal chain):** UMAP's first stage is a k-nearest-neighbour graph, which inherits everything wrong with the input space. At 300+ dims distance concentration flattens the max/min distance ratio (Rohit: ~1.8 at d=10 → ~1.02 at d=1000), so "nearest" barely differs from any other point. PCA keeps the spread-carrying directions — **denoising the neighbor distances** and making graph-building cheap. Nearest-neighbour contrast: PCA is linear and **cannot unfold a manifold** (compresses, never produces the layout); UMAP is nonlinear and unfolds it, but only where "near" still means something. Each stage does what the other can't.
- **Why HDBSCAN last (causal chain):** UMAP "does not preserve density well" and "will contract connected components of the manifold together" — cluster boundaries read off the 2-D plot are artifacts of that distortion. Since the embedding's density is not faithful, the clusterer must **re-estimate density itself** on the 10–20-D embedding. HDBSCAN does, and leaves noise unlabeled; K-Means assumes round, similar-sized clusters and **must assign every point**, so it is obliged to label noise.

## Evidence

- **Mini 4 exit ticket graded 3/3, all `sure` (verifier-agreed), 0 hints:** E1 (graduated global-structure claim), E2 (whole-embedding repulsion vs t-SNE's ≈0 cross-cluster P), E3 (own-words: push/pull + maximally-far blob collapse + the `disconnection_distance` check). Tutor sharpening: `disconnection_distance` *cuts* dangerous edges — the practical check is setting it and screening disconnected vertices.
- **Mini 5a ladder:** elicitation prior right-shaped on both halves (PCA = "the dimensions that actually matter" + harder neighbor plot at 300 dims; clusters overlap ⇒ not distinct) with 0 guiding questions spent; check-and-extend idea turn fact-checked PASS (after re-cutting one synthesized FAQ quote into its three separate sentences); sealing generation half-right.
- **First-occurrence slip:** KNN/K-Means stage-role confusion — the learner wrote "KNN simply groups those clusters with their noise" where the clusterer (K-Means) belongs. Tutor-named, not self-located. Repair: stage-role detector (assigning labels = K-Means; building the graph = KNN) + the double mistake completed (distorted-geometry clustering + forced assignment of noise). Learner confirmed "makes sense".

## Learning notes

- The learner's two-stage-map intuition (graph stage vs optimizer) from the 2026-10-16 knob-crossing repair is carrying over — the 300-dims critique targeted the *graph* stage unprompted.
- The KNN/K-Means slip is a new thread (distinct from the open min_dist/n_neighbors knob-crossing row). Watch whether the stage-role detector sticks; self-location expected before graduation.
- Highest Bloom demonstrated: Apply (pipeline rationale generated from the CP3 distance-concentration anchor).

## Dependency

- No opt-outs: no `just_tell_me`, no `told_repair`, no `declined_generation`. Mini 5b was paused *before* its probe was answered (pacing choice, not an opt-out).
