# Session — Dimensionality Reduction (P1 L10 resume, CP6 mini 1 pause) — 2026-10-23

**Session:** Tutor (resume) · **Date:** 2026-10-23 · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) — paused at **Checkpoint 6/6 (mini 1/3 in-progress)**
**Taught:** **CP6 mini 1 (Hidden Piece 2 Part 1 re-anchored on concrete 3-point toy cloud: projection dot products yielding Row 1 of $\tilde{K}$ and coordinate extraction via $\tilde{K}\alpha = \lambda\alpha$; Pause Exit Ticket X1 sealed on repair)** — paused before completing Part 2 ($1/\sqrt{\lambda_k}$ scaling) and Hidden Piece 3 (pre-image problem).
**Position:** paused at Checkpoint 6/6 (mini 1/3 in-progress) — CP5 fully sealed 2026-10-19; CP4 fully sealed 2026-10-12; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30. **Resume: Checkpoint 6/6, mini 1/3 (Hidden Piece 1 sealed; Hidden Piece 2 in-progress — sealed Part 1: eigenvectors as coordinates via $(\tilde{K}\alpha_k)_i = \lambda_k \alpha_{k,i}$ re-anchored on 3-point toy cloud; resume at Part 2: $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and $1/\sqrt{\lambda_k}$ scaling, followed by Hidden Piece 3: pre-image problem as a story and inverse transform)**.
**Sources:** Scout digest `Learning System/.tmp/context-76045384-189d-44d4-95ba-f65c19245564-dimensionality-reduction.json`; raw bodies `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - sklearn-kpca.md` (KernelPCA parameterization, dual representation, kernel trick, centering in feature space, pre-image problem), `…- rohit.md` (PCA on nonlinear manifolds), `…- shlens.md`.

## What ran

1. **Resumed Phase 1 Lesson 10 (Dimensionality Reduction) at Checkpoint 6/6, mini 1/3 (Kernel PCA with an RBF kernel)**, aiming to introduce Hidden Piece 2 Part 2 (the $1/\sqrt{\lambda_k}$ normalization factor).
2. **Progression Check & Pacing:** Learner flagged that the Hidden Piece 2 Part 1 summation progression from the previous session ($v_k = \sum_j \alpha_{k,j} \tilde{\phi}(x_j) \to \langle v_k, \tilde{\phi}(x_i) \rangle_\mathcal{H} = (\tilde{K} \alpha_k)_i = \lambda_k \alpha_{k,i}$) had not fully clicked yet (*"tbh, i havent quite understood yet this progression."*).
3. **Re-walked Hidden Piece 2 Part 1 using a concrete 3-point toy cloud $(\tilde{\phi}(x_1), \tilde{\phi}(x_2), \tilde{\phi}(x_3))$:**
   - **Step A:** Contrasted Standard PCA (axis $u$ is a weighted blend of $d$ features) with Kernel PCA (lifted feature coordinates are infinite-dimensional and never computed directly, so axis $v = \alpha_1 \tilde{\phi}(x_1) + \alpha_2 \tilde{\phi}(x_2) + \alpha_3 \tilde{\phi}(x_3)$ is built as a weighted blend of the 3 lifted training points).
   - **Step B:** Distributed the projection dot product:
     $$\langle v, \tilde{\phi}(x_1) \rangle = \alpha_1 \langle \tilde{\phi}(x_1), \tilde{\phi}(x_1) \rangle + \alpha_2 \langle \tilde{\phi}(x_2), \tilde{\phi}(x_1) \rangle + \alpha_3 \langle \tilde{\phi}(x_3), \tilde{\phi}(x_1) \rangle$$
     Learner identified that the three dot products are Column 1 (and Row 1, by symmetry of $\tilde{K}$) of the $3 \times 3$ centered similarity table $\tilde{K}$, and that multiplying by $\alpha$ yields $(\tilde{K} \alpha)_1 = \lambda \alpha_1$.
   - **Step C:** Consolidated all 3 points in a $3 \times 3$ matrix-vector table showing that projecting Points 1, 2, and 3 onto $v$ yields $\tilde{K} \alpha = \lambda \alpha$, so the entries of eigenvector $\alpha$ directly supply the projected coordinates along the nonlinear principal axis.
