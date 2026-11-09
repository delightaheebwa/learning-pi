# Session — Dimensionality Reduction (P1 L10 resume, CP6 mini 1 pause) — 2026-10-21

**Session:** Tutor (resume) · **Date:** 2026-10-21 · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) — paused at **Checkpoint 6/6 (mini 1/3 in-progress)**
**Taught:** **CP6 mini 1 (Hidden Piece 1 sealed: Kernel PCA centering in feature space: distance cancellation in RBF and explicit double-centering formula)** — pause exit ticket X1 completed (`pass`, `sure`, 1 hint). Paused before unpacking Hidden Piece 2.
**Position:** paused at Checkpoint 6/6 (mini 1/3 in-progress) — CP5 fully sealed 2026-10-19; minis 4+5a sealed 2026-10-17; minis 2–3 sealed 2026-10-14; mini 1 sealed 2026-10-13; CP4 fully sealed 2026-10-12; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30. **Resume: Checkpoint 6/6, mini 1/3 (Hidden Piece 1 sealed; resume at Hidden Piece 2: eigenvectors of centered K as coordinates and 1/sqrt(lambda) scaling, followed by Hidden Piece 3: pre-image problem with a small 3-point toy walkthrough)**.
**Sources:** Scout digest `Learning System/.tmp/context-36761f9b-8309-4534-96a9-60a8a8db4d66-dimensionality-reduction.json` (fresh 2026-10-20, inside 7-day TTL); raw bodies `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - sklearn-kpca.md` (KernelPCA parameterization, kernel trick, centering in feature space, pre-image problem), `…- rohit.md` (PCA on nonlinear manifolds), `…- shlens.md`.

## What ran

1. **CP6 mini 1 — Kernel PCA with an RBF kernel (Hidden Piece 1 sealed):**
   - **Context & Progression:** Unpacking the first of four hidden mechanics identified during the 2026-10-20 pause: centering the $n \times n$ Gram matrix $K$ in feature space $\mathcal{H}$.
   - **4-Beat Foundation Delivered (Turn Kind: Idea):**
     - **Problem (Input-space centering failure on RBF):** In standard PCA, centering subtracts the input mean $\mu = \frac{1}{n} \sum x_i$. In Kernel PCA with an RBF kernel $k(x, x') = \exp(-\gamma \|x - x'\|^2)$, pairwise differences $(x_i - c) - (x_j - c) = x_i - x_j$ cancel any uniform spatial translation $c$. Centering the raw data in $\mathbb{R}^d$ leaves the kernel matrix $K$ completely unaltered and fails to center the lifted points $\phi(x)$ in $\mathcal{H}$ around $\mu_\phi = \frac{1}{n}\sum \phi(x_i)$.
     - **Where from / Double-Centering Formula:** In feature space $\mathcal{H}$, the centered points are $\tilde{\phi}(x) = \phi(x) - \mu_\phi$. Inner products $\tilde{K}_{ij} = \langle \tilde{\phi}(x_i), \tilde{\phi}(x_j) \rangle$ expand into kernel evaluations:
       $$\tilde{K} = K - \mathbf{1}_n K - K \mathbf{1}_n + \mathbf{1}_n K \mathbf{1}_n = (I - \mathbf{1}_n) K (I - \mathbf{1}_n)$$
       where $\mathbf{1}_n$ has every element equal to $1/n$ ($\mathbf{1}_n = \frac{1}{n}\mathbf{1}\mathbf{1}^T$). This performs full feature-space centering directly on the similarity table $K$ without ever computing or materializing $\phi(x)$ or $\mu_\phi$.
     - **Conditions / Boundaries:** Requires $O(n^2)$ memory and operations. Double-centering applies to the training Gram matrix; projecting novel test points requires asymmetric centering against training column/row means.
     - **Contrast:** Standard linear PCA centers $d$ feature columns ($O(nd)$); Kernel PCA double-centers the $n \times n$ kernel matrix ($O(n^2)$) using the centering projector $(I - \mathbf{1}_n)$.
   - **Socratic Ladder & Dialogue Beats:**
     - Guided inquiry explored why shifting input points $x_i \mapsto x_i - \mu$ fails to alter Gaussian RBF kernel values.
     - Learner recognized that the distance $\|x_i - x_j\|$ is translation-invariant, meaning feature-space centering cannot be achieved by input pre-processing.
     - Unpacked the algebraic expansion of $\langle \phi(x_i) - \mu_\phi, \phi(x_j) - \mu_\phi \rangle$ leading to subtracting row means, column means, and adding the grand mean matrix $\mathbf{1}_n K \mathbf{1}_n$.

2. **Pause Exit Ticket X1 (quiz-audit PASS, grade-audit agreed 1/1, `sure`, 1 hint):**
   - **Question / Focus:** Kernel PCA centering in feature space: (1) why input-space centering does not center data in feature space for an RBF kernel (distance cancellation: $\|(x_i - \mu) - (x_j - \mu)\| = \|x_i - x_j\|$), and (2) the explicit double-centering matrix formula $\tilde{K} = K - \mathbf{1}_n K - K \mathbf{1}_n + \mathbf{1}_n K \mathbf{1}_n$ (or $(I - \mathbf{1}_n) K (I - \mathbf{1}_n)$).
   - **Verdict:** `PASS` (`applied`, `sure`, 1 hint). Learner correctly articulated the shift-cancellation in Euclidean distance for RBF and correctly produced the double-centering matrix formula.

## Attempts (ops.py, already written in-session)

- `PCA (Dimensionality Reduction)` — 2026-10-21:
  - pass `applied` (`sure`, 1 hint) — Pause exit ticket X1
  - Net: mastery **0.90** advisory, `interval_index` **3**, `last_reviewed` **2026-10-21**, `next_review` **2026-11-20**, `consecutive_correct` 3, `consecutive_wrong` 0, `Last Q Type` **applied**.

## Mistakes candidates

- None (`mistakes: []`). Exit ticket passed clean under applied reasoning; Socratic trajectory was smooth.

## Dependency events

- None (`just_tell_me`: 0, `told_repair`: 0, `declined_generation`: 0). No opt-outs; learner derived the mechanics.

## Learner pacing & next session focus

- Paused mid-Checkpoint 6 at mini 1/3 per learner pacing protocol.
- Hidden Piece 1 (centering $K$ in feature space via $(I - \mathbf{1}_n) K (I - \mathbf{1}_n)$ and RBF shift-cancellation) is sealed.
- Next session resumes at Checkpoint 6/6, mini 1/3 to unpack:
  1. **Hidden Piece 2:** Why eigenvectors of centered $\tilde{K}$ act as coordinates, and the $1/\sqrt{\lambda}$ scaling factor.
  2. **Hidden Piece 3:** The pre-image problem with a small 3-point toy walkthrough.
