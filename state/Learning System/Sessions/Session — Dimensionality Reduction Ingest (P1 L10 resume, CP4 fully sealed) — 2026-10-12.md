# Session — Dimensionality Reduction Ingest (P1 L10 resume, CP4 fully sealed) — 2026-10-12

**Type:** ingest (Clerk, partial /pause handoff) · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Position after ingest:** in-progress, **paused at Checkpoint 4/6 — CP4 fully sealed 2026-10-12** (practice 4/4 + pause exit ticket 3/3, all `sure`; CP4 mini 4 sealed 2026-10-10; CP4 minis 2 and 3/3b sealed 2026-10-09; CP4 mini 1 sealed 2026-10-08; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30). Resume from **CP5 (UMAP) mini 1 — re-scout first** (the Scout digest is 17 days old, past its 7-day TTL; only the t-SNE halves of the cached sources were consumed).

## Source of this ingest

- Handoff: `Learning System/Core/Pending Ingest.json` (`partial: true`, created 2026-10-12) — consumed; the marker was cleared (partial close: marker only).
- Lesson: `Learning System/Lessons/Lesson — Dimensionality Reduction — 2026-09-26.md`
- Teach session: `Learning System/Sessions/Session — Dimensionality Reduction (P1 L10 resume, CP4 fully sealed) — 2026-10-12.md`
- No new source fetches this session; the Scout digest is **kept** (partial close).

## Wiki writes

- **`t-SNE (Dimensionality Reduction)`** — deepened with the CP4-sealed half of the lesson:
  - **Where the two kernels come from (kernel deep-dive):** one shared idea — turn a distance into "probability of being neighbours" — two jobs. The **data side** is **Gaussian bells**, one per point, each with its own bandwidth `σ_i` **binary-searched** until `Per(P_i)` meets the user's knob (dense ⇒ narrower bell, sparse ⇒ wider). The **map side** is a **Student-t with one degree of freedom**, `q_{ij} ∝ 1/(1 + d_{ij}²)` normalised, chosen because a 2-D **Gaussian** `Q` collapses to ≈ 0 at distance and strangles the crowded band's escapes. Neither shape is forced by the other.
  - **The widening gap, no "flip point":** near `d ≈ 0` the two curves are twins; the gap then opens gradually and keeps widening — the Gaussian dies exponentially, the Student-t only like `1/d²`. The distance axis is never split half-and-half into "Gaussian territory" and "`t` territory".
  - **Why the crowd sits in the tail region — by construction:** sharply peaked `P` (≈ *perplexity* real-weight pairs) → close range is scarce and the big-`P` pairs claim it first (the KL asymmetry) → the distance-concentrated mid-range crowd (the CP3 curse anchor) is pushed outward into exactly the band where the Gaussian `Q` is dead and the `t` is still up. The heavy tail is the *mechanism of relief*, not decoration.
  - **CP4 fully sealed 2026-10-12:** practice 4/4 (knob 40 vs the 24-point ceiling with `H = log₂24 ≈ 4.58` bits; big-`P`-tiny-`Q`; the Gaussian tail too fast; no single valid global perplexity under heterogeneous densities) and pause exit ticket 3/3 (Gaussian data side / Student-t map side; close range claimed first; bells stopping short ⇒ `P_ij ≈ 0`), all `sure`, 0 hints.
  - **`## My understanding` (`status=learner-note`) extended** with the three verbatim 2026-10-12 statements, appended after the 2026-10-10 block — nothing removed, reworded, or reordered; the block now holds **thirteen** statements. The annotations sit *around* his words: `Source framing:` (the check-and-extend sharpening — the fine only speaks for `P`-weighted pairs, anything read across weightless territory is the optimizer's arrangement) and `Missing piece:` (the weight is a **log-ratio** multiplier, not a probability; and the untuned-perplexity scope of the distance claim).
- **`Knowledge Wiki/index.md`** — the `t-SNE` concept entry refreshed; **`Knowledge Wiki/log.md`** appended.

## State reconciliation

- **Position pointers** (`MISSION.md` Position; `CURRICULUM.md` Phase note + row 10 + the Phase-1 exit line; `💡 Learning Profile.md` new Last-Updated line + Current Focus + Current Position + Sequencing; `📚 Active Concepts.md` new metadata Last-Updated line + Live System Notes + Mastery Summary + the DR section header) all read the same state: **paused at Checkpoint 4/6 — CP4 fully sealed 2026-10-12 (practice 4/4 + exit ticket 3/3, all `sure`); resume CP5 (UMAP) mini 1 — re-scout first (digest past TTL)**.
- **`t-SNE (Dimensionality Reduction)` row** — `last_reviewed` 2026-10-10 → **2026-10-12**; `next_review` 2026-11-09 → **2026-11-11**; `Last Q Type` `micro-check` → **`discriminative`** (the last recorded attempt of the day is the exit ticket); content extended with the kernel deep-dive, the sealed practice and the exit ticket. Synced to `Attempts.json` (mastery **1.00** advisory, `interval_index` 3, `consecutive_correct` 7, `prereqs: ["KL Divergence"]`; the three 2026-10-12 graded rows are `transfer-near` + `explain-back` for the single practice batch and `discriminative` for the exit ticket, all `sure`, 0 hints).
- **Other DR rows** — no graded attempt today: `PCA (Dimensionality Reduction)` (2026-10-08 / 2026-11-07), `Variance & Covariance` (2026-10-06 / 2026-11-05), `Eigenvalues & Eigenvectors` (2026-10-03 / 2026-11-02), `Curse of dimensionality` (2026-10-10 / 2026-11-09) all already match `Attempts.json` and were left untouched.
- **Mistakes** — none. The handoff carries `mistakes: []` (practice 4/4 + exit ticket 3/3, no graded fail), so nothing is appended to `🧯 Mistakes.md`.
- **Dependency events** — none (`dependency_events: []`: no `just_tell_me`, no `told_repair`, no `declined_generation`; every question was a learner-initiated tangent answered in full). The same is carried into the Learning Record's `Dependency:` line by the Tutor's handoff — nothing to amend here.
- `Core/Learner History.md` regenerated via `scripts/learner_history.py`.

## Lesson-vs-handoff agreement

The lesson file's `Status:` / `Resume from:` (paused at Checkpoint 4/6; CP4 fully sealed 2026-10-12; resume **CP5 (UMAP) mini 1**, re-scout first, digest past TTL) **agree** with the handoff `status` / `resume_from` — nothing to flag or merge. The wiki guidance in the handoff is advisory (the Tutor's suggestions) and was followed.

