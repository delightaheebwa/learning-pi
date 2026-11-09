# Learning Record — Dimensionality Reduction — 2026-10-20

**Date:** 2026-10-20 · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) · **Track:** AIEFS
**Segment:** Checkpoint 6/6, mini 1/3 in-progress (Kernel PCA with an RBF kernel — 2D-to-3D lifting intuition & $d \times d$ vs $n \times n$ matrix size anchor; paused before hidden mechanics)
**Status:** In-Progress (paused at Checkpoint 6/6, mini 1/3)
**Source(s):** `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - sklearn-kpca.md`, `…- rohit.md`, `…- shlens.md`. Context digest `Learning System/.tmp/context-01a134d5-4aeb-715d-8ab7-fe2f4f944481-dimensionality-reduction.json`.

## What was learned

- **Linear vs Nonlinear Manifold Limitations (Bloom: Understand → Analyze):**
  - Standard linear PCA can only identify flat, linear orthogonal subspaces (lines, planes, hyperplanes). When data has concentric or curved manifold structure (e.g. concentric circles in 2D), any linear projection collapses distinct structures onto each other (overlapping intervals).
  - Lifting into a higher-dimensional feature space $\mathcal{H}$ via nonlinear mapping $\phi(x)$ (e.g. mapping 2D points $(x_1, x_2)$ onto a 3D paraboloid with vertical coordinate $z = x_1^2 + x_2^2$) assigns different heights to concentric rings, enabling linear separation in feature space ("pulling one out of the other").
- **Decomposition Matrix Dimensions (Bloom: Understand):**
  - Standard PCA computes and diagonalizes the sample covariance matrix $C = \frac{1}{n-1} X_c^T X_c$, which is of size $d \times d$ (for $d=2$, size is $2 \times 2$), scaling with feature dimension and independent of $n$ for decomposition.
  - Kernel PCA computes and diagonalizes the pairwise similarity Gram matrix $K$ with entries $K_{ij} = k(x_i, x_j)$, which is of size $n \times n$ (for $n=5,000$, size is $5,000 \times 5,000$), scaling with sample size.
- **The Kernel Trick Formulation (Bloom: Understand):**
  - High- or infinite-dimensional inner products $\langle \phi(x), \phi(x') \rangle$ are computed directly via a Mercer kernel function $k(x, x')$ (such as the Gaussian RBF kernel $k(x, x') = \exp(-\gamma \|x - x'\|^2)$) without explicitly calculating or storing the coordinates $\phi(x)$.

## Evidence

- **Formative dialogue rungs (mini 1/3):**
  - Elicitation & Hint: Grasped the 3D paraboloid height assignment ($z = x_1^2 + x_2^2$) separating concentric circles along the vertical axis.
  - Own-Words Statement (`status=learner-note`): *"it couldnt because you cant seperate concentric circles in 2D since there is no line you could draw that would seperate them. mapping to a non linear coordinate helps use to \"pull one out of the other\" by adding a new coordinate which wil put them at different heights thereby truly seperating them."*
- **Pause exit ticket X1 (verifier grade-audit PASS, `sure`, 1 hint):**
  - Question: Why linear PCA fails on 2D concentric rings & how lifting fixes it, plus matrix size comparison for $n=5,000, d=2$.
  - Learner Answer: *"1. it fails beause there is no line in 2d that can seperate them. lifting them into a non linear coordinate puts them at different heights thereby truly seperating them. sure 2. standard pca decomposes into 2x2 while kernel pca decomposes into 5000 x 5000. sure\nfor hidden stuff, i think basically all of it."*
  - Correctly articulated linear non-separability and vertical height separation, and accurately identified standard PCA's $2 \times 2$ vs Kernel PCA's $5,000 \times 5,000$ matrix sizes.

## Attempt metrics (ops.py)

- Concept: `PCA (Dimensionality Reduction)`
- Date: 2026-10-20
- Attempt: pass (`explain-back`, confidence `sure`, hints 1)
- Advisory Mastery: **0.85**
- Interval Index: **3**
- Consecutive Correct: 2 (Consecutive Wrong: 0)
- Last Reviewed: **2026-10-20**
- Next Review: **2026-11-19**
- Last Q Type: `explain-back`

## Mistakes ledger

- `mistakes: []` — No new mistake rows. No errors on exit ticket X1; Socratic guidance successfully resolved the lifting mechanics.

## Dependency & Pacing notes

- Dependency: 0 opt-outs (`just_tell_me`: 0, `told_repair`: 0, `declined_generation`: 0).
- Pacing reflection: Learner candidly surfaced cognitive load: *"that kinda works. it is better than before but i think we will need to slow down a bit on it for the next time. i feel like there is a lot of \"hidden stuff\" i should know when reading some of what you just said but i dont really know. plus some parts still are fuzzy for me. /pause"*.
- Next Session Plan: Stay at Checkpoint 6/6, mini 1/3 to slow down and unpack the hidden mechanics step-by-step:
  1. Centering the $n \times n$ similarity table $K$ in feature space.
  2. Why eigenvectors of $K$ act as low-dimensional coordinates.
  3. The $1/\sqrt{\lambda}$ scaling factor.
  4. The pre-image problem with a small 3-point toy walkthrough.
