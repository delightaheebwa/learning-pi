# Session — Dimensionality Reduction Ingest (P1 L10 resume, CP4 minis 2 + 3/3b sealed) — 2026-10-09

**Type:** ingest (Clerk, partial /pause handoff) · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Position after ingest:** in-progress, **paused at Checkpoint 4/6 — CP4 minis 2 and 3/3b sealed 2026-10-09** (CP4 mini 1 sealed 2026-10-08; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30). Resume **CP4 mini 4 — the Distill misreading protocol + the ⚠️ Rohit-vs-Distill cluster-distance contradiction**, then the CP4 practice.

## Source of this ingest

- Handoff: `Learning System/Core/Pending Ingest.json` (`partial: true`, created 2026-10-09) — consumed; the marker was cleared (partial close, marker only).
- Lesson: `Learning System/Lessons/Lesson — Dimensionality Reduction — 2026-09-26.md`
- Teach session: `Learning System/Sessions/Session — Dimensionality Reduction (P1 L10 resume, CP4 minis 2+3 sealed) — 2026-10-09.md`
- Learning record: `Learning System/Learning Records/0012-t-sne-perplexity-kl-objective-heavy-tails.md`
- No new source fetches this session; the Scout digest is **kept** (partial close).

## Wiki writes

- **`t-SNE (Dimensionality Reduction)`** — deepened on both halves of CP4 so far:
  - **Perplexity (mini 2):** the banked `2^H` applied to one point's neighbour distribution — `Per(P_i) = 2^{H(P_i)}`, `σ_i` tuned per point (binary search in the paper) until `Per(P_i)` equals the knob; an **effective** soft count (23.7 is a legal value), not a cutoff; low = local / high = global; typical 5–50; **ceiling `n−1`** (20 points ⇒ ≤ 19) as the precise mechanism behind Distill's "smaller than the number of points" guardrail. Contrast drawn with the `Perplexity` page's *hypothetical* uniform (here the uniform is reachable).
  - **The objective (mini 3):** `min KL(P‖Q)` — minimize, never zero (a 2D map cannot honour every neighbourhood); `P` frozen (it is the data), `Q` the only mover via gradient descent on the 2D coordinates; the `P`-supplied weights make "data says near, map says far" the expensive mismatch.
  - **Heavy tails (mini 3b):** squeezing d→2 crowds the medium-distance band; a Gaussian `Q` collapses `Q_i → 0` at distance so `log(P_i/Q_i)` blows up (every escape is fined); the Student-t fat tail keeps `Q_i` up so spreading is affordable while big-`P` pairs still pay to separate — JMLR: *mismatched tails compensate for mismatched dimensionalities*; plus the explicit **"cost is a log-ratio, not a product"** repair of the in-session flipped reason.
  - **`## My understanding` (`status=learner-note`)** — the learner's five verbatim 2026-10-09 statements placed unchanged, including the flagged heavy-tail one (right conclusion, flipped reason) with the repair annotated *around* it, never rewritten; the objective entry carries the annotated missing piece ("minimize, not zero"). Provenance marker moved from `unverified/legacy` to `synthesis` with the three sources cited and the learner-note block recorded.
- **`Perplexity`** — one new cross-linked section: the *third* use of `2^H` (t-SNE's per-point neighbour distribution; a reachable uniform; ceiling `n−1`), distinguished from the LM-reporting reading and from the uniform yardstick; added to Related.
- **`Knowledge Wiki/index.md`** — `t-SNE` and `Perplexity` concept entries refreshed; **`Knowledge Wiki/log.md`** appended.

## State reconciliation

- **Position pointers** (`MISSION.md` Position; `CURRICULUM.md` Phase note + row 10 + the Phase-1 exit line; `💡 Learning Profile.md` new Last-Updated line + Current Focus + Current Position + Sequencing; `📚 Active Concepts.md` new metadata Last-Updated line + Live System Notes + Mastery Summary + the DR section header) all read the same state: **paused at Checkpoint 4/6 — CP4 minis 2 and 3/3b sealed 2026-10-09 (CP4 mini 1 sealed 2026-10-08; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30); resume CP4 mini 4 — the Distill misreading protocol + the Rohit-vs-Distill contradiction**, then the CP4 practice.
- **`t-SNE (Dimensionality Reduction)` row** — `last_reviewed` 2026-10-08 → **2026-10-09**, `next_review` 2026-10-11 → **2026-11-08**, `Last Q Type` `definitional` → `discriminative`; source cell extended (JMLR 2008); content extended with the mini 2 / 3 / 3b material and the pacing call. Synced to `Attempts.json` (mastery 0.80 advisory, `interval_index` 3, two `pass`/`discriminative`/`sure`/0-hint attempts on 2026-10-09, `prereqs: ["KL Divergence"]`).
- **`Perplexity` row** — no graded attempt today (the elicitations were ungraded), so the row is left untouched; its dates already match `Attempts.json` (last_reviewed 2026-10-03, next_review 2026-11-02, `discriminative`). No drift found.
- **Mistakes** — none. The handoff carries `mistakes: []` (no graded fail today); the heavy-tail reason flip was repaired in-session and is recorded as a wiki annotation ("cost is a log-ratio, not a product"), not as a learner misconception. Nothing appended to `🧯 Mistakes.md`.
- **Dependency events** — none (`dependency_events: []`: no `just_tell_me`, no `declined_generation`, no `told_repair`; every State-rung generation was made). The 2026-10-09 **pacing request** is not an opt-out; it is carried in the position pointers, the t-SNE page's field notes and the CURRICULUM row.
- Historical L10 Last-Updated lines in the Learning Profile and Active Concepts were reworded so the word "Checkpoint" no longer sits before a fraction (repo convention) — the read-only position-pointer check reads them as history, not live pointers.
- `Core/Learner History.md` regenerated via `scripts/learner_history.py`.

## Lesson-vs-handoff agreement

The lesson file's `Status:` / `Resume from:` (paused at Checkpoint 4/6; CP4 minis 2 and 3/3b sealed 2026-10-09; resume CP4 mini 4 — Distill misreading protocol + the Rohit-vs-Distill contradiction) **agree** with the handoff `status` / `resume_from`; nothing to flag or merge. (The lesson file words the second half of mini 4 as "Rohit's unconditional-rule contradiction"; the handoff as "the Rohit-vs-Distill contradiction" — the same item.)

## Marker / digest

- `Core/Pending Ingest.json` — **cleared** (partial handoff: the marker only).
- Scout digest `Learning System/.tmp/context-01a0d78c-dbff-7362-bcea-13f8df10005b-dimensionality-reduction.json` — **kept** (partial close); it is 14 days old, past the 7-day TTL — **re-scout before teaching the remaining CP4/CP5 material from fresh sources** (the t-SNE/UMAP bodies remain unconsumed).
- Lesson file and the CURRICULUM row stay **in-progress**.

## Surfaces (not fixed)

- The aged Scout digest (TTL) and the kept-digest presence warning — both expected at a partial close.
- `📚 Active Concepts.md` → `Open Questions` still carries the stale `Curse of dimensionality` bullet claiming the concept "still has no Active Concepts row and no Attempts entry"; both exist since the 2026-10-07 ingest — reported, not merged (outside this ingest's touched scope).
