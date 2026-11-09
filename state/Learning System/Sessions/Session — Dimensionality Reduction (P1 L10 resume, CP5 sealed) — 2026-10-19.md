# Session — Dimensionality Reduction (P1 L10 resume, CP5 sealed) — 2026-10-19

**Session:** Tutor (resume) · **Date:** 2026-10-19 · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) — paused at **Checkpoint 6/6**
**Taught:** **CP5 mini 5b (center-only vs standardize) sealed** + **CP5 practice passed 4/4 (P1–P4, all `sure`, 0 hints)** — **CP5 (UMAP) FULLY SEALED**. Pause exit ticket X1 completed (`fail`, inverted application rule).
**Position:** paused at Checkpoint 6/6 — CP5 fully sealed 2026-10-19; minis 4+5a sealed 2026-10-17; minis 2–3 sealed 2026-10-14; mini 1 sealed 2026-10-13; CP4 fully sealed 2026-10-12. **Resume: Checkpoint 6/6, mini 1: Kernel PCA with an RBF kernel (PCA on a nonlinear manifold)** (the high-variance=important assumption vs Shlens ferris wheel, and the method-choice map).
**Sources:** continuing on the fresh **2026-10-13 digest** `Learning System/.tmp/context-01a134d5-4aeb-715d-8ab7-fe2f4f944481-dimensionality-reduction.json` (inside TTL through 2026-10-20 — kept); raw bodies `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap-faq.md` (centering vs standardizing FAQ rule, clustering advice, outlier collapse), `…- rohit.md`, `…- umap-paper.md` (§3.1 k-NN graph, §3.2 layout optimization).

## What ran

1. **Mini 5b — feature scaling (center-only vs standardize) sealed:**
   - **Elicitation P2 (resumed from 2026-10-17 pause, quiz-audit PASS, ungraded):** learner answered both questions:
     - (1) *"if no standardization, i think the knn distances will be too big since features have wildly different values since they arent on the same scale but if there is then the knn distances be less since they are on the same sclae"*
     - (2) *"i think it would be a bad idea if their values dont vary wildy from each other. another time it would be a bad idea i think is when you actually want to see the relationship between two features in their own units e.g see relationship between people's weight(kg) and thier height(meters)."*
   - **Socratic ladder & guidance:** guided turns grounded the intuition:
     - (1) In mixed scales (e.g. kg vs mm), the numerically larger feature dominates the Euclidean distance computation, causing the loss of true neighbors.
     - (2) Rescaling features with an inherent geometric relationship (e.g. latitude and longitude of an island) deforms the true geometry into an artificial spherical shape.
     - Learner confirmed verbatim: *"1. i see so that means kilogram's contribution is deemed more weighty than that of mm. it also means we lose some 'true neighbors' since some neighobors are just too far away due to different scales. / 2. it would make it the island spherical in shape which doesnt really reflect the true geometry of the island."*
   - **Check-and-extend idea turn (fact-check PASS):**
     - Centering shifts the mean to 0 without altering relative distances or feature scale.
     - Standardizing centers and rescales each feature to unit variance ($\sigma = 1$).
     - The UMAP FAQ rule: standardize when features are independent measurements on disparate, incomparable units (e.g. clinical lab tests, patient age/blood pressure); center-only without rescaling when coordinates share a meaningful geometry or common unit space.
     - **Mini 5b SEALED.**

