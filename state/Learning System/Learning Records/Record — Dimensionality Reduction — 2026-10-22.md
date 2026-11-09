# Learning Record — Dimensionality Reduction — 2026-10-22

**Date:** 2026-10-22 · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) · **Track:** AIEFS
**Segment:** Checkpoint 6/6, mini 1/3 in-progress (Kernel PCA with an RBF kernel — Hidden Piece 2 opened, Part 1 sealed: The Projection Paradox & Dual Representation)
**Status:** In-Progress (paused at Checkpoint 6/6, mini 1/3)
**Source(s):** `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - sklearn-kpca.md`, `…- rohit.md`, `…- shlens.md`. Context digest `Learning System/.tmp/context-36761f9b-8309-4534-96a9-60a8a8db4d66-dimensionality-reduction.json`.

## What was learned

- **The Projection Paradox in Kernel PCA (Bloom: Analyze):**
  - Standard PCA yields eigenvectors $u_k \in \mathbb{R}^d$ corresponding to input features, allowing direct projection $x^T u_k$.
  - In Kernel PCA, diagonalizing the centered Gram matrix $\tilde{K} \in \mathbb{R}^{n \times n}$ yields eigenvectors $\alpha_k \in \mathbb{R}^n$, whose slots index data points (samples), not features.
- **Dual Representation of Principal Axes (Bloom: Apply → Analyze):**
  - By the representer theorem, the $k$-th principal component $v_k$ in Hilbert space $\mathcal{H}$ lives in the span of the centered transformed data:
    $$v_k = \sum_{j=1}^n \alpha_{k,j} \tilde{\phi}(x_j)$$
  - Projecting the $i$-th centered training sample $\tilde{\phi}(x_i)$ onto $v_k$ in $\mathcal{H}$ expands as:
    $$\langle v_k, \tilde{\phi}(x_i) \rangle_\mathcal{H} = \sum_{j=1}^n \alpha_{k,j} \langle \tilde{\phi}(x_j), \tilde{\phi}(x_i) \rangle = (\tilde{K} \alpha_k)_i$$
  - Since $\alpha_k$ is an eigenvector of $\tilde{K}$ with eigenvalue $\lambda_k$ ($\tilde{K} \alpha_k = \lambda_k \alpha_k$):
    $$(\tilde{K} \alpha_k)_i = \lambda_k \alpha_{k,i}$$
  - This establishes that the projection of sample $i$ onto principal direction $v_k$ is directly proportional to the $i$-th entry of eigenvector $\alpha_k$, showing how eigenvectors over sample indices serve directly as low-dimensional coordinates.

## Evidence

- **Formative dialogue rungs (CP6 mini 1, Hidden Piece 2 Part 1):**
  - Learner recognized that eigenvectors $\alpha_k$ of $\tilde{K}$ index samples / observations / points ($n = 5000$ slots), resolving the apparent dimensional paradox.
  - Learner derived the inner product expansion and eigenvalue substitution $(\tilde{K} \alpha_k)_i = \lambda_k \alpha_{k,i}$.
- **Pause exit ticket:**
  - Waived per learner request ("no exit ticket for today please. lets pause here. /pause").

## Attempt metrics (ops.py)

- Concept: `PCA (Dimensionality Reduction)`
- Date: 2026-10-22
- Attempts: none logged today (`attempts: []`, exit ticket waived).
- Prior Advisory Mastery: **0.90**
- Interval Index: **3**
- Consecutive Correct: 3 (Consecutive Wrong: 0)
- Last Reviewed: **2026-10-21**
- Next Review: **2026-11-20**
- Last Q Type: `applied`

## Mistakes ledger

- `mistakes: []` — No new mistake rows. Socratic derivation was cleanly resolved.

## Dependency & Pacing notes

- Dependency: 0 opt-outs (`just_tell_me`: 0, `told_repair`: 0, `declined_generation`: 0).
- Pacing reflection: Paused mid-Checkpoint 6 at mini 1/3 per learner request.
- Next Session Plan: Resume at Checkpoint 6/6, mini 1/3 to complete:
  1. **Hidden Piece 2 Part 2:** Hilbert-space normalization $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and the $1/\sqrt{\lambda_k}$ scaling factor.
  2. **Hidden Piece 3:** The pre-image problem with a small 3-point toy walkthrough.
