# Session — Dimensionality Reduction Ingest (P1 L10 resume, CP5 minis 2–3 sealed) — 2026-10-14

**Session:** Clerk (ingest from `Core/Pending Ingest.json`, partial `/pause` handoff) · **Date:** 2026-10-14 · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) — stays **in-progress**
**Ingested:** **CP5 (UMAP) minis 2–3 sealed 2026-10-14** — the `n_neighbors` dial (input-side hard integer) and the `min_dist` dial (output-side packing floor), including the resolved ⚠️ docs-vs-paper reading of the floor; on top of the same fresh 2026-10-13 re-scout digest (audited PASS, kept inside its TTL).
**Position written:** paused at **Checkpoint 5/6** — CP5 minis 2–3 sealed 2026-10-14 (mini 1 sealed 2026-10-13; CP4 fully sealed 2026-10-12); **resume CP5 (UMAP) mini 4 — the 'better global structure' claim + the ⚠️ Rohit-vs-umap-faq contradiction.**
**Sources:** `Learning System/Core/Pending Ingest.json` (partial handoff) → lesson `Learning System/Lessons/Lesson — Dimensionality Reduction — 2026-09-26.md`; teach session `Learning System/Sessions/Session — Dimensionality Reduction (P1 L10 resume, CP5 minis 2-3 sealed) — 2026-10-14.md`; learning record `Learning System/Learning Records/0015-umap-two-dials-n-neighbors-and-min-dist.md`; raw bodies `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap-params.md` (the sweeps), `…- umap-paper.md` (Definition 11 / Algorithm 5, the hyper-parameter discussion), `…- umap-faq.md`, `…- rohit.md`.

## What was written

- **Wiki page deepened** `Knowledge Wiki/wiki/UMAP (Dimensionality Reduction).md` (provenance `status=synthesis`, `verified-by=—` — the review gate runs after the Clerk returns): a new **`## The two dials`** section —
  - **`n_neighbors` — the INPUT-side dial (a hard integer):** one fixed list length for the whole run, not a per-point soft count; the docs verbatim on the local↔global balance; the contrast with [[t-SNE (Dimensionality Reduction)|perplexity]] (same *role*, different *object* — `Per(P_i) = 2^{H(P_i)}` is an effective per-point count, `n_neighbors` is a literal k); small k ⇒ charts barely overlap ⇒ "merely glues together small chains" + components and singletons, large k ⇒ a coherent map "but at the loss of some of the finer local structure"; the docs' k = 2/20/200 sweep as the anchor; the paper's "local scale at which to approximate the manifold as roughly flat"; and the patch normalisation `Σ_j exp(−max(0, d(x_i,x_j) − ρ_i)/σ_i) = log₂(k)` (`ρ_i` = nearest-neighbour distance, `σ_i` binary-searched, Algorithms 2–3).
  - **`min_dist` — the OUTPUT-side dial (the packing floor):** the docs' "quite literally, provides the minimum distance apart that points are allowed to be", default 0.1, sweep 0.0 → 0.99; the paper's "hyperparameter directly affecting the output" / "essentially aesthetic parameter"; it **never touches the graph**, so a fragmented graph stays fragmented; the floor arrives as a **force curve** (the piecewise `Ψ` approximated by `Φ = (1 + a‖x−y‖₂^{2b})⁻¹`, a and b fitted by non-linear least squares; Algorithm 5 descends on `log Φ`), so sub-floor placements are penalized, not vetoed.
  - **⚠️ Sources disagree on how hard the floor is** — surfaced in-session and resolved: practical reading = *strong resistance*, mechanism = *gradient penalty* (docs' literal floor vs the paper's smooth approximation).
  - The **knob-crossing failure-mode note** from the exit ticket, with the separator sentence *`min_dist` never touches the graph*.
