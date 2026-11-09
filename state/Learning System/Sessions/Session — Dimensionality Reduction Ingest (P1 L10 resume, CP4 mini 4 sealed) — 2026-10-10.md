# Session — Dimensionality Reduction Ingest (P1 L10 resume, CP4 mini 4 sealed) — 2026-10-10

**Type:** ingest (Clerk, partial /pause handoff) · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Position after ingest:** in-progress, **paused at Checkpoint 4/6 — CP4 mini 4 sealed 2026-10-10** (teaching only; the CP4 practice is still pending; CP4 minis 2 and 3/3b sealed 2026-10-09; CP4 mini 1 sealed 2026-10-08; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30). Resume from the **CP4 practice — one graded MCQ batch on the whole t-SNE chain** (mini 2 perplexity incl. the n−1 ceiling; mini 3 objective; mini 3b heavy tail; mini 4 misreading protocol), then CP5 (UMAP).

## Source of this ingest

- Handoff: `Learning System/Core/Pending Ingest.json` (`partial: true`, created 2026-10-10) — consumed; the marker was cleared (partial close, marker only).
- Lesson: `Learning System/Lessons/Lesson — Dimensionality Reduction — 2026-09-26.md`
- Teach session: `Learning System/Sessions/Session — Dimensionality Reduction (P1 L10 resume, CP4 mini 4 sealed) — 2026-10-10.md`
- Learning record: `Learning System/Learning Records/0013-t-sne-misreading-protocol-cluster-sizes-distances.md`
- No new source fetches this session; the Scout digest is **kept** (partial close).

## Wiki writes