2. **CP5 Practice (4-item batch, quiz-audit PASS, grade-audit agreed 4/4, all `sure`, 0 hints):**
   - **P1 ✓ pass (`applied`, `sure`, 0 hints):** `n_neighbors` vs `min_dist` stage separation and tradeoff. Tested graph-construction stage (input k-NN connectivity) vs low-dimensional embedding layout stage (output minimum packing floor). Passed clean under retrieval pressure, advancing the 2026-10-14 mistake row toward review.
   - **P2 ✓ pass (`discriminative`, `sure`, 0 hints):** global structure and outlier collapse mechanism under default settings. Evaluated whole-embedding repulsion sampling (negative sampling) vs outlier collapse, and verified the role of `disconnection_distance`.
   - **P3 ✓ pass (`applied`, `sure`, 0 hints):** PCA→UMAP→HDBSCAN pipeline rationale. Reaffirmed that UMAP distorts density, necessitating that HDBSCAN re-estimate density on the low-dim representation; rejected the KNN-as-clusterer distractor, verifying the 2026-10-17 stage-role detector.
   - **P4 ✓ pass (`applied`, `sure`, 0 hints):** feature scaling decision across concrete domains. Correctly chose standardizing for independent clinical metrics on incomparable units, and center-only for geographic/spatial coordinates.
   - **Checkpoint 5 (UMAP) FULLY SEALED.**

3. **Pause exit ticket X1 (quiz-audit PASS, grade-audit agreed 0/1, `sure`, 0 hints):**
   - **X1 ✗ fail (`free-recall`):** core mechanical difference between centering and standardizing before UMAP, and when to choose which.
   - Learner verbatim: *"the core difference is that centering centers the data around the mean while standaradizing does that and also puts features on the same scale. i would choose centering only when dealing with features that are essentially independent while for standardizaing i would choose for when dealing with features that have meaningful relationship"*
   - **Verdict:** mechanical distinction correct (centering centers around mean, standardizing puts features on unit scale), but completely inverted the application rule (chose centering for independent features, and standardizing for meaningful relationships — exactly backwards from the UMAP FAQ rule).
   - Logged as a new active structural mistake row in `🧯 Mistakes.md`.

## Attempts (ops.py, already written in-session)

- `UMAP (Dimensionality Reduction)` — 2026-10-19:
  - pass `applied` (`sure`, 0 hints) — CP5 practice P1
  - pass `discriminative` (`sure`, 0 hints) — CP5 practice P2
  - pass `applied` (`sure`, 0 hints) — CP5 practice P3
  - pass `applied` (`sure`, 0 hints) — CP5 practice P4
  - fail `free-recall` (`sure`, 0 hints) — Pause exit ticket X1
  - Net: mastery **0.60** advisory, `interval_index` **2**, `last_reviewed` **2026-10-19**, `next_review` **2026-11-02**, `consecutive_correct` 0, `consecutive_wrong` 1, `Last Q Type` **free-recall**.

## Mistakes candidates

- **New row — Centering vs Standardizing application rule inversion** (`structural`):
  - Question: What is the core difference between centering and standardizing features before running UMAP, and when would you choose one over the other?
  - Expected: Centering shifts mean to 0 without altering scale; standardizing also rescales each feature to unit variance. Standardize when features are independent and on incomparable scales; center-only when features share a meaningful relationship/geometry (e.g. latitude/longitude).
  - Error type: `structural`.
  - Self-attribution: Inverted the application rule: assigned centering-only to independent features and standardizing to features with meaningful relationships (the reverse of the UMAP FAQ rule).
  - Status: `active`, retries 0, next retry 2026-11-02.
- **Resolved / progressing rows:**
  - 2026-10-14 row (`n_neighbors` vs `min_dist` knob crossing): P1 passed clean under retrieval pressure (identified n_neighbors as graph connectivity control vs min_dist as low-dim layout floor).
  - 2026-10-17 row (KNN/K-Means stage-role slip): P3 passed clean under retrieval pressure (affirmed HDBSCAN density re-estimation and rejected the KNN-as-clusterer distractor).

## Dependency events

- None — no `just_tell_me`, no `told_repair`, no `declined_generation`. All generations produced independently by learner.

## Learner pacing

- Resumed mini 5b cleanly, completed guiding questions, passed CP5 practice 4/4 with confidence `sure`, completed pause exit ticket X1, and chose to pause before launching Checkpoint 6/6.
