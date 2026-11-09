# Session — Dimensionality Reduction Ingest (P1 L10 resume, CP4 mini 1 sealed) — 2026-10-08

**Type:** ingest (partial `/pause` handoff) · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Source:** `Core/Pending Ingest.json` (partial, 2026-10-08) · lesson `Lessons/Lesson — Dimensionality Reduction — 2026-09-26.md` · teach session `Sessions/Session — Dimensionality Reduction (P1 L10 resume, CP4 mini 1 sealed) — 2026-10-08.md` · learning record `Learning Records/0011-t-sne-false-neighbors-and-the-anomaly-tangent.md`
**Position after ingest:** in-progress, **paused at Checkpoint 3/6 — CP4 mini 1 sealed** (CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30). Resume **CP4 mini 2 — perplexity as the banked 2^H on the neighbor distribution**.

## What happened (from the handoff)

- **Warm-up CP3 recall 2/3:** W1 round-cloud max-kept 90% ✓, W3 concentration-is-a-blur ✓, **W2 failed** — asked which point *escapes* the reconstruction-error flag, the learner answered with the flagged signature (a huge coordinate on a **dropped** axis: the loudest alarm, not an escape).
- **W2 repair (diagnose-first):** detector restated — the alarm fires only on across-dropped-axis distance; far-along-kept ⇒ error ≈ 0 ⇒ silent. Micro-check (a point 1,000 units out along a line-cloud's single kept axis) → **missed** ✓.
- **Learner tangent, sealed:** *why are far-along points never flagged?* → **shape vs depth** (the error asks the shape question only; far-along outliers need a stacked depth-style check — kept-coordinate vs training range, the `Q`/SPE + Hotelling `T²`/Mahalanobis practice), **unit vs signal** (every residual lives in the dropped subspace by construction; the flag reads its *length* against the training threshold), and **directions get dropped, points never do**.
- **CP4 mini 1 — t-SNE neighborhoods (sealed via elicit → attempt → consolidate):** first prediction "flat 2D plane; neighbors stay neighbors" (half right); two guiding questions landed the learner's own false-neighbour conclusion — "non-neighbors can become neighbors in the flatten and i guess that doesnt work for the vice versa case"; consolidation fact-checked with the **attribution fix** (the pair-probability mechanism is Rohit's; Distill's distinctive add is the interpretation-caution layer).
- **Pause exit ticket 3/3, all `sure`** (false neighbours · reconstruction error = residual length off the kept subspace · a stacked depth check is needed for far-along points). **Attempts:** PCA fail (W2) → pass (exit ticket) ⇒ mastery 0.75, `interval_index` 3, `next_review` 2026-11-07.

## Concepts touched

- **`t-SNE (Dimensionality Reduction)` — new Active Concepts row** (Type `concept`, `developing`, `last_reviewed` 2026-10-08, `next_review` 2026-10-11 = +3d, Last Q Type `definitional`) + matching `Attempts.json` entry (empty attempt list, so the row is schedulable and the row/Attempts sets stay aligned). New wiki page `t-SNE (Dimensionality Reduction)`.
- **`PCA (Dimensionality Reduction)` — enriched + synced** (`last_reviewed` 2026-10-06 → **2026-10-08**, `next_review` 2026-11-05 → **2026-11-07**, mastery 0.75, `interval_index` 3, Last Q Type → `discriminative`). Wiki page enriched with the shape/depth section + the frame-inversion detector.
- `Curse of dimensionality` — untouched (row and `Attempts.json` entry already exist from 2026-10-07; the handoff's "rowless candidate" note is **stale** and surfaced, not merged). Re-touched in-session only via warm-up W3.
- `Variance & Covariance` / `Eigenvalues & Eigenvectors` — unchanged (no attempts today; Attempts.json dates stand).

## Attribution fix applied (handoff `state_fixes_for_clerk`)

The pairwise-probability mechanism (near = high probability, far = low probability, find the 2D arrangement matching it) is **in Rohit's source**; Distill's distinctive add is the **misreading/interpretation-caution layer**. The new t-SNE page records this as an explicit correction of this track's earlier draft, and the PCA page's anomaly-detector section already carried the CP3 framing, so the enrichment added only the genuinely new **shape-vs-depth / stacked-depth-check / unit-vs-signal / directions-vs-points** material.

## ⚠️ Contradiction surfaced (kept live)

**Cluster distances:** Rohit — "Distances between clusters in the output are not meaningful. Only the clusters themselves are." (unconditional) vs Distill — distances "may mean nothing" *at arbitrary perplexity*, with perplexity 50 recovering the global geometry in their example (conditional). Resolution carried: Rohit = **safe default**, Distill = **fragile exception under tuning**; both true at their own scope. Recorded as a `⚠️ Sources disagree` callout on the t-SNE page and left open until CP4 mini 4.

## Mistakes appended — 1 row, canonical concept `PCA (Dimensionality Reduction)`

| Concept | Error type | Self-attribution | Repair |
|---|---|---|---|
| PCA (Dimensionality Reduction) | structural | none explicitly; learner self-located after the detector restate ("check what the alarm literally measures") | detector restate (alarm fires on across-dropped-axis distance only) + micro-check (1,000 units out along the kept axis → missed) + exit ticket X3; row opens `review` / retries 1 / next retry 2026-11-07 |

## Position pointers reconciled

`MISSION.md` (Position), `CURRICULUM.md` (Phase note + row 10 + the Phase-1 exit line), `Core/💡 Learning Profile.md` (Last-Updated block, Current Focus, Current Position, Sequencing) and `Core/📚 Active Concepts.md` (metadata Last-Updated line, Live System Notes pointer, Mastery Summary AIEFS bullet, L10 DR section header) all name **paused at Checkpoint 3/6 — CP4 mini 1 sealed 2026-10-08 — resume CP4 mini 2 (perplexity as the banked 2^H on the neighbor distribution)**. Row 10 stays **in-progress**. `Core/Learner History.md` regenerated via `scripts/learner_history.py`. The lesson file's own `Status:`/`Resume from:` **agrees** with the handoff (CP4 mini 1 sealed 2026-10-08; resume CP4 mini 2) — no disagreement to surface there.

## Marker / digest / audit

- Marker: `Core/Pending Ingest.json` **cleared** (partial handoff — marker only). Scout digest **kept** (partial close) and now 13 days old, past the 7-day TTL → **re-scout before CP4 mini 2+ material that needs fresh sources**.
- Lesson file stays `in-progress`; curriculum row stays `in-progress`.
- State audit: `STATE_AUDIT_VERDICT` folded into the ingest summary.
- Surfaced, not fixed: the aged Scout digest + kept-digest warning; the handoff's stale "rowless `Curse of dimensionality`" note.

## Open questions

- **CP4 mini 2** — perplexity as the banked `2^H` applied to the neighbour distribution (name-collision reframe; Rohit's typical 5–50).
- **CP4 mini 3** — the objective: how the `P` vs `Q` mismatch is scored and which direction the divergence runs (bridge to `KL Divergence`).
- **CP4 mini 4** — the Distill misreading protocol + the Rohit-vs-Distill cluster-distance contradiction (currently resolved as safe-default vs fragile-exception; to be taught loudly).
- Carried from CP3: the parked CP2 code-write integration still folds into the **final cumulative quiz** (learner's 2026-10-05 rule).