- **`t-SNE (Dimensionality Reduction)`** — deepened with the CP4 mini 4 half of the checkpoint:
  - **The misreading protocol (mini 4):** cluster sizes are meaningless — the apparent size is the **spread of the 2-D coordinates the optimizer produced**, and because one plot carries **one** user-set perplexity target (only `σ_i` adapts per point) the knob cannot manufacture a size difference; sizes shift with perplexity and re-runs, and pure noise at low perplexity still shows dramatic clumps. Cluster distances mean little **at an untuned perplexity** — the KL cost pins *neighbourhoods*, cross-cluster pairs carry `P_{ij} ≈ 0`, so their fine is ≈ 0 under *any* separation and the gap belongs to the optimizer's arrangement (no direction is guaranteed) — with the **fragile exception** that a perplexity tuned to the data's natural cluster structure makes inter-cluster distances *somewhat* meaningful (heterogeneous densities may admit no single valid perplexity).
  - **The ⚠️ Rohit-vs-Distill contradiction is resolved** (section retitled "resolved at CP4 mini 4"): both sources are true at their own scope — Rohit's unconditional rule is the **safe default**, Distill's conditional is the **fragile exception** that only a deliberate tuning experiment on your own data can establish. The callout stays on the page as the record of the split; nothing is smoothed away.
  - **3b cost picture — the learner-computed worked example:** the pair-level re-walk (frozen `P_{ij}`, steerable `Q_{ij}`, agreement ⇒ 0, 0.05 vs 0.001 ⇒ ratio 50 ⇒ ≈ 0.2) now carries his own computed mismatch case, **P = 0.2, Q = 0.001 → `0.2 × log₂ 200 ≈ 0.2 × 7.64 ≈ 1.53 bits`** (nats route ≈ 1.06 — a base-unit difference, not an error).
  - **`## My understanding` (`status=learner-note`)** — the five verbatim 2026-10-10 statements **appended** after the 2026-10-09 block; nothing removed, reworded, or reordered. Annotations sit *around* his words: `Source framing:` (his own log₂ route, the nats alternative) and `Missing piece:` (one plot ⇒ one target settles where the size comes from; the distance statement's untuned scope).
- **`Knowledge Wiki/index.md`** — the `t-SNE` concept entry refreshed; **`Knowledge Wiki/log.md`** appended.

## State reconciliation

- **Position pointers** (`MISSION.md` Position; `CURRICULUM.md` Phase note + row 10 + the Phase-1 exit line; `💡 Learning Profile.md` new Last-Updated line + Current Focus + Current Position + Sequencing; `📚 Active Concepts.md` new metadata Last-Updated line + Live System Notes + Mastery Summary + the DR section header) all read the same state: **paused at Checkpoint 4/6 — CP4 mini 4 sealed 2026-10-10 (teaching only; the CP4 practice is still pending; CP4 minis 2 and 3/3b sealed 2026-10-09; CP4 mini 1 sealed 2026-10-08; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30); resume from the CP4 practice — one graded MCQ batch on the whole t-SNE chain — then CP5 (UMAP)**.
- **`t-SNE (Dimensionality Reduction)` row** — `last_reviewed` 2026-10-09 → **2026-10-10**; `next_review` 2026-11-08 → **2026-11-09**; `Last Q Type` `discriminative` → **`micro-check`** (the last recorded attempt of the day is the re-walk micro-check; the warm-up pass was `discriminative`); content extended with the misreading protocol, the resolved scope split and the closed pacing call. Synced to `Attempts.json` (mastery **1.00** advisory, `interval_index` 3, `consecutive_correct` 4, `prereqs: ["KL Divergence"]`; the two 2026-10-10 graded attempts are warm-up `discriminative` + re-walk `micro-check`, both `sure`, 0 hints).
- **Other DR rows** — no graded attempt today: `PCA (Dimensionality Reduction)` (2026-10-08 / 2026-11-07), `Variance & Covariance` (2026-10-06 / 2026-11-05), `Eigenvalues & Eigenvectors` (2026-10-03 / 2026-11-02), `Curse of dimensionality` (2026-10-07 / 2026-10-10) all already match `Attempts.json` and were left untouched.
- **Mistakes** — none. The handoff carries `mistakes: []`: the mini-4 ownership detour was repaired in-ladder at the elicitation/statement rungs (no graded attempt, no error_type), so nothing is appended to `🧯 Mistakes.md`.
- **Dependency events** — none (`dependency_events: []`: no `just_tell_me`, no `declined_generation`, no `told_repair`; every State-rung generation was made). The two guiding-question rounds per atom were ungraded; hints were recorded only on the two graded rows, both 0.
- `Core/Learner History.md` regenerated via `scripts/learner_history.py`.

## Lesson-vs-handoff agreement

The lesson file's `Status:` / `Resume from:` (paused at Checkpoint 4/6; CP4 mini 4 sealed 2026-10-10; resume the CP4 practice, then CP5 (UMAP)) **agree** with the handoff `status` / `resume_from`; nothing to flag or merge. The wiki guidance in the handoff is advisory (the Tutor's suggestions) and was followed; no disagreement found.

## Marker / digest

- `Core/Pending Ingest.json` — **cleared** (partial handoff: the marker only).
- Scout digest `Learning System/.tmp/context-01a0d78c-dbff-7362-bcea-13f8df10005b-dimensionality-reduction.json` — **kept** (partial close); it is 15 days old, past the 7-day TTL — **re-scout before CP5** fresh-source teaching (the CP4 teaching consumed the t-SNE halves of the cached sources; the UMAP bodies remain unconsumed).
- Lesson file and the CURRICULUM row stay **in-progress**.

## Surfaces (not fixed)

- The aged Scout digest (TTL) and the kept-digest presence warning — both expected at a partial close.
- `📚 Active Concepts.md` → `Open Questions` still carries the stale `Curse of dimensionality` bullet claiming the concept "still has no Active Concepts row and no Attempts entry"; both exist since the 2026-10-07 ingest — reported, not merged (outside this ingest's touched scope).
- `Curse of dimensionality` sits at mastery 0.00 with `next_review` 2026-10-10 and no graded attempt on record — a review-flow matter, surfaced not fixed.
- Learner History is advisory and regenerated, not hand-edited.