- **`## Queued for this concept` and `## Open questions` re-cut:** the two dials are no longer queued; the local-connectivity question moves from "not yet read" to **partly answered** (paper Algorithms 2–3); CP5 mini 4 (the global-structure claim against the paper's "arguably" hedge and the FAQ's goal-not-guarantee framing), mini 5 and CP6 stay queued.
- **`## My understanding` appended** with **three more verbatim learner statements** (`status=learner-note`) — the leaf/stomata analogy (`n_neighbors`), the box-packer analogy (`min_dist`) and the closing trigger "it kicks in when two points try to go lower than the floor in terms of distance between them" — annotated **around** (Source framing: accepted as-is / direction-correct + one in-session refinement), never paraphrased, polished or replaced; the two 2026-10-13 statements are untouched.
- **Active Concepts row** `UMAP (Dimensionality Reduction)` **enriched** (it already existed from the 2026-10-13 ingest — the handoff note calling it a new row is stale, surfaced not merged) and synced to `Attempts.json`: `last_reviewed` **2026-10-14**, `next_review` **2026-10-28**, Last Q Type `applied`, mastery **0.45** advisory, `interval_index` 2, `consecutive_wrong` 1.
- **One new Mistakes row** — the knob-crossing slip (X1 + X3 in one row), `application`, self-attribution cell prefixed `[prereq: t-SNE (Dimensionality Reduction)] `, `active` / retries 0 / next retry 2026-10-28. **Dependency events: none** (`dependency_events: []`) — no `just_tell_me`, no `told_repair`, no `declined_generation`; every State-rung generation was made, so the learning record's `Dependency:` line stays "no opt-outs".
- **Position reconciliation** across `Learning System/MISSION.md`, `Learning System/CURRICULUM.md` (Phase note + row 10 + the Phase-1 exit line), `Core/💡 Learning Profile.md` (new Last-Updated line + Current Focus + Current Position + Sequencing) and `Core/📚 Active Concepts.md` (metadata line + Live System Notes + Mastery Summary + the L10 DR section header): all now read **paused at Checkpoint 5/6 — CP5 minis 2–3 sealed 2026-10-14; resume CP5 (UMAP) mini 4 — the 'better global structure' claim + the ⚠️ Rohit-vs-umap-faq contradiction**. Historical Last-Updated lines were left as history.
- `Knowledge Wiki/index.md` (the UMAP line in `## Concepts` re-cut to the two dials) + `Knowledge Wiki/log.md` (this ingest's entry).
- `Core/Learner History.md` regenerated via `python3 scripts/learner_history.py`.

## Attempts evidence (from `Core/Attempts.json` — written in-session by the Tutor, not by this ingest)

- `UMAP (Dimensionality Reduction)` — 2026-10-14: pass (`discriminative`, sure, 0 hints — CP5 mini 1 warm-up) · fail (`applied`, sure — X1) · pass (`discriminative`, sure — X2) · fail (`applied`, sure — X3); with the 2026-10-13 pass/pass rows: `last_reviewed` 2026-10-14, `next_review` **2026-10-28**, mastery **0.45** advisory, `interval_index` 2, `consecutive_wrong` 1, `consecutive_correct` 0. Prereq edge UMAP → t-SNE (Dimensionality Reduction) unchanged.
- `t-SNE (Dimensionality Reduction)` — no attempt on 2026-10-14; row and dates untouched (last_reviewed 2026-10-12, next_review 2026-11-11).

## Consistency with the lesson file

- The lesson file's own `**Status:**`/`**Resume from:**` (**paused at Checkpoint 5/6 — CP5 minis 2–3 sealed 2026-10-14**, resume **CP5 (UMAP) mini 4**) **agree** with the handoff's `status`/`resume_from` — no disagreement to surface, nothing merged.

## Marker / digest (partial close)

- `Core/Pending Ingest.json` **cleared** (the marker only — the file is gitignored) after the commit+push succeeded.
- The **fresh** digest `Learning System/.tmp/context-01a134d5-4aeb-715d-8ab7-fe2f4f944481-dimensionality-reduction.json` is **KEPT** (created 2026-10-13, inside its 7-day TTL) for the CP5 mini-4 resume.
- The lesson file and the CURRICULUM row stay **in-progress**.

## Surfaced, not fixed

- **Stale handoff note:** the task/handoff describes `UMAP (Dimensionality Reduction)` as a *new* Active Concepts row and a *new* wiki page — both already existed from the 2026-10-13 CP5-mini-1 ingest (the page already carried the mini-1 sections and two verbatim learner statements). The ingest **enriched in place**; nothing was duplicated.
- **Residual state-audit warning:** the kept fresh digest's `.tmp/` presence — deliberately expected at a partial close, not a defect.
- The lesson file's `Sources` block still names the retired 2026-09-25 digest as the "first-fetch baseline" (Tutor-owned file, left untouched).

## State audit

- `python3 "$HOME/learning-pi/pi/audit_state.py" --root .` — see `STATE_AUDIT_VERDICT` in the Clerk receipt. Baseline before this ingest was 0 errors / 3 warnings (the UMAP row's stale `2026-11-12` next-review, the stale `Pending Ingest.json`, and the kept digest); the first two are fixed here, leaving the expected kept-digest warning.