4. **Learner confirmed comprehension** (*"it clicks. if an eigenvector is multiplied with K tilda it gives lambda * alpha hence giving us the projected corrdiantes. /pause"*) and requested a pause.
5. **Ran Pause Exit Ticket X1 (3-line qualitative trace on the 3-point Kernel PCA dual projection walk):**
   - **Initial Attempt:** Correctly explained why the axis is a blend of the 3 lifted points (infinite feature dimensions) and the zero-collapse extreme check, but gave generic label "Projection" instead of Kernel PCA and echoed $\tilde{K} \alpha = \lambda \alpha$ without the dot-product-to-Row-1 causal bridge.
   - **Repair Prompt & Response:** Learner named Kernel PCA specifically and supplied the missing causal bridge — dotting $v$ with lifted Point 1 across all 3 components produces Row 1 of $\tilde{K}$ (by symmetry of $\tilde{K}$), connecting $\langle v, \tilde{\phi}(x_1) \rangle$ to $(\tilde{K} \alpha)_1 = \lambda \alpha_1$. Repair passed cleanly.
6. **Next session resumes at Checkpoint 6/6, mini 1/3:**
   - **Hidden Piece 2 Part 2:** Intuition read of $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ normalization — what the $1/\sqrt{\lambda_k}$ scaling factor is for (keeping the projection direction unit-length in feature space) and what happens as $\lambda_k \to 0$.
   - **Hidden Piece 3:** The pre-image problem as a story — why a point in feature space may have no exact input-space picture, and why reconstruction requires learning an inverse regression model (`fit_inverse_transform=True`).

## Attempts (ops.py, already written in-session)

- `PCA (Dimensionality Reduction)` — fail (exit ticket X1 initial attempt, `explain-back`, `sure`, hints 0) → mastery 0.50, interval_index 2.
- `PCA (Dimensionality Reduction)` — pass (exit ticket X1 repair, `explain-back`, `sure`, hints 1) → mastery **0.75** advisory, `interval_index` **3**, `last_reviewed` **2026-10-23**, `next_review` **2026-11-22**, `consecutive_correct` 1, `consecutive_wrong` 0, `Last Q Type` **explain-back**.

## Mistakes candidates

- None (`mistakes: []`). Initial exit ticket gap on the causal bridge and technique name was immediately repaired in-turn without logging a persistent misconception.

## Dependency events

- None (`just_tell_me`: 0, `told_repair`: 0, `declined_generation`: 0). No opt-outs; learner derived the mechanism.

## Learner verbatim quotes

- Flagging that the n-point summation progression for Hidden Piece 2 Part 1 needed unpacking:
  *"tbh, i havent quite understood yet this progression."*
- 3-point toy walk: locating the distributed dot products in $\tilde{K}$ and the eigenvalue collapse:
  *"1. the whole of the first column of the centered similarity table / 2. i think because we are dealing with a whole column here hence eigenvector * eigenvalue for that whole column in K tilda"*
- One-sentence synthesis of why eigenvector $\alpha$ gives projected coordinates:
  *"it clicks. if an eigenvector is multiplied with K tilda it gives lambda * alpha hence giving us the projected corrdiantes. /pause"*
- Pause Exit Ticket X1 (initial trace):
  *"1. Projection. the axis must be built as a blend of the 3 lifted points because in the lifted feature space there are infinite dimensions hence we can't weight using infinite number of features. / 2. for each point, K tilda * alpha = lambda * alpha, resulting in the projected coordinates / 3. the coordinate collapses to zero."*
- Pause Exit Ticket X1 (repair trace):
  *"1. kernel PCA / 2. when we multiply v and sigma(x1) on all components, it is equivalent to the row 1 in K tilda(K tilda is symmetric)"*

## Learner pacing & next session focus

- Paused mid-Checkpoint 6 at mini 1/3 per learner pacing request.
- Hidden Piece 1 sealed 2026-10-21.
- Hidden Piece 2 Part 1 sealed and re-anchored 2026-10-23 (eigenvectors as coordinates via $(\tilde{K} \alpha_k)_i = \lambda_k \alpha_{k,i}$ on 3-point toy cloud).
- Next session resumes at Checkpoint 6/6, mini 1/3 to complete:
  1. **Hidden Piece 2 Part 2:** Hilbert space normalization $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and the $1/\sqrt{\lambda_k}$ scaling factor.
  2. **Hidden Piece 3:** The pre-image problem as a story and inverse transform (`fit_inverse_transform=True`).
