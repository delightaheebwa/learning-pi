# Session — Dimensionality Reduction (P1 L10 resume, CP6 mini 1 pause) — 2026-10-20

**Session:** Tutor (resume) · **Date:** 2026-10-20 · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) — paused at **Checkpoint 6/6 (mini 1/3 in-progress)**
**Taught:** **CP6 mini 1 (Kernel PCA with RBF kernel: 2D-to-3D lifting intuition & $d \times d$ vs $n \times n$ matrix size anchor)** — pause exit ticket X1 completed (`pass`, `sure`, 1 hint). Paused before unpacking hidden mechanics.
**Position:** paused at Checkpoint 6/6 (mini 1/3 in-progress) — CP5 fully sealed 2026-10-19; minis 4+5a sealed 2026-10-17; minis 2–3 sealed 2026-10-14; mini 1 sealed 2026-10-13; CP4 fully sealed 2026-10-12; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30. **Resume: Checkpoint 6/6, mini 1/3: Kernel PCA with an RBF kernel (PCA on a nonlinear manifold — slow down and unpack the hidden steps: centering the n x n similarity table, why eigenvectors of K act as coordinates, 1/sqrt(lambda) scaling, and the pre-image problem with a small 3-point toy walkthrough)**.
**Sources:** continuing on the fresh **2026-10-13 digest** `Learning System/.tmp/context-01a134d5-4aeb-715d-8ab7-fe2f4f944481-dimensionality-reduction.json` (inside TTL through 2026-10-20); raw bodies `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - sklearn-kpca.md` (KernelPCA parameterization, kernel trick, centering in feature space, pre-image problem), `…- rohit.md` (PCA on nonlinear manifolds), `…- shlens.md`.

## What ran