## Marker / digest

- `Core/Pending Ingest.json` — **cleared** (partial handoff: the marker only).
- Scout digest `Learning System/.tmp/context-01a0d78c-dbff-7362-bcea-13f8df10005b-dimensionality-reduction.json` — **kept** (partial close); it is 17 days old, past the 7-day TTL — **re-scout before CP5** (the CP4 teaching consumed the t-SNE halves of the cached sources; the UMAP bodies remain unconsumed).
- Lesson file and the CURRICULUM row stay **in-progress**.

## Surfaces (not fixed)

- The aged Scout digest (TTL) and the kept-digest presence warning — both expected at a partial close.
- **Attempt-date discrepancy:** the two CP4-practice rows in `Attempts.json` are stamped `2026-10-11` while the session note, the handoff (`created_at` 2026-10-12) and the exit-ticket row are stamped 2026-10-12. Surfaced, not rewritten — evidence dates are the Tutor's and the sanctioned correction route is an audited `ops.py amend --reason`, not a Clerk edit.
- `📚 Active Concepts.md` → `Open Questions` still carries the stale `Curse of dimensionality` bullet claiming the concept "still has no Active Concepts row and no Attempts entry"; both exist since the 2026-10-07 ingest — reported, not merged (outside this ingest's touched scope).
- `Curse of dimensionality` sits at mastery 0.00 in one stale note with `next_review` 2026-10-10 while never having had a graded attempt before 2026-10-10 — a review-flow matter, surfaced not fixed.
- Learner History is advisory and regenerated, not hand-edited.
