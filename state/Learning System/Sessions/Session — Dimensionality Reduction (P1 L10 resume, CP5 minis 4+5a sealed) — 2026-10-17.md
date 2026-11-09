# Session — Dimensionality Reduction (P1 L10 resume, CP5 minis 4+5a sealed) — 2026-10-17

**Session:** Tutor (resume) · **Date:** 2026-10-17 · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) — paused at **Checkpoint 5/6**
**Taught:** **CP5 mini 4 exit ticket sealed (3/3)** + **CP5 mini 5a (pipeline PCA→UMAP→HDBSCAN) sealed**; mini 5b (center-only vs standardize) opened — **P2 probe delivered but unanswered** (learner paused).
**Position:** paused at Checkpoint 5/6 — CP5 mini 4 + mini 5a sealed 2026-10-17; minis 2–3 sealed 2026-10-14; mini 1 sealed 2026-10-13; CP4 fully sealed 2026-10-12. **Resume: re-ask the mini 5b P2 probe**, teach the scaling decision, then CP6.
**Sources:** continuing on the fresh **2026-10-13 digest** `Learning System/.tmp/context-01a134d5-4aeb-715d-8ab7-fe2f4f944481-dimensionality-reduction.json` (inside TTL through 2026-10-20 — kept); raw bodies `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap-faq.md` (pipeline advice, "does not preserve density well", "contract connected components", "something like K-Means is a poor choice" + "I would recommend HDBSCAN or similar" as separate sentences), `…- rohit.md` (curse-of-dimensionality table ~1.8 at d=10 → ~1.02 at d=1000), `…- umap-paper.md` (§3.1 k-NN graph first stage).

## What ran

1. **CP5 mini 4 exit ticket (quiz-audit PASS cycle 2 after e1/e2 length-parity + strawman fixes; grade-audit agreed 3/3):**
   - **E1 B ✓** (`discriminative`, `sure`, 0 hints) — graduated claim: a goal reached often, guaranteed never; enough maximally far outliers can pull the whole space together.
   - **E2 A ✓** (`discriminative`, `sure`, 0 hints) — whole-embedding repulsion sampling; t-SNE's cross-cluster P_ij ≈ 0 leaves the cost almost unmoved by the gaps.
   - **E3 ✓** (`free-recall`, `sure`, 0 hints) — learner's own words (verbatim): *"it means that UMAP tries to make the global structure as honest as possible by pushing apart random sampled points that are not neighbors and pull together those that are but this breaks if points are maximally apart from each other which makes the otpimizer then consider them all neighbors and hence pull them togehter causing a collapse into a blob. what i would check is the disconnection_distance before trusting the cluster-to-cluster arrangement on a UMAP plot. sure."*
   - **Tutor sharpening:** `disconnection_distance` cuts the dangerous edges — the practical check is *setting it* and screening for disconnected vertices, not just naming it. **Mini 4 SEALED.**
2. **Mini 5a — the pipeline (sealed):**
   - **Elicitation (ungraded, quiz-audit PASS):** P1 prior — (a) *"I think it first reduces the number of dimensions to the ones that actually matter(explain most of the data). I think feeding UMAP 300 dimensions would make it harder to make neighbors plot."* (b) *"i think because some clusters may have overlap hence we may not have distinct clusters which is needed for final clustering."* — both right-shaped (0 guiding questions; ladder budget 2 available, none needed).
   - **Check-and-extend idea turn (fact-check PASS after one attribution fix: a synthesized FAQ sentence was re-cut into its three separate sentences):** PCA first because UMAP's first stage is the k-NN graph and 300+ dims pollutes it (distance concentration — CP3 anchor ~1.8 at d=10 → ~1.02 at d=1000); PCA denoises the neighbor distances and makes graph-building cheap; PCA for very large/high-dimensional data, UMAP for smaller datasets; ~50/10–20 = practical defaults, not laws; contrast: PCA linear (cannot unfold a manifold), UMAP nonlinear (cannot fix polluted distances). Last stage: UMAP "does not preserve density well" → boundary artifacts → the clusterer must re-estimate density itself → HDBSCAN finds varying-density clusters and leaves noise unlabeled; K-Means must assign every point.
   - **Sealing line + repair:** learner's generation — *"it would be a mistake because the plot itself doesnt preserve density well hence noise will be within each cluster and KNN simply groups those clusters with their noise"* — **KNN/K-Means slip (first occurrence):** wrote the graph-stage term (KNN) where the clusterer (K-Means) belongs. Repair (fact-check PASS 4/4): stage-role detector (assigning labels = K-Means; building the graph = KNN) + the double mistake completed: (1) geometry — the 2-D plot's density is distorted, so boundaries found on it are artifacts; (2) forced assignment — K-Means is obliged to label noise; HDBSCAN can say "no". Learner: *"makes sense"* → **mini 5a SEALED.**
3. **Mini 5b opened, NOT answered:** P2 probe (center vs standardize vs nothing, features in wildly different units) delivered with a quiz-audit PASS receipt; learner paused before answering.

## Attempts (ops.py, already written in-session)

- `UMAP (Dimensionality Reduction)` — 2026-10-17: pass `discriminative` (`sure`, 0 hints) ×2 + pass `free-recall` (`sure`, 0 hints) — the exit ticket. Mastery **0.90** advisory, `interval_index` **3**, `next_review` **2026-11-16**, `consecutive_wrong` 0.
- `t-SNE (Dimensionality Reduction)` — no attempt (last_reviewed 2026-10-12, next_review 2026-11-11).
- Prereq check 2026-10-17: `ops.py prereqs "UMAP (Dimensionality Reduction)"` → ok (t-SNE `neutral`, no block).

## Mistakes candidate (Tutor does NOT write the ledger — Clerk appends at ingest)

- **First occurrence — KNN/K-Means stage-role slip** (`structural`): in the mini-5a sealing line the learner used KNN (UMAP's graph stage) where the clustering algorithm (K-Means) belongs; caught by the Tutor, repaired in-ladder with the stage-role detector; learner confirmed "makes sense". Self-attribution not elicited. Evidence: the sealing line quoted above. **No new row was written by the Tutor.**

## Dependency events

- None — no `just_tell_me`, no `told_repair`, no `declined_generation`. The pause was requested before the mini 5b answer, not mid-idea.

## Learner pacing

- Sealed mini 4 with no questions ("lets move on"); sealed mini 5a ("makes sense"); chose to **pause** before the mini 5b idea landed.
