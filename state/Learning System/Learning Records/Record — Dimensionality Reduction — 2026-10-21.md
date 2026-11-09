# Learning Record — Dimensionality Reduction — 2026-10-21

**Date:** 2026-10-21 · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) · **Track:** AIEFS
**Segment:** Checkpoint 6/6, mini 1/3 in-progress (Kernel PCA with an RBF kernel — Hidden Piece 1 sealed: centering the $n \times n$ Gram matrix $K$ in feature space)
**Status:** In-Progress (paused at Checkpoint 6/6, mini 1/3)
**Source(s):** `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - sklearn-kpca.md`, `…- rohit.md`, `…- shlens.md`. Context digest `Learning System/.tmp/context-36761f9b-8309-4534-96a9-60a8a8db4d66-dimensionality-reduction.json`.

## What was learned

- **Input-Space Shift Invariance in RBF Kernels (Bloom: Analyze):**
  - Standard PCA relies on mean-centering $x_i - \mu$ in input space $\mathbb{R}^d$.
  - For shift-invariant kernels like the Gaussian RBF kernel $k(x, x') = \exp(-\gamma \|x - x'\|^2)$, uniform translation in input space satisfies $\|(x_i - c) - (x_j - c)\|^2 = \|x_i - x_j\|^2$. The shift cancels out identically in pairwise Euclidean distances, leaving the kernel Gram matrix $K$ completely unchanged.
  - Centering input features does not center the lifted feature vectors $\phi(x)$ around their mean $\mu_\phi = \frac{1}{n} \sum_{i=1}^n \phi(x_i)$ in Hilbert space $\mathcal{H}$.
- **Feature-Space Double-Centering Formulation (Bloom: Apply → Analyze):**
  - Because $\phi(x)$ may be infinite-dimensional and is never explicitly computed, centering must occur implicitly on the Gram matrix.
  - Defining centered features $\tilde{\phi}(x_i) = \phi(x_i) - \frac{1}{n}\sum_{k=1}^n \phi(x_k)$, the inner product expands to:
    $$\tilde{K}_{ij} = \langle \tilde{\phi}(x_i), \tilde{\phi}(x_j) \rangle = K_{ij} - \frac{1}{n}\sum_{k=1}^n K_{kj} - \frac{1}{n}\sum_{l=1}^n K_{il} + \frac{1}{n^2}\sum_{k=1}^n\sum_{l=1}^n K_{kl}$$
  - Expressed compactly in matrix form:
    $$\tilde{K} = K - \mathbf{1}_n K - K \mathbf{1}_n + \mathbf{1}_n K \mathbf{1}_n = (I - \mathbf{1}_n) K (I - \mathbf{1}_n)$$
    where $\mathbf{1}_n = \frac{1}{n}\mathbf{1}\mathbf{1}^T$ is the $n \times n$ matrix with entries $1/n$.
  - This allows exact centering in $\mathcal{H}$ with $O(n^2)$ matrix operations without computing $\phi(x)$.

## Evidence

- **Formative dialogue rungs (CP6 mini 1, Hidden Piece 1):**
  - Socratic derivation of RBF distance cancellation: recognized that shifting points by a mean vector leaves Euclidean distance invariant, making raw input centering ineffective for RBF Kernel PCA.
  - Algebraic walkthrough of inner product expansion of $\langle \phi(x_i) - \mu_\phi, \phi(x_j) - \mu_\phi \rangle$.
- **Pause exit ticket X1 (verifier grade-audit PASS, `sure`, 1 hint):**
  - Question: Why input centering fails for RBF Kernel PCA (distance cancellation) and the explicit double-centering matrix formula for $\tilde{K}$.
  - Answer evaluated: passed clean under applied reasoning (`applied`), confirming understanding of distance cancellation and $(I - \mathbf{1}_n) K (I - \mathbf{1}_n)$.

## Attempt metrics (ops.py)

- Concept: `PCA (Dimensionality Reduction)`
- Date: 2026-10-21
- Attempt: pass (`applied`, confidence `sure`, hints 1)
- Advisory Mastery: **0.90**
- Interval Index: **3**
- Consecutive Correct: 3 (Consecutive Wrong: 0)
- Last Reviewed: **2026-10-21**
- Next Review: **2026-11-20**
- Last Q Type: `applied`

## Mistakes ledger

- `mistakes: []` — No new mistake rows. Exit ticket passed; Socratic trajectory was direct and resolved cleanly.

## Dependency & Pacing notes

- Dependency: 0 opt-outs (`just_tell_me`: 0, `told_repair`: 0, `declined_generation`: 0).
- Pacing reflection: Paused mid-Checkpoint 6 at mini 1/3. Hidden Piece 1 (centering $K$ in feature space) is sealed.
- Next Session Plan: Resume at Checkpoint 6/6, mini 1/3 to unpack:
  1. **Hidden Piece 2:** Why eigenvectors of centered $\tilde{K}$ act as coordinates, and the $1/\sqrt{\lambda}$ scaling factor.
  2. **Hidden Piece 3:** The pre-image problem with a small 3-point toy walkthrough.
