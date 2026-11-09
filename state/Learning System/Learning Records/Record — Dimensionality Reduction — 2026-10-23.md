# Learning Record — Dimensionality Reduction — 2026-10-23

**Date:** 2026-10-23 · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) · **Track:** AIEFS
**Segment:** Checkpoint 6/6, mini 1/3 in-progress (Kernel PCA with an RBF kernel — Hidden Piece 2 Part 1 re-anchored on 3-point toy cloud: dual projection mechanics sealed; Exit Ticket X1 sealed on repair)
**Status:** In-Progress (paused at Checkpoint 6/6, mini 1/3)
**Source(s):** `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - sklearn-kpca.md`, `…- rohit.md`, `…- shlens.md`. Context digest `Learning System/.tmp/context-76045384-189d-44d4-95ba-f65c19245564-dimensionality-reduction.json`.

## What was learned

- **Kernel PCA Projection via 3-Point Toy Cloud (Bloom: Apply → Analyze):**
  - In Standard PCA, the axis $u$ is a linear combination of feature directions: $u = \sum_{j=1}^d w_j e_j$.
  - In Kernel PCA with an infinite-dimensional feature space $\mathcal{H}$ (e.g. Gaussian RBF), explicit feature coordinates cannot be computed. By the representer theorem / dual representation, the principal axis $v$ is constructed as a weighted blend of the lifted training points:
    $$v = \sum_{j=1}^n \alpha_j \tilde{\phi}(x_j)$$
    For a 3-point toy cloud: $v = \alpha_1 \tilde{\phi}(x_1) + \alpha_2 \tilde{\phi}(x_2) + \alpha_3 \tilde{\phi}(x_3)$.
- **Causal Bridge: Inner Products to Row 1 of $\tilde{K}$ (Bloom: Analyze):**
  - Projecting lifted Point 1 ($\tilde{\phi}(x_1)$) onto $v$ distributes across the linear combination:
    $$\langle v, \tilde{\phi}(x_1) \rangle = \alpha_1 \langle \tilde{\phi}(x_1), \tilde{\phi}(x_1) \rangle + \alpha_2 \langle \tilde{\phi}(x_2), \tilde{\phi}(x_1) \rangle + \alpha_3 \langle \tilde{\phi}(x_3), \tilde{\phi}(x_1) \rangle$$
  - The three inner products correspond to $\tilde{K}_{11}, \tilde{K}_{21}, \tilde{K}_{31}$ (Column 1 of $\tilde{K}$). By symmetry ($\tilde{K}_{ij} = \tilde{K}_{ji}$), these are identical to Row 1 of $\tilde{K}$.
  - Taking the dot product of Row 1 with eigenvector $\alpha$ yields $(\tilde{K} \alpha)_1$. Because $\alpha$ is an eigenvector with eigenvalue $\lambda$ ($\tilde{K} \alpha = \lambda \alpha$):
    $$\langle v, \tilde{\phi}(x_1) \rangle = (\tilde{K} \alpha)_1 = \lambda \alpha_1$$
  - Evaluating this simultaneously across all points yields the matrix equation $\tilde{K} \alpha = \lambda \alpha$, establishing that the entries of eigenvector $\alpha$ directly supply the projected coordinates of each data point along the principal axis.
- **Extreme-Case Behavior:**
  - As an eigenvalue $\lambda \to 0$, the projected coordinate $\lambda \alpha_i \to 0$, representing collapse along an uninformative or noise direction.

## Evidence

- **Formative dialogue rungs (CP6 mini 1, Hidden Piece 2 Part 1 re-anchoring):**
  - Learner recognized that inner products of lifted Point 1 with all training points form Column 1 / Row 1 of the centered similarity matrix $\tilde{K}$.
  - Learner connected the matrix-vector multiplication $(\tilde{K} \alpha)_1$ to $\lambda \alpha_1$, stating: *"it clicks. if an eigenvector is multiplied with K tilda it gives lambda * alpha hence giving us the projected corrdiantes. /pause"*.
- **Pause exit ticket X1 (explain-back, sure, 1 repair prompt):**
  - Initial attempt correctly explained point-blending and the zero-collapse extreme check, but omitted the specific name Kernel PCA and echoed the eigenvalue equation without the dot-product causal bridge.
  - Repair prompt elicited the technique name ("kernel PCA") and the exact causal bridge: *"when we multiply v and sigma(x1) on all components, it is equivalent to the row 1 in K tilda(K tilda is symmetric)"*.

## Attempt metrics (ops.py)

- Concept: `PCA (Dimensionality Reduction)`
- Date: 2026-10-23
- Attempt 1: `fail` (`explain-back`, `sure`, 0 hints) → mastery 0.50, interval_index 2.
- Attempt 2: `pass` (`explain-back`, `sure`, 1 hint) → mastery **0.75** advisory, `interval_index` **3**, `consecutive_correct` 1, `consecutive_wrong` 0.
- Last Reviewed: **2026-10-23**
- Next Review: **2026-11-22**
- Last Q Type: `explain-back`

## Mistakes ledger

- `mistakes: []` — No persistent misconception rows. Initial exit ticket omissions were promptly self-corrected upon a single targeted prompt.

## Dependency & Pacing notes

- Dependency: 0 opt-outs (`just_tell_me`: 0, `told_repair`: 0, `declined_generation`: 0).
- Pacing reflection: Paused mid-Checkpoint 6 at mini 1/3 per learner request.
- Next Session Plan: Resume at Checkpoint 6/6, mini 1/3 to complete:
  1. **Hidden Piece 2 Part 2:** Hilbert-space normalization $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and the $1/\sqrt{\lambda_k}$ scaling factor.
  2. **Hidden Piece 3:** The pre-image problem as a story — why a point in feature space may have no exact input-space picture, and why reconstruction requires learning an inverse regression model (`fit_inverse_transform=True`).
