# Learning Record 0018 — UMAP: Feature Scaling Decision & Checkpoint 5 Sealed — 2026-10-19

**Date:** 2026-10-19 · **Lesson:** Phase 1 L10 Dimensionality Reduction (CP5 mini 5b sealed + CP5 practice 4/4 + pause exit ticket X1) · **Source(s):** umap-faq "Should I standardize my data?" (`Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap-faq.md`); umap-paper §3.1 & §3.2 (`…- umap-paper.md`); Rohit P1 L10 (`…- rohit.md`). Digest: fresh 2026-10-13 re-scout (inside TTL).

## What was learned

- **Feature Scaling Decision (Bloom: Understand → Apply):**
  - **Centering:** Shifts feature mean to 0 without changing relative distances, spreads, or individual variances.
  - **Standardizing:** Centers each feature and rescales it by dividing by its standard deviation to achieve unit variance ($\sigma = 1$).
  - **The UMAP FAQ Rule:**
    - Standardize when features are **independent measurements on incomparable scales or units** (e.g. clinical blood pressure in mmHg vs age in years vs weight in kg). Without standardization, the feature with the largest numerical spread dominates the Euclidean metric in high-D space, destroying true nearest-neighbor graph connectivity.
    - Center-only (do not standardize) when features **share a meaningful geometric relationship or common coordinate system** (e.g. latitude and longitude, physical 2-D/3-D spatial measurements). Rescaling independent axes with different variances in spatial coordinates distorts genuine geometric aspect ratios (e.g. squishing an elongated island into a sphere).
- **CP5 Synthesis & Checkpoint Sealed (Bloom: Analyze → Evaluate):**
  - Full consolidation of UMAP across its 5 mini-checkpoints: (1) Riemannian manifold assumptions & patch-glue-match mechanics; (2) `n_neighbors` input-side graph connectivity dial; (3) `min_dist` output-side layout packing floor; (4) global structure preservation via whole-embedding negative sampling vs outlier collapse; (5) PCA→UMAP→HDBSCAN pipeline rationale and feature scaling rules.

## Evidence

- **CP5 Practice (4-item batch, verifier-agreed 4/4, all `sure`, 0 hints):**
  - **P1 (`applied`, pass):** Successfully separated `n_neighbors` (graph construction, input connectivity) from `min_dist` (low-dim layout, output packing floor) and described their tradeoffs under retrieval pressure.
  - **P2 (`discriminative`, pass):** Correctly distinguished whole-embedding negative sampling as the driver of relative cluster arrangement, while recognizing the documented outlier pull-together collapse mitigated by `disconnection_distance`.
  - **P3 (`applied`, pass):** Articulated why HDBSCAN is needed to re-estimate density after UMAP contracts connected components and distorts density; rejected KNN-as-clusterer distractor.
  - **P4 (`applied`, pass):** Correctly applied the feature scaling rule to concrete cases (standardize independent clinical metrics; center-only for geographic coordinates).
- **Pause exit ticket X1 (`free-recall`, fail, `sure`, 0 hints):**
  - Core mechanical distinction between centering and standardizing articulated accurately.
  - Application rule inverted under retrieval pressure (assigned centering to independent features and standardizing to meaningful relationships). Logged as active structural mistake.

## Learning notes

- Both prior knob-crossing / terminology slips (2026-10-14 `n_neighbors`/`min_dist` stage crossing, and 2026-10-17 KNN/K-Means clusterer role slip) passed cleanly on P1 and P3 under retrieval pressure without prompting.
- The scaling application inversion on X1 suggests that while the physical geometry intuition was grasped during the Socratic ladder ("spherical island"), the formal domain rule mapping was flipped when asked in the exit ticket. Needs retrieval drill on next warm-up.
- Highest Bloom demonstrated: Evaluate / Apply (integrative CP5 practice across the full UMAP mechanics).

## Dependency

- No opt-outs: no `just_tell_me`, no `told_repair`, no `declined_generation`. All practice items and reflections answered independently by learner.
