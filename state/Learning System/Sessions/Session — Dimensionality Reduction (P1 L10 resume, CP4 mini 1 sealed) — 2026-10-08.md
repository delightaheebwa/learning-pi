# Session — Dimensionality Reduction (P1 L10 resume, CP4 mini 1 sealed) — 2026-10-08

**Type:** teach (pause handoff) · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Position after session:** in-progress, **paused at Checkpoint 3/6 — CP4 mini 1 sealed** (CP3 fully sealed 2026-10-07). Resume **CP4 mini 2 — perplexity as 2^H on the neighbor distribution** (then KL(P‖Q) objective, Distill misreading protocol + the Rohit-vs-Distill contradiction).

## What happened

- **Warm-up (CP3 recall, quiz-audit PASS cycle 2; grade-audit agreed 2/3):** W1 B ✓ (round cloud: dropping anything keeps at most 90%), W3 D ✓ (concentration = nearest/farthest blur). **W2 ✗ fail** — picked B (huge dropped-axis coordinate) as the *escaping* point: the flagged-signature answer reused on an inverted frame ("which escapes" answered as "what gets caught").
- **W2 repair (diagnose-first → sealed):** detector restated (alarm fires only on across-dropped-axis distance; far-along-kept ⇒ error ≈ 0 ⇒ silent); micro-check (1,000 units out along a line-cloud's kept axis) answered **missed** ✓.
- **Learner tangent — why never flag far-along points? (sealed, DIVE-style, on-path):** two clarifications + a deep repair. (1) **Shape vs depth:** error = shape mismatch (across), not distance from the crowd (along); normal data spreads hugely along kept axes (the big λ's), so far-along is "more of the normal direction"; catching it needs a stacked **depth-style check** (kept-coordinate vs training range; Mahalanobis/Hotelling-T² practice — fact-check verified as standard Q+T² stacking). (2) **Unit vs signal:** every residual lives in the dropped subspace *by construction* — that's the unit, like Celsius; the flag reads its **length** against the threshold set by training residuals. (3) **Directions get dropped; points never do:** the compression discards every point's across-coordinate identically; residual size decides flagged/not-flagged, never keep/drop. Fisher-style one-picture consolidation delivered and verified. Learner sealed with "a big residual tells me the point is an outlier as compared to the normal data" (pass, sharpened: outlier-ness is about *shape*).
- **CP4 mini 1 — t-SNE neighborhoods (sealed via elicit → attempt → consolidate):**
  - E1 prediction (Swiss roll, PCA keeps top-2): "flat 2D plane; neighbors stay neighbors" — flat-plane half fine, neighbor half wrong.
  - Guiding Q1 (carpet-roll pressed between glass panes): learner refused "unrolled sheet" ✓, geometry still muddled ("lie on a straight line relative to each other").
  - Guiding Q2 (the two layer-points land close): learner's own words — **"non-neighbors can become neighbors in the flatten and i guess that doesnt work for the vice versa case"** — exactly right.
  - Consolidated (fact-check PASS 4/4, cycle 2 after attribution fix): linear squash can only shrink/preserve distances ⇒ true neighbors never torn apart, but distinct regions collapse ⇒ **false neighbors**; the flatten is a smeared shadow, not the unrolled sheet. **Attribution fix:** the pairwise-probability mechanism (near = high prob, far = low prob, find the 2D arrangement matching it) is **already in Rohit's source**; Distill's distinctive add is the misreading/interpretation-caution layer (dramatic clusters in pure noise at low perplexity; cluster sizes/distances misleading) — parked for CP4 mini 4. Synthesis: PCA's squash blurs the neighborhood pattern; t-SNE's job is defending it, with failure modes of its own to be named before trusting any picture.
  - Check-back: learner confirmed the why-now landed ("yeah makes sense").
- **Pause exit ticket (today's material only; quiz-audit PASS cycle 3; grade-audit agreed 3/3, all sure):** X1 B ✓ (unrelated sheet regions collapsed into apparent neighbors) · X2 C ✓ (reconstruction error = residual length off the kept subspace) · X3 D ✓ (depth-style kept-coordinate range check needed in addition).
- **Attempts (ops.py):** PCA (Dimensionality Reduction) fail (warm-up W2), pass (exit ticket) → mastery 0.75, interval_index 3, next_review 2026-11-07.

## Concepts touched

- **`PCA (Dimensionality Reduction)`** — anomaly-tangent deepening (shape-vs-depth, unit-vs-signal, depth-check stacking) + pause exit ticket; attempts fail→pass logged (mastery 0.75, next 2026-11-07). No wiki/Active Concepts writes by the Tutor — queued via `Core/Pending Ingest.json`.
- **`t-SNE (Dimensionality Reduction)`** — **candidate new row** (Type `concept`): CP4 mini 1 only (goal + pairwise-probability mechanism, false-neighbors failure of linear squashes, non-linearity "unfolds complex manifolds PCA cannot"). Rowless today.
- **`Curse of dimensionality`** — still rowless (carried candidate from 2026-10-07); re-touched only via warm-up W3.

## Position pointers (to reconcile at /ingest)

Lesson file `Status:`/`Resume from:` updated today (paused CP3 3/6 — CP4 mini 1 sealed; resume CP4 mini 2). `MISSION.md`, `CURRICULUM.md`, `Core/💡 Learning Profile.md`, `Core/📚 Active Concepts.md` still say **paused at Checkpoint 2/6 or 3/6 pre-CP4** — Clerk to realign all four at next ingest: **paused at Checkpoint 3/6 — CP4 mini 1 sealed; resume CP4 mini 2 (perplexity as 2^H)**; sync the PCA row from Attempts.json (mastery 0.75, interval_index 3, next_review 2026-11-07, last_reviewed 2026-10-08); create the `t-SNE (Dimensionality Reduction)` candidate row; still consider the `Curse of dimensionality` row (carried 2026-10-07); fix the Distill-vs-Rohit attribution in any wiki text that credits the probability framing to Distill (it is in Rohit's source; Distill = interpretation cautions).

## Handoff

- Marker: `Core/Pending Ingest.json` (partial handoff — anomaly tangent + CP4 mini 1; no wiki pages authored by the Tutor, one attribution-fix note for the Clerk).
- Practice rule in force: paper walks / graded MCQ batches only; no code as a learning-system task (learner, 2026-10-05).
- Open items for CP4: mini 2 perplexity-as-2^H reframe (learner's banked "3 bits → 8" anchor) → mini 3 KL(P‖Q) objective (asymmetry; Distill t-heavy-tail justification) → mini 4 Distill misreading protocol + the ⚠️ Rohit-vs-Distill contradiction (⚠️ resolved 2026-10-08 in draft as: Rohit = safe default, Distill = fragile exception under tuning; also Rohit already carries the probability mechanism — surface the contradiction loudly when taught).
- Mistake candidate carried: PCA frame-inversion slip (structural; sealed same session). No other mistakes today; no Feynman item today (mid-checkpoint pause, not lesson end).
