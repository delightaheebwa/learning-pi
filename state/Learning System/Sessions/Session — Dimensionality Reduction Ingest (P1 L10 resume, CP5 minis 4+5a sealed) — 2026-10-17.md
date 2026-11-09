# Session — Dimensionality Reduction Ingest (P1 L10 resume, CP5 minis 4+5a sealed) — 2026-10-17

**Session:** Clerk (ingest from `Core/Pending Ingest.json`, partial `/pause` handoff) · **Date:** 2026-10-17 · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) — stays **in-progress**
**Ingested:** **CP5 (UMAP) mini 4 exit ticket sealed (3/3)** + **CP5 mini 5a (pipeline PCA→UMAP→HDBSCAN) sealed 2026-10-17**; mini 5b (center-only vs standardize) opened — **P2 probe delivered but unanswered** (learner paused).
**Position written:** paused at **Checkpoint 5/6** — CP5 mini 4 SEALED (exit ticket 3/3) + CP5 mini 5a (pipeline PCA→UMAP→HDBSCAN) SEALED 2026-10-17; mini 5b opened (P2 probe delivered 2026-10-17, NOT answered). Minis 2–3 sealed 2026-10-14; mini 1 sealed 2026-10-13; CP4 fully sealed 2026-10-12. **Resume: CP5 (UMAP) mini 5b — center-only vs standardize**: RE-ASK the P2 probe, teach the scaling decision, then CP6.
**Sources:** `Learning System/Core/Pending Ingest.json` (partial handoff) → lesson `Learning System/Lessons/Lesson — Dimensionality Reduction — 2026-09-26.md`; teach session `Learning System/Sessions/Session — Dimensionality Reduction (P1 L10 resume, CP5 minis 4+5a sealed) — 2026-10-17.md`; learning record `Learning System/Learning Records/0017-umap-pipeline-each-stage-does-what-the-other-cant.md`; raw bodies `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap-faq.md` ("Which tool should I use?", clustering advice, "does not preserve density well", "contract connected components", K-Means poor choice / HDBSCAN recommended), `…- umap-paper.md` (§3.1 k-NN graph first stage), `…- rohit.md` (curse-of-dimensionality table ~1.8 at d=10 → ~1.02 at d=1000). Kept digest `Learning System/.tmp/context-01a134d5-4aeb-715d-8ab7-fe2f4f944481-dimensionality-reduction.json` (created 2026-10-13, inside TTL through 2026-10-20).

## What was written

- **Wiki page deepened** `Knowledge Wiki/wiki/UMAP (Dimensionality Reduction).md` (provenance `status=synthesis`, `verified-by=—`, `date=2026-10-17`):
  - Updated `## Global structure: goal, not guarantee` noting the mini 4 exit ticket sealed 3/3 on 2026-10-17.
  - Added new **`## The pipeline: PCA → UMAP → HDBSCAN`** section:
    - **Why PCA first (~50 dims):** denoise neighbor distances against distance concentration in ambient space (max/min ratio ~1.8 at $d=10$ collapses to ~1.02 at $d=1000$) and make graph construction cheap; contrast: PCA is linear and cannot unfold curved manifolds, UMAP is nonlinear and unfolds manifolds but cannot fix polluted distances — each stage does what the other cannot.
    - **Why UMAP to intermediate dimensions (~10–20 dims):** preserves manifold topology and geometric degrees of freedom for clustering rather than forcing a 2-D projection with extreme crowding penalties.
    - **Why HDBSCAN last (and why K-Means is a poor choice):** (1) Geometry — UMAP does not preserve density well and contracts connected components together, so 2-D plot boundaries are artifacts; the clusterer must re-estimate density itself on the ~10–20-D embedding; (2) Forced assignment — K-Means assumes spherical equal clusters and must assign every point, forcing it to label noise as clusters; HDBSCAN finds varying-density clusters and leaves noise unlabeled (`label = -1`).
    - **Stage-role detector:** assigning cluster labels = K-Means / HDBSCAN; building the graph = KNN (UMAP's first stage).
  - Updated `## Queued for this concept`: mini 4 exit ticket sealed, mini 5a sealed, mini 5b opened (resume point: re-ask P2 probe), CP6 pending.
  - **`## My understanding` appended** with **three more verbatim learner statements** (`status=learner-note`, now eleven total):
    1. E3 exit ticket verbatim (own-words push-pull + outlier blob collapse + `disconnection_distance` check).
    2. Mini 5a elicitation prior verbatim (why PCA first and clustering after).
    3. Mini 5a sealing line verbatim (why clustering directly on 2-D with K-Means fails, including the stage-role slip).
    Annotated *around*, never rewritten.
- **Active Concepts row** `UMAP (Dimensionality Reduction)` **enriched** and synced to `Attempts.json`: `last_reviewed` **2026-10-17**, `next_review` **2026-11-16**, `Last Q Type` **`free-recall`**, mastery **0.90** advisory, `interval_index` **3**, `consecutive_correct` **4**, `consecutive_wrong` **0**.
- **Mistakes: 1 new row appended** to `Learning System/Core/🧯 Mistakes.md`: KNN/K-Means stage-role confusion (`structural`, `active`, retries 0, next retry 2026-10-24) from the mini 5a sealing line ("KNN simply groups those clusters with their noise"); repaired with the stage-role detector.
- **Dependency events: none** (`dependency_events: []`).
- **Position reconciliation** across `Learning System/MISSION.md`, `Learning System/CURRICULUM.md`, `Core/💡 Learning Profile.md`, and `Core/📚 Active Concepts.md`: all aligned to paused at Checkpoint 5/6 — CP5 mini 4 SEALED + mini 5a SEALED 2026-10-17; mini 5b opened (P2 probe delivered, unanswered); resume CP5 (UMAP) mini 5b (center-only vs standardize).
- `Knowledge Wiki/index.md` refreshed (UMAP entry updated with sealed mini 4 exit ticket, pipeline section, and eleven statements) + `Knowledge Wiki/log.md` (this ingest's entry).
- `Core/Learner History.md` regenerated via `python3 scripts/learner_history.py`.

## Attempts evidence (from `Core/Attempts.json` — written in-session by the Tutor)

- `UMAP (Dimensionality Reduction)` — 2026-10-17: pass (`discriminative`, sure, 0 hints — E1) · pass (`discriminative`, sure, 0 hints — E2) · pass (`free-recall`, sure, 0 hints — E3 own-words); with prior rows: `last_reviewed` **2026-10-17**, `next_review` **2026-11-16**, mastery **0.90** advisory, `interval_index` **3**, `consecutive_correct` 4, `consecutive_wrong` 0.

## Consistency with the lesson file

- The lesson file's own `**Status:**`/`**Resume from:**` (**paused at Checkpoint 5/6 — CP5 mini 4 SEALED + mini 5a SEALED 2026-10-17**, resume **CP5 (UMAP) mini 5b — center-only vs standardize**) agree with the handoff's `status`/`resume_from`.

## Marker / digest (partial close)

- `Core/Pending Ingest.json` **cleared** (partial handoff — the marker only).
- The **fresh** digest `Learning System/.tmp/context-01a134d5-4aeb-715d-8ab7-fe2f4f944481-dimensionality-reduction.json` is **KEPT** (created 2026-10-13, inside its 7-day TTL through 2026-10-20).
- The lesson file and the CURRICULUM row stay **in-progress**.
