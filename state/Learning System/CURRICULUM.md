# Curriculum — AI Engineering from Scratch (Rohit)

> Authoritative "what's next" map, aligned to **AI Engineering from Scratch** by Rohit Ghumare (https://github.com/rohitg00/ai-engineering-from-scratch).
> Source of truth for order is upstream `ROADMAP.md` (cached SHA at time of switch: `main` 2026-09-01). Rohit's `docs/en.md` per lesson is **a source, not the source** — Scout gathers `docs/en.md` + every link in its `## Further Reading` plus curated `RESOURCES.md` entries.
> One mission per roadmap phase (plus Mission 0 Catch-Up). Lessons within a mission are **sequential** — one at a time. Interleaving lives only in the review flow. One curriculum lesson = one runnable artifact (see Rohit "Every lesson ships something"). Status `not-started` → `in-progress` → `done`. A lesson is `done` only after practice + retrieval + Feynman explain-back.
> **Adaptive rule:** before each new lesson, Scout re-fetches the live `phases/<NN>-<phase>/<NN>-<lesson>/docs/en.md` and its Further Reading URLs, compares to cached hash, and surfaces any delta in `SCOUT DIGEST: ⚠️ Upstream changed`. Tutor prefers live combined sources over parametric memory. See `Learning System/MISSION.md` and `Skills/learning-teach/SKILL.md`.
> **Language rule:** build language per lesson follows Rohit's `Languages:` header (Python / TypeScript / Rust; Julia optional). Phase default is in the mission header; lesson-level overrides apply. See `RESOURCES.md`.
> **Scope note:** full 20-phase map is present for navigation; it is not a contract to finish end-to-end. After each phase, decide to go deeper / branch / build a learning system around a topic. Archived SWE roadmap: `Learning System/Archive/CURRICULUM — SWE Primary Colors — archived 2026-09-01.md` and wiki banner; `📦 Concept Archive.md` holds paused SWE rows (visibility strictly out of scope — Scout/Tutor do not grep it).

## Mission 0 — Catch-Up: Foundations Reactivation *(special · done)*

Goal: **80/20 reactivation** of everything up to and including **Phase 1, Lesson 06 — Probability & Distributions**. You did Phase 0 + P1.01–06 before (exercises done) but haven't reviewed in weeks. This lesson rebuilds the 20% that unlocks 80% of later phases, probes for gaps, and sets `next` to Phase 1 Lesson 07.

- **Source:** Phase 0 (12 lessons) + Phase 1 L01–L06 synthesized from Rohit `phases/00-setup-and-tooling/*/docs/en.md` + `phases/01-math-foundations/01-*` through `06-probability-and-distributions/docs/en.md` plus each lesson's `## Further Reading` (external).
- **Lang:** Python (Julia notes for L01 where Rohit lists it, but Python-first).
- **Probe:** 6–8 MCQs + 2 free-recall, broad→narrow, confidence-tagged, `quiz-audit` gated — locate edge per strand (tooling / linear algebra / calculus / probability).
- **80/20 map (taught in this catch-up):**
  - **Tooling mental model:** 4-layer stack (System → Packages → Runtimes → AI libs); `uv`/`venv`, `verify.py --route`, `nvidia-smi` vs `torch.cuda.is_available()` / MPS, `.env` + `.gitignore` for keys.
  - **Vectors/Matrices:** vectors as points, magnitude, dot product = similarity, matrices as transforms, shape `(m×n)@(n×p)`, broadcast `W@x+b`, dense layer `relu(Wx+b)`, rank/basis intuition.
  - **Transformations/Eigen:** rotate/scale/shear, composition non-commutative, determinants as volume scale, `Av=λv` as fixed directions.
  - **Calculus substrate:** derivatives/gradients, chain rule as engine for backprop, autodiff forward vs reverse intuition.
  - **Probability core:** axioms, conditional `P(A|B)`, independence, **PMF vs PDF**, Bernoulli/Categorical/Normal (68/95/99.7), `E[X]` / `Var = E[X²]-μ²`, **CLT = why normals dominate**, log-probs & `log-sum-exp` trick, **softmax (subtract-max) + cross-entropy = −log P(correct)**.

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 0 | Catch-Up: 80/20 Foundations (Tooling → Probability, P0 + P1.01–06) | ~90 min | none | Python | done | Special reactivation. Probe first, then teach gaps. On pass → jump to Phase 1 L07. Source: P0–P1.06 `docs/en.md` + Further Reading synthesis. |

**Exit:** you can state the 4-layer env stack, explain `Wx+b` with shapes, distinguish PMF/PDF, and derive cross-entropy from NLL without notes.

## Mission 1 — Phase 0: Setup & Tooling *(~14 hours · Python / Node / Rust · not-started)*

Goal: Setup & Tooling — see upstream `phases/00-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Phase note:** covered by Mission 0 catch-up (reactivation) — lessons below remain `not-started` individually; skip or retrieval-check on demand.
- **Lang (phase default):** Python / Node / Rust — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/00-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Dev Environment | ~75 min | none | Python | not-started | Source: Phase 0 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 02 | Git & Collaboration | ~45 min | 1 | Python | not-started | Source: Phase 0 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 03 | GPU Setup & Cloud | ~75 min | 2 | Python | not-started | Source: Phase 0 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 04 | APIs & Keys | ~75 min | 3 | Python | not-started | Source: Phase 0 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 05 | Jupyter Notebooks | ~75 min | 4 | Python | not-started | Source: Phase 0 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 06 | Python Environments | ~75 min | 5 | Python | not-started | Source: Phase 0 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 07 | Docker for AI | ~75 min | 6 | Python | not-started | Source: Phase 0 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 08 | Editor Setup | ~75 min | 7 | Python | not-started | Source: Phase 0 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 09 | Data Management | ~75 min | 8 | Python | not-started | Source: Phase 0 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 10 | Terminal & Shell | ~45 min | 9 | Python | not-started | Source: Phase 0 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 11 | Linux for AI | ~45 min | 10 | Python | not-started | Source: Phase 0 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |
| 12 | Debugging & Profiling | ~75 min | 11 | Python | not-started | Source: Phase 0 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python / Node / Rust). |

**Exit:** 4-layer env reproducible, `verify.py --route` passes, Docker/tooling not blocking future phases.

## Mission 2 — Phase 1: Math Foundations *(~23 hours · Python (Julia optional) · in-progress)*

Goal: Math Foundations — see upstream `phases/01-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Phase note:** L01–L06 covered by Mission 0 catch-up; L07 done 2026-09-05; L08 Optimization done 2026-09-10 (retrieval + Feynman pass); **L09 Information Theory done 2026-09-24** — CP1–CP6 banked (CP4 re-sealed; CP5 practice on a fresh joint I = 0.1187 bits with the sign slip caught by MI ≥ 0; CP5.5 variation of information consolidated; CP6 perplexity + bits/nats + label smoothing with both practice slips — nats-base-on-bits and ε=1-extreme — repaired in-session), Feynman explain-back passed on attempt 3, final cumulative quiz 5/6 (Q1 entropy unweighted-surprise slip repaired + isomorphic re-test pass at 1.75 bits); **L10 Dimensionality Reduction in-progress — paused at Checkpoint 6/6, mini 1/3 (Hidden Piece 1 sealed; Hidden Piece 2 in-progress — sealed Part 1: eigenvectors as coordinates via $(\tilde{K} \alpha_k)_i = \lambda_k \alpha_{k,i}$ re-anchored on 3-point toy cloud; resume at Part 2: $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and $1/\sqrt{\lambda_k}$ scaling, followed by Hidden Piece 3: pre-image problem as a story and inverse transform).** CP6 mini 1 paused 2026-10-23 (Pause Exit Ticket X1 passed on repair; Hidden Piece 2 Part 1 re-anchored on concrete 3-point toy cloud: projection dot products yielding Row 1 of $\tilde{K}$ and coordinate extraction via $\tilde{K}\alpha = \lambda\alpha$; 2026-10-22 Hidden Piece 2 Part 1 opened/sealed via dual representation $v_k = \sum_{j=1}^n \alpha_{k,j} \tilde{\phi}(x_j)$; 2026-10-21 Hidden Piece 1 sealed: Kernel PCA centering in feature space via double-centering formula $\tilde{K} = (I - \mathbf{1}_n) K (I - \mathbf{1}_n)$ and RBF shift cancellation; 2026-10-20 lifting geometry and $2 \times 2$ vs $5000 \times 5000$ matrix size distinction established); resume Checkpoint 6/6, mini 1/3: Kernel PCA with an RBF kernel (Hidden Piece 1 sealed; Hidden Piece 2 Part 1 sealed; resume at Part 2: $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and $1/\sqrt{\lambda_k}$ scaling, followed by Hidden Piece 3: pre-image problem as a story and inverse transform); CP5 fully SEALED 2026-10-19 (mini 5b scaling taught, CP5 practice batch 4/4 passed; exit ticket X1 completed with mechanical distinction correct) (CP5 mini 4 sealed 2026-10-17; minis 2–3 sealed 2026-10-14; mini 1 sealed 2026-10-13; CP4 fully sealed 2026-10-12; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30) (probe 7/9; CP1 sealed 2026-09-30 — mini 2 variance bookkeeping by hand (4 / 0.75 / 1.5), the det(C−λI)=0 roots 4.59 / 0.16, the eigenbasis diagonalization, the integrative practice λ = 10 / 0, pause exit ticket 2/3 with the eigenbasis-diagonal label slip repaired in-session); CP2 minis 1–2 sealed 2026-10-02 (the 5-step recipe center → covariance → eigenvectors → sort by λ → project, plus the cov/eigh/sort/slice/project lines; exit ticket X1/X2 PASS, X3 FAIL on the eigh output layout → repaired with the shape detector); CP2 mini 3 sealed 2026-10-03 (the full class assembled line-by-line and raced vs sklearn — tie up to sign, explained variance 4.98024987 both arms, signed max gap 13.2 = 2× the biggest coordinate, magnitude gap 8.9e-16; the one slip — the `np.cov` `rowvar=True` default stated backwards — repaired in-turn and locked by exit ticket X3); CP4 mini 1 sealed 2026-10-08 (t-SNE neighborhoods — goal + Rohit's pair-probability mechanism + the false-neighbour failure of linear squashes, with the Distill-vs-Rohit attribution fix; plus the anomaly-detector tangent: shape-vs-depth, the stacked depth check, unit-vs-signal; pause exit ticket 3/3 all sure) — CP4 minis 2 + 3/3b sealed 2026-10-09 (perplexity = the banked `2^H` applied per point — `Per(P_i) = 2^{H(P_i)}`, `σ_i` tuned per point, an effective soft count, typical 5–50, ceiling `n−1`; the objective = `min KL(P‖Q)` with `P` frozen and `Q` the only mover; the heavy-tailed Student-t `Q` keeps `Q_i` from collapsing so the crowded medium band can spread — JMLR "mismatched tails compensate for mismatched dimensionalities"; the learner's flipped reason — product vs the `P`-weighted log-ratio — repaired in-session) — resume: **Checkpoint 6/6, mini 1/3: Kernel PCA with an RBF kernel (Hidden Piece 1 sealed; Hidden Piece 2 in-progress — sealed Part 1: eigenvectors as coordinates via $(\tilde{K} \alpha_k)_i = \lambda_k \alpha_{k,i}$ re-anchored on 3-point toy cloud; resume at Part 2: $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and $1/\sqrt{\lambda_k}$ scaling, followed by Hidden Piece 3: pre-image problem as a story and inverse transform)**: the fresh 2026-10-23 digest is kept, inside its 7-day TTL, audited PASS — CP4 mini 4 is sealed 2026-10-10 (the misreading protocol + the resolved ⚠️ Rohit-vs-Distill scope split) — CP2's practice was sealed 2026-10-05 as a paper walk (rows (1,0), (5,2), (3,4), k=1 → mean (3,2), C = [[4,2],[2,4]] after the ÷n → ÷(n−1) repair, λ = 6 / 2, kept fraction λ_top/Σλ = 6/8 = 3/4), and the from-memory code write is off the books entirely per the learner's 2026-10-05 rule (paper walks or graded MCQ batches; the parked code-write integration folds into the final cumulative quiz) → CP3 … CP6 → final cumulative quiz + Feynman.
- **Lang (phase default):** Python (Julia optional) — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/01-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Linear Algebra Intuition | ~45 min | none | Python (Julia optional) | not-started* | Covered by Mission 0 catch-up (80/20). Ritual: retrieval-check on demand, not re-taught unless probe fails. Source: P1 L01 `docs/en.md`. |
| 02 | Vectors, Matrices & Operations | ~75 min | 1 | Python (Julia optional) | not-started* | Covered by Mission 0 catch-up (80/20). Ritual: retrieval-check on demand, not re-taught unless probe fails. Source: P1 L02 `docs/en.md`. |
| 03 | Matrix Transformations & Eigenvalues | ~75 min | 2 | Python (Julia optional) | not-started* | Covered by Mission 0 catch-up (80/20). Ritual: retrieval-check on demand, not re-taught unless probe fails. Source: P1 L03 `docs/en.md`. |
| 04 | Calculus for ML — Derivatives & Gradients | ~45 min | 3 | Python (Julia optional) | not-started* | Covered by Mission 0 catch-up (80/20). Ritual: retrieval-check on demand, not re-taught unless probe fails. Source: P1 L04 `docs/en.md`. |
| 05 | Chain Rule & Automatic Differentiation | ~75 min | 4 | Python (Julia optional) | not-started* | Covered by Mission 0 catch-up (80/20). Ritual: retrieval-check on demand, not re-taught unless probe fails. Source: P1 L05 `docs/en.md`. |
| 06 | Probability & Distributions | ~45 min | 5 | Python (Julia optional) | not-started* | Covered by Mission 0 catch-up (80/20). Ritual: retrieval-check on demand, not re-taught unless probe fails. Source: P1 L06 `docs/en.md`. |
| 07 | Bayes' Theorem & Statistical Thinking | ~75 min | 6 | Python (Julia optional) | done | Taught 2026-09-02, re-activated 2026-09-05 (retrieval + Feynman pass). Est ~75 min (from ROADMAP). Scout fetches live docs + Further Reading; language per Rohit header (Python for P1). |
| 08 | Optimization — Gradient Descent Family | ~75 min | 7 | Python (Julia optional) | done | CP1–5 + SHIP + cumulative quiz (6/6) + Feynman pass. 2026-09-10. | Source: Phase 1 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 09 | Information Theory — Entropy, KL Divergence | ~45 min | 8 | Python (Julia optional) | done | **Done 2026-09-24.** CP1–CP6 banked: information content + entropy (incl. the unweighted-surprise repair), cross-entropy/floor, KL divergence (identity + Gibbs/Jensen re-digest + rebate/cost), mutual information (four forms + KL connection + nonnegativity + fresh-joint practice with the sign slip caught by MI ≥ 0), variation of information (true metric per Meilă 2003/2007), CP6 perplexity + bits/nats + label smoothing (both practice slips repaired in-session). Feynman explain-back pass (attempt 3); final cumulative quiz 5/6 (Q1 entropy slip repaired + isomorphic re-test 1.75 bits). New concepts: Perplexity, Bits vs Nats, Label Smoothing (Logits & log-odds supporting page). Next: L10 Dimensionality Reduction. Source: Phase 1 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 10 | Dimensionality Reduction — PCA, t-SNE, UMAP | ~75 min | 9 | Python (Julia optional) | in-progress | **Paused at Checkpoint 6/6, mini 1/3 — Hidden Piece 1 sealed 2026-10-21; Hidden Piece 2 in-progress — sealed Part 1 2026-10-22 and re-anchored on 3-point toy cloud 2026-10-23: eigenvectors as coordinates via $(\tilde{K} \alpha_k)_i = \lambda_k \alpha_{k,i}$; Pause Exit Ticket X1 passed on repair; resume at Part 2: $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and $1/\sqrt{\lambda_k}$ scaling, followed by Hidden Piece 3: pre-image problem as a story and inverse transform; CP5 fully SEALED 2026-10-19** (CP5 mini 4 sealed 2026-10-17; minis 2–3 sealed 2026-10-14; mini 1 sealed 2026-10-13; CP4 fully sealed 2026-10-12; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30) — probe 7/9 (curse of dimensionality unknown/new; centering-orthogonality slip repaired in-session; PMF-vs-PDF label regression). CP1 sealed in the 2026-09-30 resume session: mini 2 delivered in slow-down mode (variance bookkeeping by hand 4/0.75/1.5 after two self-located arithmetic repairs; det(C−λI)=0 → λ = 4.59/0.16 on the 4/1.5/0.75 matrix; eigenbasis diagonalization — the off-diagonal goes to exactly 0 and the diagonal entries are the λ's; standalone viz turn, viz-audit PASS), integrative practice C = [[8,4],[4,2]] → λ = 10/0 with the λ=0-is-a-line correction, pause exit ticket 2/3 (X3 eigenbasis-diagonal label slip repaired in-session). CP2 minis 1–2 sealed 2026-10-02: the 5-step recipe (center → covariance → eigenvectors → sort by λ → project) and the why of each, then the code piece by piece (`C = np.cov(Xc, rowvar=False)` d×d with n only via 1/(n−1); `np.linalg.eigh` ascending with eigenvectors as columns; `order = vals.argsort()[::-1]`; `V = vecs[:, order[:k]]` d×k; `Xp = Xc @ V` n×k; eigenvector sign reflection, sklearn `svd_flip` cosmetic); pause exit ticket X1/X2 PASS, X3 FAIL (`argsort()[:, :-1]` for `[::-1]`, `vecs` called n×d with its rows mapped to the projected points) → repaired with the told-answer shape detector (has-n ⇒ points possible; all-d ⇒ directions only); new `PCA (Dimensionality Reduction)` row + structural Mistakes row. CP2 mini 3 sealed 2026-10-03: the full `MyPCA` class assembled (taught line-by-line — the learner does not write code in chat) and raced against `sklearn.decomposition.PCA(n_components=1)` on a seeded cloud (seed=3, n=200, cov [[4,2],[2,1.5]], k=1) — explained variance 4.98024987 identical on both arms, components exact sign flips, max signed coordinate gap 13.2 = 2× the biggest coordinate (label mirror, not error), magnitude gap 8.9e-16 ⇒ **tie up to sign**; warm-up W1–W3 PASS; line-by-line (a) FAIL — the `np.cov` default (`rowvar=True`, rows-as-variables) stated backwards — repaired in-turn and locked by exit ticket X3 (A, sure); (b)/(c)/(d) PASS; learner-initiated pokes sealed (the 13.2 reading as 2× the biggest coordinate = cloud size; sign-sensitive thresholds restated as |score|; variance = average of squared deviations ⇒ uᵀCu ⇒ PSD ⇒ eigenvalues ≥ 0). New durable learner preference: no code written in chat (from-memory builds happen in the learner's own environment, reported as artifacts/prose). CP2's single practice was **sealed 2026-10-05 as a paper walk** (rows (1,0), (5,2), (3,4), k=1 → mean (3,2), C = [[4,2],[2,4]] after the ÷n → ÷(n−1) repair, λ = 6 / 2, top axis λ = 6, kept fraction repaired to λ_top/Σλ = 6/8 = 3/4; off-diagonal/variance relapse repaired with the self-dot ⇒ diagonal detector); the from-memory code write is off the books entirely per the learner's 2026-10-05 rule (paper walks or graded MCQ batches; the parked integration folds into the final cumulative quiz). CP3 sealed 2026-10-07 (minis 1–5 + the paper-walk practice): choosing k (ratio λ/Σλ, elbow convention — the first bar whose incoming drop is small, keep the bars before it; reconstruction error = Σ of the dropped λ's), PCA as an anomaly detector (per-sample error = Σ(coordinate)² along the dropped axes; along = normal / across = suspect), the round cloud (λI ⇒ every direction an eigenvector, flat scree, no bar droppable under 95% — compression needs unequal spread), the curse-of-dimensionality thread (distance concentration; the trace pie Σλ fixed under rotation); practice kept 37/40 & error 6, outlier 5.7 vs < 0.3, elbow k = 3 with the 95% rule agreeing. CP4 mini 1 sealed 2026-10-08: t-SNE neighborhoods (goal = preserve which points are near each other — Rohit: "Points that were neighbors in 784 dimensions stay neighbors in 2D"; the pair-probability mechanism is already in Rohit's source, Distill's distinctive add is the interpretation-caution layer; a linear squash never tears true neighbours apart but collapses distinct regions into **false neighbours**) + the anomaly-detector tangent (shape-vs-depth, the stacked depth check, unit-vs-signal, directions-vs-points; warm-up W2 frame-inversion repaired in-session, pause exit ticket 3/3 all sure); new wiki page `t-SNE (Dimensionality Reduction)` and new Active Concepts row. CP4 minis 2 + 3/3b sealed 2026-10-09: perplexity = the banked `2^H` applied to each point's neighbour distribution (`Per(P_i) = 2^{H(P_i)}`, `σ_i` tuned until the knob is met; an *effective* soft count, not a cutoff; typical 5–50; the ceiling `n−1` — 20 points ⇒ ≤ 19 — is the precise break behind Distill's "smaller than the number of points"), the objective = **minimize** `KL(P‖Q)` (never zero; `P` frozen, `Q` the only mover via gradient descent on the 2D coordinates; the weights come from `P`, so "data says near, map says far" is the expensive mismatch), and the heavy-tailed Student-t `Q` (a Gaussian fines every escape as `Q_i → 0` at distance; the fat tail keeps `Q_i` up so spreading is affordable and the crowded medium band gets room without tearing true neighbourhoods — JMLR "mismatched tails compensate for mismatched dimensionalities"); the learner's conclusion was right with a flipped reason (product `P×Q` vs the `P`-weighted log-ratio), repaired in-session to the log-ratio; warm-up 3/3 + the pause exit ticket 3/3 (2026-10-09) and the 2026-10-10 warm-up + re-walk micro-check, all sure, 0 hints; **misreading protocol sealed 2026-10-10** (cluster sizes meaningless — an apparent size is the map-internal spread of the 2-D coordinates, and one plot carries ONE user-set perplexity target; cluster distances mean little at an untuned perplexity — cross-cluster pairs carry `P_ij ≈ 0` so their fine is ≈ 0 under any separation, leaving the gap to the optimizer with no guaranteed direction — with the fragile exception that a perplexity tuned to the data's natural cluster structure makes inter-cluster distances *somewhat* meaningful) and the **⚠️ Rohit-vs-Distill contradiction resolved** (Rohit = safe default rule; Distill = fragile exception needing a deliberate tuning experiment); the 3b re-walk he requested on 2026-10-09 was delivered and sealed with his own computed fine (P = 0.2, Q = 0.001 → 0.2·log₂200 ≈ 1.53 bits) — **pacing call closed 2026-10-10**. Resume: **Checkpoint 6/6, mini 1/3: Kernel PCA with an RBF kernel (Hidden Piece 1 sealed; Hidden Piece 2 in-progress — sealed Part 1: eigenvectors as coordinates via $(\tilde{K} \alpha_k)_i = \lambda_k \alpha_{k,i}$ re-anchored on 3-point toy cloud; resume at Part 2: $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and $1/\sqrt{\lambda_k}$ scaling, followed by Hidden Piece 3: pre-image problem as a story and inverse transform)**: the fresh 2026-10-23 digest is kept, inside its 7-day TTL, audited PASS; CP4's practice closed 2026-10-12 (4/4 + pause exit ticket 3/3, all `sure`) with the kernel deep-dive sealed alongside it, CP6 and the final cumulative quiz + Feynman. Source: Phase 1 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 11 | Singular Value Decomposition | ~75 min | 10 | Python (Julia optional) | not-started | Source: Phase 1 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 12 | Tensor Operations | ~75 min | 11 | Python (Julia optional) | not-started | Source: Phase 1 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 13 | Numerical Stability | ~45 min | 12 | Python (Julia optional) | not-started | Source: Phase 1 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 14 | Norms & Distances | ~45 min | 13 | Python (Julia optional) | not-started | Source: Phase 1 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 15 | Statistics for ML | ~45 min | 14 | Python (Julia optional) | not-started | Source: Phase 1 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 16 | Sampling Methods | ~75 min | 15 | Python (Julia optional) | not-started | Source: Phase 1 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 17 | Linear Systems | ~75 min | 16 | Python (Julia optional) | not-started | Source: Phase 1 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 18 | Convex Optimization | ~75 min | 17 | Python (Julia optional) | not-started | Source: Phase 1 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 19 | Complex Numbers for AI | ~45 min | 18 | Python (Julia optional) | not-started | Source: Phase 1 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 20 | The Fourier Transform | ~75 min | 19 | Python (Julia optional) | not-started | Source: Phase 1 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 21 | Graph Theory for ML | ~45 min | 20 | Python (Julia optional) | not-started | Source: Phase 1 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |
| 22 | Stochastic Processes | ~45 min | 21 | Python (Julia optional) | not-started | Source: Phase 1 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python (Julia optional)). |

**Exit:** calculus → probability chain solid; you can implement PMF/PDF, softmax + NLL, and state CLT without notes. Continue Phase 1 at L10 (Dimensionality Reduction — PCA, t-SNE, UMAP; in-progress — paused at Checkpoint 6/6, mini 1/3 — Hidden Piece 1 sealed 2026-10-21; Hidden Piece 2 in-progress — sealed Part 1 2026-10-22: eigenvectors as coordinates via $(\tilde{K} \alpha_k)_i = \lambda_k \alpha_{k,i}$; resume at Part 2: $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and $1/\sqrt{\lambda_k}$ scaling, followed by Hidden Piece 3: pre-image problem with a small 3-point toy walkthrough; CP5 fully SEALED 2026-10-19; resume: **Checkpoint 6/6, mini 1/3: Kernel PCA with an RBF kernel (Hidden Piece 1 sealed; Hidden Piece 2 in-progress — sealed Part 1: eigenvectors as coordinates via $(\tilde{K} \alpha_k)_i = \lambda_k \alpha_{k,i}$; resume at Part 2: $\|v_k\|_\mathcal{H}^2 = \alpha_k^T \tilde{K} \alpha_k = \lambda_k$ and $1/\sqrt{\lambda_k}$ scaling, followed by Hidden Piece 3: pre-image problem)** (the fresh 2026-10-20 digest is kept, inside its 7-day TTL through 2026-10-27, audited PASS)).

## Mission 3 — Phase 2: ML Fundamentals *(~21 hours · Python · not-started)*

Goal: ML Fundamentals — see upstream `phases/02-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/02-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | What Is Machine Learning — Types & Taxonomy | ~45 min | none | Python | not-started | Source: Phase 2 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | Linear Regression from Scratch | ~75 min | 1 | Python | not-started | Source: Phase 2 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | Logistic Regression & Classification | ~75 min | 2 | Python | not-started | Source: Phase 2 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | Decision Trees & Random Forests | ~75 min | 3 | Python | not-started | Source: Phase 2 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | Support Vector Machines | ~75 min | 4 | Python | not-started | Source: Phase 2 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | K-Nearest Neighbors & Distance Metrics | ~75 min | 5 | Python | not-started | Source: Phase 2 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | Unsupervised Learning — K-Means, DBSCAN | ~75 min | 6 | Python | not-started | Source: Phase 2 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | Feature Engineering & Selection | ~75 min | 7 | Python | not-started | Source: Phase 2 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Model Evaluation — Metrics, Cross-Validation | ~75 min | 8 | Python | not-started | Source: Phase 2 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | Bias, Variance & the Learning Curve | ~45 min | 9 | Python | not-started | Source: Phase 2 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Ensemble Methods — Boosting, Bagging, Stacking | ~75 min | 10 | Python | not-started | Source: Phase 2 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | Hyperparameter Tuning & AutoML | ~75 min | 11 | Python | not-started | Source: Phase 2 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 13 | ML Pipelines & Experiment Tracking | ~75 min | 12 | Python | not-started | Source: Phase 2 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 14 | Naive Bayes — Multinomial, Gaussian, Bernoulli | ~75 min | 13 | Python | not-started | Source: Phase 2 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 15 | Time Series Fundamentals | ~45 min | 14 | Python | not-started | Source: Phase 2 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 16 | Anomaly Detection | ~75 min | 15 | Python | not-started | Source: Phase 2 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 17 | Handling Imbalanced Data | ~75 min | 16 | Python | not-started | Source: Phase 2 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 18 | Feature Selection | ~75 min | 17 | Python | not-started | Source: Phase 2 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for ML Fundamentals exit criteria.

## Mission 4 — Phase 3: Deep Learning Core *(~15 hours · Python · not-started)*

Goal: Deep Learning Core — see upstream `phases/03-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/03-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | The Perceptron — Where It All Started | ~45 min | none | Python | not-started | Source: Phase 3 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | Multi-Layer Networks & Forward Pass | ~75 min | 1 | Python | not-started | Source: Phase 3 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | Backpropagation from Scratch | ~75 min | 2 | Python | not-started | Source: Phase 3 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | Activation Functions — ReLU, Sigmoid, GELU & Why | ~45 min | 3 | Python | not-started | Source: Phase 3 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | Loss Functions — MSE, Cross-Entropy, Contrastive | ~45 min | 4 | Python | not-started | Source: Phase 3 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | Optimizers — SGD, Momentum, Adam, AdamW | ~75 min | 5 | Python | not-started | Source: Phase 3 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | Regularization — Dropout, Weight Decay, BatchNorm | ~75 min | 6 | Python | not-started | Source: Phase 3 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | Weight Initialization & Training Stability | ~45 min | 7 | Python | not-started | Source: Phase 3 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Learning Rate Schedules & Warmup | ~45 min | 8 | Python | not-started | Source: Phase 3 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | Build Your Own Mini Framework | ~120 min | 9 | Python | not-started | Source: Phase 3 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Introduction to PyTorch | ~75 min | 10 | Python | not-started | Source: Phase 3 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | Introduction to JAX | ~75 min | 11 | Python | not-started | Source: Phase 3 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 13 | Debugging Neural Networks | ~75 min | 12 | Python | not-started | Source: Phase 3 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for Deep Learning Core exit criteria.

## Mission 5 — Phase 4: Computer Vision *(~27 hours · Python · not-started)*

Goal: Computer Vision — see upstream `phases/04-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/04-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Image Fundamentals — Pixels, Channels, Color Spaces | ~45 min | none | Python | not-started | Source: Phase 4 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | Convolutions from Scratch | ~75 min | 1 | Python | not-started | Source: Phase 4 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | CNNs — LeNet to ResNet | ~75 min | 2 | Python | not-started | Source: Phase 4 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | Image Classification | ~75 min | 3 | Python | not-started | Source: Phase 4 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | Transfer Learning & Fine-Tuning | ~75 min | 4 | Python | not-started | Source: Phase 4 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | Object Detection — YOLO from Scratch | ~75 min | 5 | Python | not-started | Source: Phase 4 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | Semantic Segmentation — U-Net | ~75 min | 6 | Python | not-started | Source: Phase 4 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | Instance Segmentation — Mask R-CNN | ~75 min | 7 | Python | not-started | Source: Phase 4 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Image Generation — GANs | ~75 min | 8 | Python | not-started | Source: Phase 4 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | Image Generation — Diffusion Models | ~75 min | 9 | Python | not-started | Source: Phase 4 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Stable Diffusion — Architecture & Fine-Tuning | ~75 min | 10 | Python | not-started | Source: Phase 4 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | Video Understanding — Temporal Modeling | ~45 min | 11 | Python | not-started | Source: Phase 4 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 13 | 3D Vision — Point Clouds, NeRFs | ~45 min | 12 | Python | not-started | Source: Phase 4 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 14 | Vision Transformers (ViT) | ~45 min | 13 | Python | not-started | Source: Phase 4 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 15 | Real-Time Vision — Edge Deployment | ~75 min | 14 | Python | not-started | Source: Phase 4 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 16 | Build a Complete Vision Pipeline | ~120 min | 15 | Python | not-started | Source: Phase 4 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 17 | Self-Supervised Vision — SimCLR, DINO, MAE | ~75 min | 16 | Python | not-started | Source: Phase 4 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 18 | Open-Vocabulary Vision — CLIP | ~45 min | 17 | Python | not-started | Source: Phase 4 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 19 | OCR & Document Understanding | ~45 min | 18 | Python | not-started | Source: Phase 4 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 20 | Image Retrieval & Metric Learning | ~45 min | 19 | Python | not-started | Source: Phase 4 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 21 | Keypoint Detection & Pose Estimation | ~45 min | 20 | Python | not-started | Source: Phase 4 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 22 | 3D Gaussian Splatting from Scratch | ~90 min | 21 | Python | not-started | Source: Phase 4 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 23 | Diffusion Transformers & Rectified Flow | ~75 min | 22 | Python | not-started | Source: Phase 4 L23 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 24 | SAM 3 & Open-Vocabulary Segmentation | ~60 min | 23 | Python | not-started | Source: Phase 4 L24 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 25 | Vision-Language Models (ViT-MLP-LLM) | ~75 min | 24 | Python | not-started | Source: Phase 4 L25 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 26 | Monocular Depth & Geometry Estimation | ~60 min | 25 | Python | not-started | Source: Phase 4 L26 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 27 | Multi-Object Tracking & Video Memory | ~60 min | 26 | Python | not-started | Source: Phase 4 L27 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 28 | World Models & Video Diffusion | ~75 min | 27 | Python | not-started | Source: Phase 4 L28 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for Computer Vision exit criteria.

## Mission 6 — Phase 5: NLP *(~30 hours · Python · not-started)*

Goal: NLP — see upstream `phases/05-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/05-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Text Processing — Tokenization, Stemming, Lemmatization | ~45 min | none | Python | not-started | Source: Phase 5 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | Bag of Words, TF-IDF & Text Representation | ~75 min | 1 | Python | not-started | Source: Phase 5 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | Word Embeddings — Word2Vec from Scratch | ~75 min | 2 | Python | not-started | Source: Phase 5 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | GloVe, FastText & Subword Embeddings | ~45 min | 3 | Python | not-started | Source: Phase 5 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | Sentiment Analysis | ~75 min | 4 | Python | not-started | Source: Phase 5 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | Named Entity Recognition (NER) | ~75 min | 5 | Python | not-started | Source: Phase 5 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | POS Tagging & Syntactic Parsing | ~45 min | 6 | Python | not-started | Source: Phase 5 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | Text Classification — CNNs & RNNs for Text | ~75 min | 7 | Python | not-started | Source: Phase 5 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Sequence-to-Sequence Models | ~75 min | 8 | Python | not-started | Source: Phase 5 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | Attention Mechanism — The Breakthrough | ~45 min | 9 | Python | not-started | Source: Phase 5 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Machine Translation | ~75 min | 10 | Python | not-started | Source: Phase 5 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | Text Summarization | ~75 min | 11 | Python | not-started | Source: Phase 5 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 13 | Question Answering Systems | ~75 min | 12 | Python | not-started | Source: Phase 5 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 14 | Information Retrieval & Search | ~75 min | 13 | Python | not-started | Source: Phase 5 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 15 | Topic Modeling — LDA, BERTopic | ~45 min | 14 | Python | not-started | Source: Phase 5 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 16 | Text Generation — Language Models Before Transformers | ~45 min | 15 | Python | not-started | Source: Phase 5 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 17 | Chatbots — Rule-Based to Neural | ~75 min | 16 | Python | not-started | Source: Phase 5 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 18 | Multilingual NLP | ~45 min | 17 | Python | not-started | Source: Phase 5 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 19 | Subword Tokenization — BPE, WordPiece, Unigram, SentencePiece | ~60 min | 18 | Python | not-started | Source: Phase 5 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 20 | Structured Outputs & Constrained Decoding | ~60 min | 19 | Python | not-started | Source: Phase 5 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 21 | NLI & Textual Entailment | ~60 min | 20 | Python | not-started | Source: Phase 5 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 22 | Embedding Models Deep Dive | ~60 min | 21 | Python | not-started | Source: Phase 5 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 23 | Chunking Strategies for RAG | ~60 min | 22 | Python | not-started | Source: Phase 5 L23 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 24 | Coreference Resolution | ~60 min | 23 | Python | not-started | Source: Phase 5 L24 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 25 | Entity Linking & Disambiguation | ~60 min | 24 | Python | not-started | Source: Phase 5 L25 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 26 | Relation Extraction & Knowledge Graph Construction | ~60 min | 25 | Python | not-started | Source: Phase 5 L26 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 27 | LLM Evaluation — RAGAS, DeepEval, G-Eval | ~75 min | 26 | Python | not-started | Source: Phase 5 L27 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 28 | Long-Context Evaluation — NIAH, RULER, LongBench, MRCR | ~60 min | 27 | Python | not-started | Source: Phase 5 L28 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 29 | Dialogue State Tracking | ~75 min | 28 | Python | not-started | Source: Phase 5 L29 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for NLP exit criteria.

## Mission 7 — Phase 6: Speech & Audio *(~18 hours · Python · not-started)*

Goal: Speech & Audio — see upstream `phases/06-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/06-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Audio Fundamentals — Waveforms, Sampling, Fourier Transform | ~45 min | none | Python | not-started | Source: Phase 6 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | Spectrograms, Mel Scale & Audio Features | ~45 min | 1 | Python | not-started | Source: Phase 6 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | Audio Classification | ~75 min | 2 | Python | not-started | Source: Phase 6 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | Speech Recognition (ASR) | ~45 min | 3 | Python | not-started | Source: Phase 6 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | Whisper — Architecture & Fine-Tuning | ~75 min | 4 | Python | not-started | Source: Phase 6 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | Speaker Recognition & Verification | ~45 min | 5 | Python | not-started | Source: Phase 6 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | Text-to-Speech (TTS) | ~75 min | 6 | Python | not-started | Source: Phase 6 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | Voice Cloning & Voice Conversion | ~75 min | 7 | Python | not-started | Source: Phase 6 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Music Generation | ~75 min | 8 | Python | not-started | Source: Phase 6 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | Audio-Language Models | ~45 min | 9 | Python | not-started | Source: Phase 6 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Real-Time Audio Processing | ~75 min | 10 | Python | not-started | Source: Phase 6 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | Build a Voice Assistant Pipeline | ~120 min | 11 | Python | not-started | Source: Phase 6 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 13 | Neural Audio Codecs — EnCodec, SNAC, Mimi, DAC | ~60 min | 12 | Python | not-started | Source: Phase 6 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 14 | Voice Activity Detection & Turn-Taking | ~45 min | 13 | Python | not-started | Source: Phase 6 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 15 | Streaming Speech-to-Speech — Moshi, Hibiki | ~75 min | 14 | Python | not-started | Source: Phase 6 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 16 | Voice Anti-Spoofing & Audio Watermarking | ~75 min | 15 | Python | not-started | Source: Phase 6 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 17 | Audio Evaluation — WER, MOS, MMAU, Leaderboards | ~60 min | 16 | Python | not-started | Source: Phase 6 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for Speech & Audio exit criteria.

## Mission 8 — Phase 7: Transformers Deep Dive *(~14 hours · Python · not-started)*

Goal: Transformers Deep Dive — see upstream `phases/07-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/07-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Why Transformers — The Problems with RNNs | ~45 min | none | Python | not-started | Source: Phase 7 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | Self-Attention from Scratch | ~75 min | 1 | Python | not-started | Source: Phase 7 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | Multi-Head Attention | ~75 min | 2 | Python | not-started | Source: Phase 7 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | Positional Encoding — Sinusoidal, RoPE, ALiBi | ~45 min | 3 | Python | not-started | Source: Phase 7 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | The Full Transformer — Encoder + Decoder | ~75 min | 4 | Python | not-started | Source: Phase 7 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | BERT — Masked Language Modeling | ~45 min | 5 | Python | not-started | Source: Phase 7 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | GPT — Causal Language Modeling | ~75 min | 6 | Python | not-started | Source: Phase 7 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | T5, BART — Encoder-Decoder Models | ~45 min | 7 | Python | not-started | Source: Phase 7 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Vision Transformers (ViT) | ~45 min | 8 | Python | not-started | Source: Phase 7 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | Audio Transformers — Whisper Architecture | ~45 min | 9 | Python | not-started | Source: Phase 7 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Mixture of Experts (MoE) | ~45 min | 10 | Python | not-started | Source: Phase 7 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | KV Cache, Flash Attention & Inference Optimization | ~75 min | 11 | Python | not-started | Source: Phase 7 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 13 | Scaling Laws | ~45 min | 12 | Python | not-started | Source: Phase 7 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 14 | Build a Transformer from Scratch — The Capstone | ~120 min | 13 | Python | not-started | Source: Phase 7 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 15 | Attention Variants — Sliding Window, Sparse, Differential | ~60 min | 14 | Python | not-started | Source: Phase 7 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 16 | Speculative Decoding — Draft, Verify, Repeat | ~60 min | 15 | Python | not-started | Source: Phase 7 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for Transformers Deep Dive exit criteria.

## Mission 9 — Phase 8: Generative AI *(~14 hours · Python · not-started)*

Goal: Generative AI — see upstream `phases/08-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/08-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Generative Models — Taxonomy & History | ~45 min | none | Python | not-started | Source: Phase 8 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | Autoencoders & VAE | ~75 min | 1 | Python | not-started | Source: Phase 8 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | GANs — Generator vs Discriminator | ~75 min | 2 | Python | not-started | Source: Phase 8 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | Conditional GANs & Pix2Pix | ~75 min | 3 | Python | not-started | Source: Phase 8 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | StyleGAN | ~45 min | 4 | Python | not-started | Source: Phase 8 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | Diffusion Models — DDPM from Scratch | ~75 min | 5 | Python | not-started | Source: Phase 8 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | Latent Diffusion & Stable Diffusion | ~75 min | 6 | Python | not-started | Source: Phase 8 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | ControlNet, LoRA & Image Conditioning | ~75 min | 7 | Python | not-started | Source: Phase 8 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Inpainting, Outpainting & Image Editing | ~75 min | 8 | Python | not-started | Source: Phase 8 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | Video Generation | ~45 min | 9 | Python | not-started | Source: Phase 8 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Audio Generation | ~45 min | 10 | Python | not-started | Source: Phase 8 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | 3D Generation | ~45 min | 11 | Python | not-started | Source: Phase 8 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 13 | Flow Matching & Rectified Flows | ~45 min | 12 | Python | not-started | Source: Phase 8 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 14 | Evaluation — FID, CLIP Score, Human Preference | ~45 min | 13 | Python | not-started | Source: Phase 8 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 19 | Visual Autoregressive Modeling (VAR): Next-Scale Prediction | ~90 min | 14 | Python | not-started | Source: Phase 8 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for Generative AI exit criteria.

## Mission 10 — Phase 9: Reinforcement Learning *(~13 hours · Python · not-started)*

Goal: Reinforcement Learning — see upstream `phases/09-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/09-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | MDPs, States, Actions & Rewards | ~45 min | none | Python | not-started | Source: Phase 9 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | Dynamic Programming | ~75 min | 1 | Python | not-started | Source: Phase 9 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | Monte Carlo Methods | ~75 min | 2 | Python | not-started | Source: Phase 9 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | Temporal Difference — Q-Learning, SARSA | ~75 min | 3 | Python | not-started | Source: Phase 9 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | Deep Q-Networks (DQN) | ~75 min | 4 | Python | not-started | Source: Phase 9 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | Policy Gradient Methods — REINFORCE | ~75 min | 5 | Python | not-started | Source: Phase 9 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | Actor-Critic — A2C, A3C | ~75 min | 6 | Python | not-started | Source: Phase 9 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | Proximal Policy Optimization (PPO) | ~75 min | 7 | Python | not-started | Source: Phase 9 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Reward Modeling & RLHF | ~45 min | 8 | Python | not-started | Source: Phase 9 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | Multi-Agent RL | ~45 min | 9 | Python | not-started | Source: Phase 9 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Sim-to-Real Transfer | ~45 min | 10 | Python | not-started | Source: Phase 9 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | RL for Games | ~75 min | 11 | Python | not-started | Source: Phase 9 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for Reinforcement Learning exit criteria.

## Mission 11 — Phase 10: LLMs from Scratch *(~26 hours · Python · not-started)*

Goal: LLMs from Scratch — see upstream `phases/10-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/10-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Tokenizers — BPE, WordPiece, SentencePiece | ~45 min | none | Python | not-started | Source: Phase 10 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | Building a Tokenizer from Scratch | ~75 min | 1 | Python | not-started | Source: Phase 10 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | Data Pipelines for Pre-Training | ~75 min | 2 | Python | not-started | Source: Phase 10 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | Pre-Training a Mini GPT (124M) | ~120 min | 3 | Python | not-started | Source: Phase 10 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | Scaling — Distributed Training, FSDP, DeepSpeed | ~75 min | 4 | Python | not-started | Source: Phase 10 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | Instruction Tuning — SFT | ~75 min | 5 | Python | not-started | Source: Phase 10 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | RLHF — Reward Model + PPO Training | ~75 min | 6 | Python | not-started | Source: Phase 10 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | DPO — Direct Preference Optimization | ~75 min | 7 | Python | not-started | Source: Phase 10 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Constitutional AI & Self-Improvement | ~45 min | 8 | Python | not-started | Source: Phase 10 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | Evaluation — Benchmarks, Evals, LM Harness | ~75 min | 9 | Python | not-started | Source: Phase 10 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Quantization — INT8, GPTQ, AWQ, GGUF | ~75 min | 10 | Python | not-started | Source: Phase 10 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | Inference Optimization | ~75 min | 11 | Python | not-started | Source: Phase 10 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 13 | Building a Complete LLM Pipeline | ~120 min | 12 | Python | not-started | Source: Phase 10 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 14 | Open Models — Architecture Walkthroughs | ~45 min | 13 | Python | not-started | Source: Phase 10 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 15 | Speculative Decoding and EAGLE-3 | ~75 min | 14 | Python | not-started | Source: Phase 10 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 16 | Differential Attention (V2) | ~60 min | 15 | Python | not-started | Source: Phase 10 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 17 | Native Sparse Attention (DeepSeek NSA) | ~60 min | 16 | Python | not-started | Source: Phase 10 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 18 | Multi-Token Prediction (MTP) | ~60 min | 17 | Python | not-started | Source: Phase 10 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 19 | DualPipe Parallelism | ~60 min | 18 | Python | not-started | Source: Phase 10 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 20 | DeepSeek-V3 Architecture Walkthrough | ~75 min | 19 | Python | not-started | Source: Phase 10 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 21 | Jamba — Hybrid SSM-Transformer | ~60 min | 20 | Python | not-started | Source: Phase 10 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 22 | Async and Hogwild! Inference | ~60 min | 21 | Python | not-started | Source: Phase 10 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 25 | Speculative Decoding and EAGLE | ~75 min | 22 | Python | not-started | Source: Phase 10 L25 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 34 | Gradient Checkpointing and Activation Recomputation | ~70 min | 23 | Python | not-started | Source: Phase 10 L34 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for LLMs from Scratch exit criteria.

## Mission 12 — Phase 11: LLM Engineering *(~17 hours · Python / TypeScript · branched — L01 completed 2026-10-29 via a side interrogation; Phase 11 L03 opened 2026-11-09 as a second side interrogation; the sequential curriculum position is still Phase 1 L10 to finish)*

Goal: LLM Engineering — see upstream `phases/11-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python / TypeScript — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/11-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Prompt Engineering — Techniques & Patterns | ~45 min | none | Python | done | **Done 2026-10-29** — the interrogation opened on 2026-10-28 was finished: all five triage rows closed (row 4 eval/measurement layer — the harness holds expected + actual outputs and re-runs on every change, and the scorer is not the ruler; row 5 failure regime — over-specific role → fabrication on the data-support condition, CoT below ~100B → pollution-by-conditioning so one-shot wins); **v2 captured verbatim**, entailment check banked, `naive-student` clone PASS, sabotage battery closed. Unread remainder banked as later attack material: the harness code section past "build it", temperature/top-p mechanics, the prefill contradiction (real, version-bounded), PE2 meta-prompting limits, and Rohit's Johnny citation error (real). Branch lesson — the sequential curriculum position did not move; Phase 1 L10 is still where the sequence stands. Source: Phase 11 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 02 | Few-Shot, Chain-of-Thought, Tree-of-Thought | ~45 min | 1 | Python | not-started | Source: Phase 11 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 03 | Structured Outputs | ~75 min | 2 | Python | **in-progress** | **Branch interrogation 2026-11-09, PAUSED** (off-curriculum side interrogation; the sequential position stays Phase 1 L10). Taught + held: the app-needs-typed-data gap; the ladder as *where the constraint acts* (prompt → JSON mode → schema mode → masking, with masking the *mechanism* behind schema mode, not a fourth knob); the decider (parser state × schema → legal token set; mask + renormalise) vs Rohit's last-char rule; Pydantic → schema and Instructor → validate-and-retry. **Paused mid-repair, battery withheld:** row 4's closing fresh-surface discriminator at `{"product": "Sony", "price": 348}` FAILED (`[miss: discrimination]`); row 5 (failure-mode catchability split) unattacked; row 7 (provider schema subset) off-path; no graduation/clone; exit ticket declined. Resume `/continue` at the open discriminator. **47 live concepts.** **Lesson file + `/pause` marker on disk and reconciled (2026-11-09 finalize `/ingest`):** `Lessons/Lesson — Structured Outputs — 2026-11-09.md` (`Status: PAUSED — mid-repair`, `Resume from:` = the row-4 fresh-surface discriminator — verbatim agreement with the handoff's `status: paused` / `resume_from`); `Core/Pending Ingest.json` consumed and cleared; the 2026-11-09 Scout digest kept (partial close, inside its 7-day TTL). **Status stays `in-progress`** — paused mid-repair, v1's `[?]` blanks untouched, no graduation, no clone. The learning record is still owed (written at lesson close, not at a pause). Source: Phase 11 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 04 | Embeddings & Vector Representations | ~75 min | 3 | Python | not-started | Source: Phase 11 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 05 | Context Engineering | ~75 min | 4 | Python | not-started | Source: Phase 11 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 06 | RAG — Retrieval-Augmented Generation | ~75 min | 5 | Python | not-started | Source: Phase 11 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 07 | Advanced RAG | ~75 min | 6 | Python | not-started | Source: Phase 11 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 08 | Fine-Tuning with LoRA & QLoRA | ~75 min | 7 | Python | not-started | Source: Phase 11 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 09 | Function Calling & Tool Use | ~75 min | 8 | Python | not-started | Source: Phase 11 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 10 | Evaluation & Testing LLM Applications | ~45 min | 9 | Python | not-started | Source: Phase 11 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 11 | Caching, Rate Limiting & Cost Optimization | ~45 min | 10 | Python | not-started | Source: Phase 11 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 12 | Guardrails, Safety & Content Filtering | ~45 min | 11 | Python | not-started | Source: Phase 11 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 13 | Building a Production LLM Application | ~120 min | 12 | Python | not-started | Source: Phase 11 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 14 | Model Context Protocol (MCP) | ~75 min | 13 | Python | not-started | Source: Phase 11 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 15 | Prompt Caching & Context Caching | ~60 min | 14 | Python | not-started | Source: Phase 11 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |

**Exit:** see ROADMAP.md phase header for LLM Engineering exit criteria.

## Mission 13 — Phase 12: Multimodal AI *(~65 hours · Python / TypeScript / Rust · not-started)*

Goal: Multimodal AI — see upstream `phases/12-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python / TypeScript / Rust — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/12-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Vision Transformers and the Patch-Token Primitive | ~120 min | none | Python | not-started | Source: Phase 12 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 02 | CLIP and Contrastive Vision-Language Pretraining | ~180 min | 1 | Python | not-started | Source: Phase 12 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 03 | BLIP-2 and Q-Former as Modality Bridge | ~180 min | 2 | Python | not-started | Source: Phase 12 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 04 | Flamingo and Gated Cross-Attention | ~120 min | 3 | Python | not-started | Source: Phase 12 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 05 | LLaVA and Visual Instruction Tuning | ~180 min | 4 | Python | not-started | Source: Phase 12 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 06 | Any-Resolution Vision: Patch-n'-Pack and NaFlex | ~120 min | 5 | Python | not-started | Source: Phase 12 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 07 | Open-Weight VLM Recipes: What Actually Matters | ~180 min | 6 | Python | not-started | Source: Phase 12 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 08 | LLaVA-OneVision: Single, Multi, Video | ~180 min | 7 | Python | not-started | Source: Phase 12 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 09 | Qwen-VL Family and Dynamic-FPS Video | ~120 min | 8 | Python | not-started | Source: Phase 12 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 10 | InternVL3 Native Multimodal Pretraining | ~120 min | 9 | Python | not-started | Source: Phase 12 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 11 | Chameleon and Early-Fusion Token-Only | ~180 min | 10 | Python | not-started | Source: Phase 12 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 12 | Emu3 Next-Token Prediction for Generation | ~120 min | 11 | Python | not-started | Source: Phase 12 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 13 | Transfusion Autoregressive + Diffusion | ~180 min | 12 | Python | not-started | Source: Phase 12 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 14 | Show-o and Discrete-Diffusion Unified | ~120 min | 13 | Python | not-started | Source: Phase 12 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 15 | Janus-Pro Decoupled Encoders | ~120 min | 14 | Python | not-started | Source: Phase 12 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 16 | MIO Any-to-Any Streaming | ~120 min | 15 | Python | not-started | Source: Phase 12 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 17 | Video-Language Temporal Grounding | ~180 min | 16 | Python | not-started | Source: Phase 12 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 18 | Long-Video Understanding at Million-Token Context | ~180 min | 17 | Python | not-started | Source: Phase 12 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 19 | Audio-Language Models: Whisper to AF3 | ~180 min | 18 | Python | not-started | Source: Phase 12 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 20 | Omni Models: Thinker-Talker | ~180 min | 19 | Python | not-started | Source: Phase 12 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 21 | Embodied VLAs: RT-2, OpenVLA, π0, GR00T | ~180 min | 20 | Python | not-started | Source: Phase 12 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 22 | Document and Diagram Understanding | ~180 min | 21 | Python | not-started | Source: Phase 12 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 23 | ColPali Vision-Native Document RAG | ~180 min | 22 | Python | not-started | Source: Phase 12 L23 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 24 | Multimodal RAG and Cross-Modal Retrieval | ~180 min | 23 | Python | not-started | Source: Phase 12 L24 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 25 | Multimodal Agents and Computer-Use (Capstone) | ~240 min | 24 | Python | not-started | Source: Phase 12 L25 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |

**Exit:** see ROADMAP.md phase header for Multimodal AI exit criteria.

## Mission 14 — Phase 13: Tools & Protocols *(~43 hours · TypeScript / Python · not-started)*

Goal: Tools & Protocols — see upstream `phases/13-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** TypeScript / Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/13-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | The Tool Interface | ~45 min | none | TypeScript | not-started | Source: Phase 13 L01 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 02 | Function Calling Deep Dive | ~75 min | 1 | TypeScript | not-started | Source: Phase 13 L02 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 03 | Parallel and Streaming Tool Calls | ~75 min | 2 | TypeScript | not-started | Source: Phase 13 L03 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 04 | Structured Output | ~75 min | 3 | TypeScript | not-started | Source: Phase 13 L04 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 05 | Tool Schema Design | ~45 min | 4 | TypeScript | not-started | Source: Phase 13 L05 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 06 | MCP Fundamentals: Stateless Requests and JSON-RPC | ~55 min | 5 | TypeScript | not-started | Source: Phase 13 L06 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 07 | Building an MCP Server: Stateless Python and TypeScript | ~85 min | 6 | TypeScript | not-started | Source: Phase 13 L07 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 08 | Building an MCP Client: Discovery, Routing, and Dual-Era Fallback | ~85 min | 7 | TypeScript | not-started | Source: Phase 13 L08 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 09 | MCP Transports: stdio and Stateless Streamable HTTP | ~65 min | 8 | TypeScript | not-started | Source: Phase 13 L09 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 10 | MCP Resources and Prompts: Addressable Context for Stateless Servers | ~60 min | 9 | TypeScript | not-started | Source: Phase 13 L10 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 11 | MCP Model Input: Sampling Migration and Stateless MRTR | ~75 min | 10 | TypeScript | not-started | Source: Phase 13 L11 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 12 | Explicit Scope and Stateless Elicitation | ~60 min | 11 | TypeScript | not-started | Source: Phase 13 L12 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 13 | MCP Tasks Extension: Durable Work on a Stateless Core | ~90 min | 12 | TypeScript | not-started | Source: Phase 13 L13 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 14 | MCP Apps on the Stateless Protocol | ~75 min | 13 | TypeScript | not-started | Source: Phase 13 L14 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 15 | MCP Security: Poisoned Metadata, Routing, and MRTR State | ~60 min | 14 | TypeScript | not-started | Source: Phase 13 L15 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 16 | MCP Authorization: CIMD, Issuer Binding, PKCE, and Step-Up | ~90 min | 15 | TypeScript | not-started | Source: Phase 13 L16 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 17 | Stateless MCP Gateways and Registry Admission | ~75 min | 16 | TypeScript | not-started | Source: Phase 13 L17 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 18 | MCP Auth in Production: Issuer-Bound Enrollment and Tokens | ~90 min | 17 | TypeScript | not-started | Source: Phase 13 L18 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 19 | A2A Protocol | ~75 min | 18 | TypeScript | not-started | Source: Phase 13 L19 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 20 | OpenTelemetry GenAI | ~75 min | 19 | TypeScript | not-started | Source: Phase 13 L20 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 21 | LLM Routing Layer | ~45 min | 20 | TypeScript | not-started | Source: Phase 13 L21 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 22 | Agent Skills: Portable Contract and Runtime Boundary | ~90 min | 21 | TypeScript | not-started | Source: Phase 13 L22 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 23 | Capstone: Stateless Tool Ecosystem | ~120 min | 22 | TypeScript | not-started | Source: Phase 13 L23 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 24 | Skill Discovery and Progressive Disclosure | ~105 min | 23 | TypeScript | not-started | Source: Phase 13 L24 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 25 | Skill Invocation and Routing | ~105 min | 24 | TypeScript | not-started | Source: Phase 13 L25 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 26 | Skill Permissions, Sandboxes, and Trust | ~120 min | 25 | TypeScript | not-started | Source: Phase 13 L26 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 27 | Skill Evals, Packaging, and Portability | ~150 min | 26 | TypeScript | not-started | Source: Phase 13 L27 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 28 | MCP Tool Contracts and Content | ~120 min | 27 | TypeScript | not-started | Source: Phase 13 L28 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 29 | MCP Reliability, Cancellation, and Flow Control | ~120 min | 28 | TypeScript | not-started | Source: Phase 13 L29 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 30 | MCP Registry Supply Chain: Admission, Drift, and Rollback | ~90 min | 29 | TypeScript | not-started | Source: Phase 13 L30 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |
| 31 | MCP Conformance Engineering: Versioning, Evidence, and Operations | ~100 min | 30 | TypeScript | not-started | Source: Phase 13 L31 `docs/en.md` + Further Reading. Lang per lesson header (TypeScript / Python). |

**Exit:** see ROADMAP.md phase header for Tools & Protocols exit criteria.

## Mission 15 — Phase 14: Agent Engineering *(~55 hours · Python / TypeScript · not-started)*

Goal: Agent Engineering — see upstream `phases/14-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python / TypeScript — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/14-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | The Agent Loop | ~60 min | none | Python | not-started | Source: Phase 14 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 02 | ReWOO and Plan-and-Execute | ~60 min | 1 | Python | not-started | Source: Phase 14 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 03 | Reflexion and Verbal Reinforcement Learning | ~60 min | 2 | Python | not-started | Source: Phase 14 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 04 | Tree of Thoughts and LATS | ~75 min | 3 | Python | not-started | Source: Phase 14 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 05 | Self-Refine and CRITIC | ~60 min | 4 | Python | not-started | Source: Phase 14 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 06 | Tool Use and Function Calling | ~60 min | 5 | Python | not-started | Source: Phase 14 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 07 | Agent Memory — Virtual Context and Memory Paging | ~75 min | 6 | Python | not-started | Source: Phase 14 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 08 | Memory Blocks and Sleep-Time Compute | ~75 min | 7 | Python | not-started | Source: Phase 14 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 09 | Hybrid Memory — Vector + Graph + KV | ~75 min | 8 | Python | not-started | Source: Phase 14 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 10 | Skill Libraries and Lifelong Learning (Voyager) | ~75 min | 9 | Python | not-started | Source: Phase 14 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 11 | Planning with HTN and Evolutionary Search | ~75 min | 10 | Python | not-started | Source: Phase 14 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 12 | Anthropic's Workflow Patterns | ~60 min | 11 | Python | not-started | Source: Phase 14 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 13 | Stateful Graph Orchestration — Durable Execution and Checkpoints | ~75 min | 12 | Python | not-started | Source: Phase 14 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 14 | The Actor Model for Agents | ~75 min | 13 | Python | not-started | Source: Phase 14 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 15 | Role-Based Agent Teams — Roles, Tasks, Processes | ~60 min | 14 | Python | not-started | Source: Phase 14 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 16 | OpenAI Agents SDK — Handoffs, Guardrails, Tracing | ~75 min | 15 | Python | not-started | Source: Phase 14 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 17 | The Harness as a Library — Subagents and Session Store | ~75 min | 16 | Python | not-started | Source: Phase 14 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 18 | Production Agent Runtimes | ~45 min | 17 | Python | not-started | Source: Phase 14 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 19 | Benchmarks — SWE-bench, GAIA, AgentBench | ~60 min | 18 | Python | not-started | Source: Phase 14 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 20 | Benchmarks — WebArena and OSWorld | ~60 min | 19 | Python | not-started | Source: Phase 14 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 21 | Computer Use — Claude, OpenAI CUA, Gemini | ~60 min | 20 | Python | not-started | Source: Phase 14 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 22 | Voice Agents — Pipecat and LiveKit | ~60 min | 21 | Python | not-started | Source: Phase 14 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 23 | OpenTelemetry GenAI Semantic Conventions | ~60 min | 22 | Python | not-started | Source: Phase 14 L23 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 24 | Agent Observability — Langfuse, Phoenix, Opik | ~45 min | 23 | Python | not-started | Source: Phase 14 L24 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 25 | Multi-Agent Debate and Collaboration | ~60 min | 24 | Python | not-started | Source: Phase 14 L25 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 26 | Failure Modes — Why Agents Break | ~60 min | 25 | Python | not-started | Source: Phase 14 L26 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 27 | Prompt Injection and the PVE Defense | ~75 min | 26 | Python | not-started | Source: Phase 14 L27 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 28 | Orchestration Patterns — Supervisor, Swarm, Hierarchical | ~60 min | 27 | Python | not-started | Source: Phase 14 L28 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 29 | Production Runtimes — Queue, Event, Cron | ~60 min | 28 | Python | not-started | Source: Phase 14 L29 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 30 | Eval-Driven Agent Development | ~60 min | 29 | Python | not-started | Source: Phase 14 L30 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 31 | Agent Workbench: Why Capable Models Still Fail | ~45 min | 30 | Python | not-started | Source: Phase 14 L31 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 32 | The Minimal Agent Workbench | ~45 min | 31 | Python | not-started | Source: Phase 14 L32 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 33 | Agent Instructions as Executable Constraints | ~50 min | 32 | Python | not-started | Source: Phase 14 L33 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 34 | Repo Memory and Durable State | ~60 min | 33 | Python | not-started | Source: Phase 14 L34 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 35 | Initialization Scripts for Agents | ~45 min | 34 | Python | not-started | Source: Phase 14 L35 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 36 | Scope Contracts and Task Boundaries | ~50 min | 35 | Python | not-started | Source: Phase 14 L36 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 37 | Runtime Feedback Loops | ~50 min | 36 | Python | not-started | Source: Phase 14 L37 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 38 | Verification Gates | ~55 min | 37 | Python | not-started | Source: Phase 14 L38 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 39 | Reviewer Agent: Separate Builder from Marker | ~55 min | 38 | Python | not-started | Source: Phase 14 L39 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 40 | Multi-Session Handoff | ~50 min | 39 | Python | not-started | Source: Phase 14 L40 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 41 | The Workbench on a Real Repo | ~60 min | 40 | Python | not-started | Source: Phase 14 L41 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 42 | Capstone: Ship a Reusable Agent Workbench Pack | ~75 min | 41 | Python | not-started | Source: Phase 14 L42 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 43 | Frame the Task Before the Agent Writes Code | ~60 min | 42 | Python | not-started | Source: Phase 14 L43 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 44 | Build an Evidence-Backed Execution Plan | ~65 min | 43 | Python | not-started | Source: Phase 14 L44 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 45 | Delegate Agent Work with Isolation and Merge Contracts | ~70 min | 44 | Python | not-started | Source: Phase 14 L45 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 46 | Turn Every Agent Correction into a System Improvement | ~65 min | 45 | Python | not-started | Source: Phase 14 L46 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 47 | Define the Outcome Before You Choose the Output | ~60 min | 46 | Python | not-started | Source: Phase 14 L47 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 48 | Discover the Workflow People Actually Perform | ~70 min | 47 | Python | not-started | Source: Phase 14 L48 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 49 | Map Assumptions and Resolve the Riskiest One First | ~65 min | 48 | Python | not-started | Source: Phase 14 L49 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 50 | Choose the Smallest Slice That Can Change the Decision | ~65 min | 49 | Python | not-started | Source: Phase 14 L50 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 51 | Write Specifications That Preserve Judgment | ~75 min | 50 | Python | not-started | Source: Phase 14 L51 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 52 | Design Success Metrics Before the Result Exists | ~70 min | 51 | Python | not-started | Source: Phase 14 L52 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 53 | Choose Prototype, Pilot, or Production Deliberately | ~70 min | 52 | Python | not-started | Source: Phase 14 L53 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 54 | Build a Feedback Ratchet with Ownership and Retirement | ~75 min | 53 | Python | not-started | Source: Phase 14 L54 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |

**Exit:** see ROADMAP.md phase header for Agent Engineering exit criteria.

## Mission 16 — Phase 15: Autonomous Systems *(~20 hours · Python · not-started)*

Goal: Autonomous Systems — see upstream `phases/15-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/15-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | From Chatbots to Long-Horizon Agents (METR) | ~45 min | none | Python | not-started | Source: Phase 15 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | STaR, V-STaR, Quiet-STaR — Self-Taught Reasoning | ~60 min | 1 | Python | not-started | Source: Phase 15 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | AlphaEvolve — Evolutionary Coding Agents | ~60 min | 2 | Python | not-started | Source: Phase 15 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | Darwin Gödel Machine — Self-Modifying Agents | ~60 min | 3 | Python | not-started | Source: Phase 15 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | AI Scientist v2 — Workshop-Level Research | ~60 min | 4 | Python | not-started | Source: Phase 15 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | Automated Alignment Research (Anthropic AAR) | ~60 min | 5 | Python | not-started | Source: Phase 15 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | Recursive Self-Improvement — Capability vs Alignment | ~60 min | 6 | Python | not-started | Source: Phase 15 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | Bounded Self-Improvement Designs | ~60 min | 7 | Python | not-started | Source: Phase 15 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Autonomous Coding Agent Landscape (SWE-bench, CodeAct) | ~45 min | 8 | Python | not-started | Source: Phase 15 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | Permission Modes for Autonomous Agents | ~45 min | 9 | Python | not-started | Source: Phase 15 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Browser Agents and Indirect Prompt Injection | ~45 min | 10 | Python | not-started | Source: Phase 15 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | Durable Execution for Long-Running Agents | ~60 min | 11 | Python | not-started | Source: Phase 15 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 13 | Action Budgets, Iteration Caps, Cost Governors | ~60 min | 12 | Python | not-started | Source: Phase 15 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 14 | Kill Switches, Circuit Breakers, Canary Tokens | ~60 min | 13 | Python | not-started | Source: Phase 15 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 15 | HITL — Propose-Then-Commit | ~60 min | 14 | Python | not-started | Source: Phase 15 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 16 | Checkpoints and Rollback | ~60 min | 15 | Python | not-started | Source: Phase 15 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 17 | Constitutional AI and Rule Overrides | ~60 min | 16 | Python | not-started | Source: Phase 15 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 18 | Llama Guard and Input/Output Classification | ~45 min | 17 | Python | not-started | Source: Phase 15 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 19 | Anthropic Responsible Scaling Policy v3.0 | ~45 min | 18 | Python | not-started | Source: Phase 15 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 20 | OpenAI Preparedness Framework and DeepMind FSF | ~45 min | 19 | Python | not-started | Source: Phase 15 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 21 | METR Time Horizons and External Evaluation | ~60 min | 20 | Python | not-started | Source: Phase 15 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 22 | CAIS, CAISI, and Societal-Scale Risk | ~45 min | 21 | Python | not-started | Source: Phase 15 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for Autonomous Systems exit criteria.

## Mission 17 — Phase 16: Multi-Agent & Swarms *(~28 hours · Python / TypeScript · not-started)*

Goal: Multi-Agent & Swarms — see upstream `phases/16-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python / TypeScript — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/16-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Why Multi-Agent | ~45 min | none | Python | not-started | Source: Phase 16 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 02 | FIPA-ACL Heritage and Speech Acts | ~60 min | 1 | Python | not-started | Source: Phase 16 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 03 | Communication Protocols | ~45 min | 2 | Python | not-started | Source: Phase 16 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 04 | The Multi-Agent Primitive Model | ~60 min | 3 | Python | not-started | Source: Phase 16 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 05 | Supervisor / Orchestrator-Worker Pattern | ~75 min | 4 | Python | not-started | Source: Phase 16 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 06 | Hierarchical Architecture and Decomposition Drift | ~60 min | 5 | Python | not-started | Source: Phase 16 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 07 | Society of Mind and Multi-Agent Debate | ~75 min | 6 | Python | not-started | Source: Phase 16 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 08 | Role Specialization — Planner / Critic / Executor / Verifier | ~75 min | 7 | Python | not-started | Source: Phase 16 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 09 | Parallel Swarm and Networked Architectures | ~60 min | 8 | Python | not-started | Source: Phase 16 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 10 | Group Chat and Speaker Selection | ~60 min | 9 | Python | not-started | Source: Phase 16 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 11 | Handoffs and Routines (Stateless Orchestration) | ~60 min | 10 | Python | not-started | Source: Phase 16 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 12 | A2A — The Agent-to-Agent Protocol | ~75 min | 11 | Python | not-started | Source: Phase 16 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 13 | Shared Memory and Blackboard Patterns | ~75 min | 12 | Python | not-started | Source: Phase 16 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 14 | Consensus and Byzantine Fault Tolerance for Agents | ~75 min | 13 | Python | not-started | Source: Phase 16 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 15 | Voting, Self-Consistency, and Debate Topology | ~75 min | 14 | Python | not-started | Source: Phase 16 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 16 | Negotiation and Bargaining | ~75 min | 15 | Python | not-started | Source: Phase 16 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 17 | Generative Agents and Emergent Simulation | ~75 min | 16 | Python | not-started | Source: Phase 16 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 18 | Theory of Mind and Emergent Coordination | ~75 min | 17 | Python | not-started | Source: Phase 16 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 19 | Swarm Optimization for LLMs (PSO, ACO) | ~75 min | 18 | Python | not-started | Source: Phase 16 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 20 | MARL — MADDPG, QMIX, MAPPO | ~90 min | 19 | Python | not-started | Source: Phase 16 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 21 | Agent Economies, Token Incentives, Reputation | ~75 min | 20 | Python | not-started | Source: Phase 16 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 22 | Production Scaling — Queues, Checkpoints, Durability | ~75 min | 21 | Python | not-started | Source: Phase 16 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 23 | Failure Modes — MAST, Groupthink, Monoculture, Cascading | ~75 min | 22 | Python | not-started | Source: Phase 16 L23 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 24 | Evaluation and Coordination Benchmarks | ~75 min | 23 | Python | not-started | Source: Phase 16 L24 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |
| 25 | Case Studies and 2026 State of the Art | ~90 min | 24 | Python | not-started | Source: Phase 16 L25 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript). |

**Exit:** see ROADMAP.md phase header for Multi-Agent & Swarms exit criteria.

## Mission 18 — Phase 17: Infrastructure & Production *(~32 hours · Python / TypeScript / Rust · not-started)*

Goal: Infrastructure & Production — see upstream `phases/17-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python / TypeScript / Rust — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/17-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Managed LLM Platforms — Bedrock, Azure OpenAI, Vertex AI | ~60 min | none | Python | not-started | Source: Phase 17 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 02 | Inference Platform Economics — Fireworks, Together, Baseten, Modal | ~60 min | 1 | Python | not-started | Source: Phase 17 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 03 | GPU Autoscaling on Kubernetes — Karpenter, KAI Scheduler | ~75 min | 2 | Python | not-started | Source: Phase 17 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 04 | Serving Engine Internals — PagedAttention, Continuous Batching, Chunked Prefill | ~75 min | 3 | Python | not-started | Source: Phase 17 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 05 | EAGLE-3 Speculative Decoding in Production | ~60 min | 4 | Python | not-started | Source: Phase 17 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 06 | Prefix-Cache Serving — RadixAttention and KV Reuse | ~60 min | 5 | Python | not-started | Source: Phase 17 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 07 | Hardware-Specialized Inference Compilation — FP8 and NVFP4 on Blackwell | ~75 min | 6 | Python | not-started | Source: Phase 17 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 08 | Inference Metrics — TTFT, TPOT, ITL, Goodput, P99 | ~60 min | 7 | Python | not-started | Source: Phase 17 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 09 | Production Quantization — AWQ, GPTQ, GGUF, FP8, NVFP4 | ~75 min | 8 | Python | not-started | Source: Phase 17 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 10 | Cold Start Mitigation for Serverless LLMs | ~60 min | 9 | Python | not-started | Source: Phase 17 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 11 | Multi-Region LLM Serving and KV Cache Locality | ~60 min | 10 | Python | not-started | Source: Phase 17 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 12 | Edge Inference — ANE, Hexagon, WebGPU, Jetson | ~60 min | 11 | Python | not-started | Source: Phase 17 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 13 | LLM Observability Stack Selection | ~60 min | 12 | Python | not-started | Source: Phase 17 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 14 | Prompt Caching and Semantic Caching Economics | ~60 min | 13 | Python | not-started | Source: Phase 17 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 15 | Batch APIs — the 50% Discount as Industry Standard | ~45 min | 14 | Python | not-started | Source: Phase 17 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 16 | Model Routing as a Cost-Reduction Primitive | ~60 min | 15 | Python | not-started | Source: Phase 17 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 17 | Disaggregated Prefill/Decode — NVIDIA Dynamo and llm-d | ~75 min | 16 | Python | not-started | Source: Phase 17 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 18 | Production Serving Stack — KV Offloading and Cache-Aware Routing | ~60 min | 17 | Python | not-started | Source: Phase 17 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 19 | AI Gateways — LiteLLM, Portkey, Kong, Bifrost | ~60 min | 18 | Python | not-started | Source: Phase 17 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 20 | Shadow, Canary, and Progressive Deployment | ~60 min | 19 | Python | not-started | Source: Phase 17 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 21 | A/B Testing LLM Features — GrowthBook and Statsig | ~60 min | 20 | Python | not-started | Source: Phase 17 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 22 | Load Testing LLM APIs — k6, LLMPerf, GenAI-Perf | ~75 min | 21 | Python | not-started | Source: Phase 17 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 23 | SRE for AI — Multi-Agent Incident Response | ~60 min | 22 | Python | not-started | Source: Phase 17 L23 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 24 | Chaos Engineering for LLM Production | ~60 min | 23 | Python | not-started | Source: Phase 17 L24 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 25 | Security — Secrets, PII Scrubbing, Audit Logs | ~60 min | 24 | Python | not-started | Source: Phase 17 L25 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 26 | Compliance — SOC 2, HIPAA, GDPR, EU AI Act, ISO 42001 | ~60 min | 25 | Python | not-started | Source: Phase 17 L26 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 27 | FinOps for LLMs — Unit Economics and Multi-Tenant Attribution | ~60 min | 26 | Python | not-started | Source: Phase 17 L27 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 28 | Self-Hosted Serving Selection — Matching Engine to Hardware and Scale | ~45 min | 27 | Python | not-started | Source: Phase 17 L28 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |

**Exit:** see ROADMAP.md phase header for Infrastructure & Production exit criteria.

## Mission 19 — Phase 18: Ethics, Safety & Alignment *(~31 hours · Python · not-started)*

Goal: Ethics, Safety & Alignment — see upstream `phases/18-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/18-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Instruction-Following as Alignment Signal | ~45 min | none | Python | not-started | Source: Phase 18 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 02 | Reward Hacking & Goodhart's Law | ~60 min | 1 | Python | not-started | Source: Phase 18 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 03 | Direct Preference Optimization Family | ~60 min | 2 | Python | not-started | Source: Phase 18 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 04 | Sycophancy as RLHF Amplification | ~45 min | 3 | Python | not-started | Source: Phase 18 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 05 | Constitutional AI & RLAIF | ~60 min | 4 | Python | not-started | Source: Phase 18 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 06 | Mesa-Optimization & Deceptive Alignment | ~75 min | 5 | Python | not-started | Source: Phase 18 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 07 | Sleeper Agents — Persistent Deception | ~60 min | 6 | Python | not-started | Source: Phase 18 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 08 | In-Context Scheming in Frontier Models | ~60 min | 7 | Python | not-started | Source: Phase 18 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 09 | Alignment Faking | ~60 min | 8 | Python | not-started | Source: Phase 18 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 10 | AI Control — Safety Despite Subversion | ~75 min | 9 | Python | not-started | Source: Phase 18 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 11 | Scalable Oversight & Weak-to-Strong Generalization | ~60 min | 10 | Python | not-started | Source: Phase 18 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 12 | Red-Teaming — PAIR & Automated Attacks | ~75 min | 11 | Python | not-started | Source: Phase 18 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 13 | Many-Shot Jailbreaking | ~45 min | 12 | Python | not-started | Source: Phase 18 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 14 | ASCII Art & Visual Jailbreaks | ~60 min | 13 | Python | not-started | Source: Phase 18 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 15 | Indirect Prompt Injection | ~75 min | 14 | Python | not-started | Source: Phase 18 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 16 | Red-Team Tooling — Garak, Llama Guard, PyRIT | ~75 min | 15 | Python | not-started | Source: Phase 18 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 17 | WMDP & Dual-Use Capability Evaluation | ~60 min | 16 | Python | not-started | Source: Phase 18 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 18 | Frontier Safety Frameworks — RSP, PF, FSF | ~75 min | 17 | Python | not-started | Source: Phase 18 L18 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 19 | Model Welfare Research | ~45 min | 18 | Python | not-started | Source: Phase 18 L19 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 20 | Bias & Representational Harm | ~60 min | 19 | Python | not-started | Source: Phase 18 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 21 | Fairness Criteria — Group, Individual, Counterfactual | ~60 min | 20 | Python | not-started | Source: Phase 18 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 22 | Differential Privacy for LLMs | ~60 min | 21 | Python | not-started | Source: Phase 18 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 23 | Watermarking — SynthID, Stable Signature, C2PA | ~75 min | 22 | Python | not-started | Source: Phase 18 L23 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 24 | Regulatory Frameworks — EU, US, UK, Korea | ~75 min | 23 | Python | not-started | Source: Phase 18 L24 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 25 | EchoLeak & CVEs for AI | ~45 min | 24 | Python | not-started | Source: Phase 18 L25 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 26 | Model, System & Dataset Cards | ~60 min | 25 | Python | not-started | Source: Phase 18 L26 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 27 | Data Provenance & Training-Data Governance | ~60 min | 26 | Python | not-started | Source: Phase 18 L27 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 28 | Alignment Research Ecosystem — MATS, Redwood, Apollo, METR | ~45 min | 27 | Python | not-started | Source: Phase 18 L28 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 29 | Moderation Systems — OpenAI, Perspective, Llama Guard | ~60 min | 28 | Python | not-started | Source: Phase 18 L29 `docs/en.md` + Further Reading. Lang per lesson header (Python). |
| 30 | Dual-Use Risk — Cyber, Bio, Chem, Nuclear | ~75 min | 29 | Python | not-started | Source: Phase 18 L30 `docs/en.md` + Further Reading. Lang per lesson header (Python). |

**Exit:** see ROADMAP.md phase header for Ethics, Safety & Alignment exit criteria.

## Mission 20 — Phase 19: Capstone Projects *(~620 hours · Python / TypeScript / Rust · not-started)*

Goal: Capstone Projects — see upstream `phases/19-*/docs/en.md` per lesson. Goal phrasing follows Rohit ROADMAP.md phase header.

- **Lang (phase default):** Python / TypeScript / Rust — lesson-level `Languages:` header overrides (Rohit). Python for math/ML, TypeScript for Tools/Agents/Protocols, Rust where phase lists it, Julia optional in Phase 1.
- **Source base:** `https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/phases/19-*` — each lesson: `phases/<phase>/<lesson>/docs/en.md` + `## Further Reading` external refs + `code/` per Rohit (Rohit is a source, not the source).

| # | Lesson | Est. time | Prereqs | Lang | Status | Notes |
|---|--------|-----------|---------|------|--------|-------|
| 01 | Terminal-Native Coding Agent | ~35 hr | none | Python | not-started | Source: Phase 19 L01 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 02 | RAG over Codebase (Cross-Repo Semantic Search) | ~30 hr | 1 | Python | not-started | Source: Phase 19 L02 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 03 | Real-Time Voice Assistant (ASR to LLM to TTS) | ~30 hr | 2 | Python | not-started | Source: Phase 19 L03 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 04 | Multimodal Document QA (Vision-First) | ~30 hr | 3 | Python | not-started | Source: Phase 19 L04 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 05 | Autonomous Research Agent (AI-Scientist Class) | ~40 hr | 4 | Python | not-started | Source: Phase 19 L05 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 06 | DevOps Troubleshooting Agent for Kubernetes | ~30 hr | 5 | Python | not-started | Source: Phase 19 L06 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 07 | End-to-End Fine-Tuning Pipeline | ~35 hr | 6 | Python | not-started | Source: Phase 19 L07 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 08 | Production RAG Chatbot (Regulated Vertical) | ~30 hr | 7 | Python | not-started | Source: Phase 19 L08 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 09 | Code Migration Agent (Repo-Level Upgrade) | ~30 hr | 8 | Python | not-started | Source: Phase 19 L09 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 10 | Multi-Agent Software Engineering Team | ~40 hr | 9 | Python | not-started | Source: Phase 19 L10 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 11 | LLM Observability & Eval Dashboard | ~25 hr | 10 | Python | not-started | Source: Phase 19 L11 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 12 | Video Understanding Pipeline (Scene to QA) | ~30 hr | 11 | Python | not-started | Source: Phase 19 L12 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 13 | Stateless MCP Server with Registry and Governance | ~25 hr | 12 | Python | not-started | Source: Phase 19 L13 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 14 | Speculative-Decoding Inference Server | ~30 hr | 13 | Python | not-started | Source: Phase 19 L14 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 15 | Constitutional Safety Harness + Red-Team Range | ~25 hr | 14 | Python | not-started | Source: Phase 19 L15 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 16 | GitHub Issue-to-PR Autonomous Agent | ~30 hr | 15 | Python | not-started | Source: Phase 19 L16 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 17 | Personal AI Tutor (Adaptive, Multimodal) | ~30 hr | 16 | Python | not-started | Source: Phase 19 L17 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 20 | Agent Harness Loop Contract | ~90 min | 17 | Python | not-started | Source: Phase 19 L20 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 21 | Tool Registry with Schema Validation | ~90 min | 18 | Python | not-started | Source: Phase 19 L21 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 22 | JSON-RPC 2.0 Over Newline-Delimited Stdio | ~90 min | 19 | Python | not-started | Source: Phase 19 L22 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 23 | Function Call Dispatcher | ~90 min | 20 | Python | not-started | Source: Phase 19 L23 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 24 | Plan-Execute Control Flow | ~90 min | 21 | Python | not-started | Source: Phase 19 L24 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 25 | Verification Gates and the Observation Budget | ~90 min | 22 | Python | not-started | Source: Phase 19 L25 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 26 | Sandbox Runner with Denylist and Path Jail | ~90 min | 23 | Python | not-started | Source: Phase 19 L26 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 27 | Eval Harness with Fixture Tasks | ~90 min | 24 | Python | not-started | Source: Phase 19 L27 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 28 | Observability with OTel GenAI Spans and Prometheus Metrics | ~90 min | 25 | Python | not-started | Source: Phase 19 L28 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 29 | End-to-End Coding Agent on the Harness | ~90 min | 26 | Python | not-started | Source: Phase 19 L29 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 30 | BPE Tokenizer From Scratch | ~90 min | 27 | Python | not-started | Source: Phase 19 L30 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 31 | Tokenized Dataset with Sliding Window | ~90 min | 28 | Python | not-started | Source: Phase 19 L31 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 32 | Token and Positional Embeddings | ~90 min | 29 | Python | not-started | Source: Phase 19 L32 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 33 | Multi-Head Self-Attention | ~90 min | 30 | Python | not-started | Source: Phase 19 L33 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 34 | Transformer Block from Scratch | ~90 min | 31 | Python | not-started | Source: Phase 19 L34 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 35 | GPT Model Assembly | ~90 min | 32 | Python | not-started | Source: Phase 19 L35 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 36 | Training Loop and Evaluation | ~90 min | 33 | Python | not-started | Source: Phase 19 L36 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 37 | Loading Pretrained Weights | ~90 min | 34 | Python | not-started | Source: Phase 19 L37 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 38 | Classifier Fine-Tuning by Head Swap | ~90 min | 35 | Python | not-started | Source: Phase 19 L38 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 39 | Instruction Tuning by Supervised Fine-Tuning | ~90 min | 36 | Python | not-started | Source: Phase 19 L39 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 40 | Direct Preference Optimization from Scratch | ~90 min | 37 | Python | not-started | Source: Phase 19 L40 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 41 | Full Evaluation Pipeline | ~90 min | 38 | Python | not-started | Source: Phase 19 L41 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 42 | Large Corpus Downloader | ~90 min | 39 | Python | not-started | Source: Phase 19 L42 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 43 | HDF5 Tokenized Corpus | ~90 min | 40 | Python | not-started | Source: Phase 19 L43 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 44 | Cosine LR with Linear Warmup | ~90 min | 41 | Python | not-started | Source: Phase 19 L44 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 45 | Gradient Clipping and Mixed Precision | ~90 min | 42 | Python | not-started | Source: Phase 19 L45 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 46 | Gradient Accumulation | ~90 min | 43 | Python | not-started | Source: Phase 19 L46 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 47 | Checkpoint Save and Resume | ~90 min | 44 | Python | not-started | Source: Phase 19 L47 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 48 | Distributed Data Parallel and FSDP from Scratch | ~90 min | 45 | Python | not-started | Source: Phase 19 L48 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 49 | Language Model Evaluation Harness | ~90 min | 46 | Python | not-started | Source: Phase 19 L49 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 50 | Hypothesis Generator | ~90 min | 47 | Python | not-started | Source: Phase 19 L50 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 51 | Literature Retrieval | ~90 min | 48 | Python | not-started | Source: Phase 19 L51 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 52 | Experiment Runner | ~90 min | 49 | Python | not-started | Source: Phase 19 L52 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 53 | Result Evaluator | ~90 min | 50 | Python | not-started | Source: Phase 19 L53 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 54 | Paper Writer | ~90 min | 51 | Python | not-started | Source: Phase 19 L54 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 55 | Critic Loop | ~90 min | 52 | Python | not-started | Source: Phase 19 L55 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 56 | Iteration Scheduler | ~90 min | 53 | Python | not-started | Source: Phase 19 L56 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 57 | End-to-End Research Demo | ~90 min | 54 | Python | not-started | Source: Phase 19 L57 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 58 | Vision Encoder Patches | ~90 min | 55 | Python | not-started | Source: Phase 19 L58 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 59 | Vision Transformer Encoder | ~90 min | 56 | Python | not-started | Source: Phase 19 L59 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 60 | Projection Layer for Modality Alignment | ~90 min | 57 | Python | not-started | Source: Phase 19 L60 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 61 | Cross-Attention Fusion | ~90 min | 58 | Python | not-started | Source: Phase 19 L61 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 62 | Vision-Language Pretraining | ~90 min | 59 | Python | not-started | Source: Phase 19 L62 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 63 | Multimodal Evaluation | ~90 min | 60 | Python | not-started | Source: Phase 19 L63 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 64 | Chunking Strategies, Compared | ~90 min | 61 | Python | not-started | Source: Phase 19 L64 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 65 | Hybrid Retrieval with BM25 and Dense Embeddings | ~90 min | 62 | Python | not-started | Source: Phase 19 L65 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 66 | Cross-Encoder Reranker | ~90 min | 63 | Python | not-started | Source: Phase 19 L66 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 67 | Query Rewriting: HyDE, Multi-Query, and Decomposition | ~90 min | 64 | Python | not-started | Source: Phase 19 L67 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 68 | RAG Evaluation: Precision, Recall, MRR, nDCG, Faithfulness, Answer Relevance | ~90 min | 65 | Python | not-started | Source: Phase 19 L68 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 69 | End-to-End RAG System | ~90 min | 66 | Python | not-started | Source: Phase 19 L69 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 70 | Task Spec Format | ~90 min | 67 | Python | not-started | Source: Phase 19 L70 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 71 | Classical Metrics | ~90 min | 68 | Python | not-started | Source: Phase 19 L71 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 72 | Code Exec Metric | ~90 min | 69 | Python | not-started | Source: Phase 19 L72 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 73 | Perplexity and Calibration | ~90 min | 70 | Python | not-started | Source: Phase 19 L73 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 74 | Leaderboard Aggregation | ~90 min | 71 | Python | not-started | Source: Phase 19 L74 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 75 | End-to-End Eval Runner | ~90 min | 72 | Python | not-started | Source: Phase 19 L75 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 76 | Collective Ops From Scratch | ~90 min | 73 | Python | not-started | Source: Phase 19 L76 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 77 | Data Parallel DDP From Scratch | ~90 min | 74 | Python | not-started | Source: Phase 19 L77 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 78 | ZeRO Optimizer State Sharding | ~90 min | 75 | Python | not-started | Source: Phase 19 L78 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 79 | Pipeline Parallel and Bubble Analysis | ~90 min | 76 | Python | not-started | Source: Phase 19 L79 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 80 | Sharded Checkpoint and Atomic Resume | ~90 min | 77 | Python | not-started | Source: Phase 19 L80 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 81 | End-to-End Distributed Training | ~90 min | 78 | Python | not-started | Source: Phase 19 L81 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 82 | Jailbreak Taxonomy | ~90 min | 79 | Python | not-started | Source: Phase 19 L82 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 83 | Prompt Injection Detector | ~90 min | 80 | Python | not-started | Source: Phase 19 L83 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 84 | Refusal Evaluation | ~90 min | 81 | Python | not-started | Source: Phase 19 L84 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 85 | Content Classifier Integration | ~90 min | 82 | Python | not-started | Source: Phase 19 L85 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 86 | Constitutional Rules Engine | ~90 min | 83 | Python | not-started | Source: Phase 19 L86 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |
| 87 | End-to-End Safety Gate | ~90 min | 84 | Python | not-started | Source: Phase 19 L87 `docs/en.md` + Further Reading. Lang per lesson header (Python / TypeScript / Rust). |

**Exit:** see ROADMAP.md phase header for Capstone Projects exit criteria.

## Branch — off-curriculum interrogations *(not a Rohit node — the sequential curriculum position is unaffected)*

> Learner-surfaced topics taught through the same Scout/Tutor/Clerk interrogation loop but outside the AI Engineering from Scratch roadmap. They never move the sequential curriculum position, and they are carried in the `aiefs` review track so a plain `review` still reaches them.

| # | Topic | Est. time | Prereqs | Lang | Status | Notes |
|---|-------|-----------|---------|------|--------|-------|
| B01 | Software Architecture — intro & the 'non-functional' label (*Head First Software Architecture*, Ch.1) | — | none | — | in-progress | **Paused 2026-11-06** (clean pause after a repair close; one counterexample attack queued, none in flight). Architecture = "expensive and hard to change later" solid closed-book; "non-functional" placed as a **requirements** label (fresh-surface repair close PASS). Open: counterexample on the v1 tail ("with architecture → functional; otherwise → non-functional (unreliable)") — both halves; then a calibration re-check (exit ticket's blanket "confident in all of it" is banked as illusion-of-competence). Concepts: `Software Architecture — intro` (2026-11-09), `Software Architecture — failure-list placement of 'non-functional'` (2026-11-13). Handoff: partial (`/pause`), no Scout digest (learner-surfaced source, no fetch). |

---

## Rules

1. Lessons strictly sequential within a mission; missions in phase order (0→19). Mission 0 Catch-Up is prerequisite to Phase 1 L07; Phase 0 individual lessons are covered by that catch-up and may be retrieval-checked, not re-taught.
2. Scout, before each **new** lesson: fetch live `phases/<phase>/<lesson>/docs/en.md` + **every URL in its `## Further Reading`** (+ `RESOURCES.md` curated), hash, compare to digest cache, surface drift (`SCOUT DIGEST: ⚠️ Upstream changed`). Rohit is a source, not the source.
3. New concepts enter `Core/📚 Active Concepts.md` on first introduction (status `developing`, `last_reviewed` today, `next_review` +3d), exactly like ingest. Scout/Tutor grep **only** `📚 Active Concepts.md` + `RESOURCES.md` + curriculum — `📦 Concept Archive.md` is strictly out of scope (SWE archived).
4. A lesson marked `not-started*` (covered by catch-up) is retrieval-checked, never re-taught; on fail demote to `in-progress`.
5. Advancement requires: practice complete + retrieval pass + Feynman explain-back (Learning Record, Bloom level noted).
6. **Language:** per-lesson `Languages:` header (Rohit) decides build language (Python / TypeScript / Rust; Julia optional). Phase default is fallback; do not default everything to Python.
7. Interleaving only in review flow (SRS shuffle + adjacency + question-type alternation) — never inside lessons/quizzes.
8. Full 20-phase map is navigational, not contractual. After each phase, decide to go deeper / branch / build. Cache is ignored per decision 2026-09-01 (live fetch each lesson; no phase cache layer).

## Provenance

- **Upstream:** https://github.com/rohitg00/ai-engineering-from-scratch — `ROADMAP.md` + `phases/*/docs/en.md` + `phases/*/code/` (MIT). Cached at switch: `main` 2026-09-01 (~323h, 20 phases, 523 lessons).
- **Previous roadmap archived:** `Learning System/Archive/CURRICULUM — SWE Primary Colors — archived 2026-09-01.md` + `Learning System/Archive/MISSION — SWE Stage 0 — archived 2026-09-01.md` + wiki banner.
- **Environment note (Docker Desktop Windows-side, separate from WSL):** OpenWebUI base URL inside WSL is `http://host.docker.internal:3000` (not `localhost:3000`); workspace repo at `/home/user/learning-system` (container) vs `/home/delinux/learning-system` (WSL). See `OPENWEBUI.md`.