1. **CP6 mini 1 — Kernel PCA with an RBF kernel (in-progress):**
   - **Context & Progression:** Bridge from linear PCA and non-parametric manifold algorithms (t-SNE, UMAP) to Kernel PCA.
   - **4-Beat Foundation Delivered (Turn Kind: Idea):**
     - **Problem:** Standard linear PCA finds orthogonal linear hyperplanes. Concentric circles or nonlinear manifolds cannot be separated by linear projections; any straight projection collapses them into overlapping intervals.
     - **Where from / Mechanism:** The kernel trick lifts points $x \in \mathbb{R}^d$ via nonlinear map $\phi(x)$ into higher-dimensional Hilbert space $\mathcal{H}$ (e.g. 2D points $(x_1, x_2)$ onto 3D paraboloid $z = x_1^2 + x_2^2$, or infinite dimensions via RBF kernel $k(x, x') = \exp(-\gamma \|x - x'\|^2)$). Inner products $\langle \phi(x), \phi(x') \rangle$ are evaluated directly via kernel function $K_{ij} = k(x_i, x_j)$ without calculating $\phi(x)$ explicitly. Centering $K$ in feature space followed by eigendecomposition yields nonlinear principal components.
     - **Conditions / Boundaries:** Mercer kernel condition (positive semi-definiteness); computational complexity scales with dataset size $n$ rather than feature dimension $d$ ($n \times n$ Gram matrix requiring $O(n^2)$ space and $O(n^3)$ decomposition, vs standard PCA's $d \times d$ covariance matrix); suffers from the pre-image problem where mapping a feature-space projection back to input space $\mathbb{R}^d$ is ill-posed without an exact closed form.
     - **Contrast:** Standard PCA diagonalizes a $d \times d$ covariance matrix $C$; Kernel PCA diagonalizes an $n \times n$ pairwise similarity Gram matrix $K$. Unlike t-SNE/UMAP which iteratively optimize low-dimensional coordinates via gradient descent and lack an explicit mapping for out-of-sample test points, Kernel PCA provides an analytical out-of-sample projection operator via kernel evaluations against training points.
   - **Socratic Ladder & Dialogue Beats:**
     - **Rung 1 (Elicitation):** Elicited why linear PCA fails on 2D concentric circles and how lifting helps.
     - **Rung 2 (Hint & Guided Scaffold):** Socratic hint for 2D points $(x_1, x_2)$ lifted to 3D paraboloid $z = x_1^2 + x_2^2$.
       - Learner verbatim: *"1. for the inner ring is sits at (1,1,z) and the outer sits at (3,3,z). 2. i think they end up as seperate points along the vertical axis"*
       - Guided repair confirmed that the inner ring sits at low height $z$ while the outer ring sits at high height $z$, separating cleanly along the vertical axis.
     - **Rung 3 (Own-Words Statement, `status=learner-note`):**
       - Learner verbatim: *"it couldnt because you cant seperate concentric circles in 2D since there is no line you could draw that would seperate them. mapping to a non linear coordinate helps use to \"pull one out of the other\" by adding a new coordinate which wil put them at different heights thereby truly seperating them."*
       - Check-and-extend confirmed the "pull one out of the other" intuition and linked it to the lifting map $\phi(x)$ and kernel inner product.
   - **Pacing & Comprehension Reflection (Learner-initiated pause):**
     - Learner verbatim: *"that kinda works. it is better than before but i think we will need to slow down a bit on it for the next time. i feel like there is a lot of \"hidden stuff\" i should know when reading some of what you just said but i dont really know. plus some parts still are fuzzy for me. /pause"*
     - Tutor paused immediately to respect learner cognitive load and plan a slow-paced step-by-step breakdown.

2. **Pause Exit Ticket X1 (quiz-audit PASS, grade-audit agreed 1/1, `sure`, 1 hint):**
   - **Question:** "Suppose we have n = 5,000 data points lying on two flat concentric rings in d = 2 dimensions (x_1, x_2). (1) Why does standard linear PCA fail to separate the two rings in 2D, and how does lifting them into a nonlinear coordinate fix that geometry? (2) For this dataset (n = 5,000, d = 2), what is the matrix size (rows x columns) that Standard PCA decomposes versus the pairwise similarity table K that Kernel PCA decomposes?"
   - **Learner Answer (verbatim):** *"1. it fails beause there is no line in 2d that can seperate them. lifting them into a non linear coordinate puts them at different heights thereby truly seperating them. sure 2. standard pca decomposes into 2x2 while kernel pca decomposes into 5000 x 5000. sure\nfor hidden stuff, i think basically all of it."*
   - **Verdict:** `PASS` (verifier agreed; geometric non-separability and vertical height separation correctly articulated; matrix sizes $2 \times 2$ vs $5000 \times 5000$ accurately stated).

## Attempts (ops.py, already written in-session)

- `PCA (Dimensionality Reduction)` — 2026-10-20:
  - pass `explain-back` (`sure`, 1 hint) — Pause exit ticket X1
  - Net: mastery **0.85** advisory, `interval_index` **3**, `last_reviewed` **2026-10-20**, `next_review` **2026-11-19**, `consecutive_correct` 2, `consecutive_wrong` 0, `Last Q Type` **explain-back**.

## Mistakes candidates

- None (`mistakes: []`). No errors on the exit ticket; the Socratic ladder was guided smoothly.

## Dependency events

- None (`just_tell_me`: 0, `told_repair`: 0, `declined_generation`: 0). All answers produced by the learner.

## Learner pacing & next session focus

- Paused mid-Checkpoint 6 at mini 1/3 per learner request.
- 2D-to-3D lifting intuition and matrix size anchor ($2 \times 2$ vs $5000 \times 5000$) are solid.
- Learner noted that "hidden stuff" feels fuzzy. Next session will slow down and unpack the hidden mechanics step-by-step:
  1. Centering the $n \times n$ similarity table $K$ in feature space.
  2. Why eigenvectors of $K$ act as low-dimensional coordinates.
  3. The $1/\sqrt{\lambda}$ scaling factor.
  4. The pre-image problem with a small 3-point toy walkthrough.
