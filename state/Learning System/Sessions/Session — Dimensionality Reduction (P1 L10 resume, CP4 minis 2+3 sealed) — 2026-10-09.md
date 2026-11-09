# Session — Dimensionality Reduction (P1 L10 resume, CP4 minis 2+3 sealed) — 2026-10-09

**Type:** teach (pause handoff) · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Position after session:** in-progress, **paused at Checkpoint 4/6 — CP4 minis 2 and 3/3b sealed** (mini 1 sealed 2026-10-08; CP3 fully sealed 2026-10-07). Resume **CP4 mini 4 — Distill misreading protocol + the Rohit-vs-Distill contradiction**, then the CP4 practice.

## What happened

- **Warm-up (CP4 mini 1 recall, quiz-audit PASS cycle 1; grade-audit agreed 3/3, all sure):** W1 B ✓ (collapsed roll layers = false neighbors) · W2 A ✓ (shrink-or-preserve: a close pair can never end up farther apart than it was) · W3 ✓ in own words — "t-SNE ensures only true neighbors stay neighbors while PCA introduced false neighbors. t-SNE did this by ensuring the probability distribution of the points from before any transformation happens, is the same afterwards."
- **CP4 mini 2 — perplexity (sealed via elicit → state → check-and-extend; no guiding question needed):**
  - E1 prediction (hunch): **"i think it will control how many true neighbors each point will keep."** — right idea.
  - Check-and-extend: (1) *effective, not exact* — a soft count, can be 23.7; Rohit: "Controls the effective number of neighbors each point considers." (2) *name-collision reframe* — the SAME banked $2^H$ applied to each point's neighbor distribution: $\mathrm{Per}(P_i) = 2^{H(P_i)}$; per-point $\sigma_i$ tuned until $\mathrm{Per}(P_i)$ = knob. (3) *what the knob buys* — low = very local structure, high = broader patterns (Distill: balancing attention local vs global); typical 5–50; guardrail: perplexity must be smaller than the number of points.
  - Check-back (20-point dataset, perplexity=30?): learner — **"now attention has to be made on effectively 30 points yet there are 20 and i think attention on some points that dont even exist will confuse the model."** Right instinct; sharpened with his own $2^H$: uniform over the 19 other points → $H = \log_2 19 \approx 4.25$ bits → ceiling $\mathrm{Per} \approx 19$; knob 30 = unreachable target ("confuse the model" = fair gloss, exact failure = unreachable target). (fact-check PASS 6/6.)
- **CP4 mini 3 — KL(P‖Q) objective (sealed via elicit → state → check-and-extend):**
  - E2 prediction: **"it is trying to bring the kl divergence to zero since bringing it to zero would mean there is no deviation between the two distributions."** — right, one word off.
  - Check-and-extend: **minimize**, not zero — zero unattainable (2D can't honor every neighborhood); $P$ frozen (it IS the data), $Q$ the only thing that moves (gradient descent on the 2D coordinates); asymmetry — $\mathrm{KL}(P\|Q) = \sum_i P_i \log \frac{P_i}{Q_i}$, weights from $P$ ⇒ "data says near, map says far" is the expensive mismatch. (fact-check PASS 5/5.)
  - Check-back → learner: **"the distribution of the actual data supplies the weights. the mismatch that gets a big penalty is a high supplied weight(the data says a point is near) but the 2D map says the point is far(small probability)"** — exactly right.
- **CP4 mini 3b — heavy-tail t justification (sealed via elicit → 1 guiding question → check-and-extend):**
  - E3 prediction: **"squeezing that to 2D reduces the number of medium-distance neighbors, and a slower falloff helps to keep as many medium-distance neighbors as possible"** — squeeze right, benefit direction muddled.
  - Guiding Q (budget: 1 — cheap or expensive to place a moderately-related pair far apart under a heavy-tailed Q?): learner — **"it is cheap for the map to place moderately related pairs far apart... the map will then spread out the crowded medium-distance pairs"** — conclusion right, **reason flipped** ("multiply the moderate weight by a low probability" = product model; actual cost is the log-ratio).
  - Check-and-extend: cost = $P_i \log \frac{P_i}{Q_i}$, P-weighted log-ratio (not a product); Gaussian $Q$ collapses $Q_i \to 0$ at distance ⇒ log blows up ⇒ spreading expensive; t-distribution fat tail keeps $Q_i$ from collapsing ⇒ spreading affordable; big-$P$ pairs still pay to separate ⇒ local structure preserved while the crowded medium band gets room. Chain: squeeze → crowd → Gaussian fines every escape → heavy tail makes escape cheap → crowding relieved without tearing true neighborhoods (JMLR: "mismatched tails compensate for mismatched dimensionalities"). (fact-check PASS 6/6.)
  - **Learner pacing call:** he flagged mini 3b as loaded — "i feel we should unpack more... we should slow down there before moving ahead" — and asked to pause. Mini 4 deferred at his request; re-offer a re-walk of the 3b cost picture next session.
- **Pause exit ticket (today's material only; quiz-audit PASS cycle 2 after length-parity + distractor fixes; grade-audit agreed 3/3, all sure):** X1 B ✓ (15 valid: in 5–50 and under the ceiling 19) · X2 C ✓ (Q only — 2D coordinates move; P frozen from data) · X3 B ✓ (P·log(P/Q) blows up as Gaussian Q collapses toward zero with P non-zero).
- **Attempts (ops.py):** t-SNE (Dimensionality Reduction) pass ×2 (warm-up + exit ticket, both discriminative, sure, hints 0) → mastery **0.80**, interval_index 3, next_review 2026-11-08; prereq edge recorded: t-SNE → KL Divergence.

## Concepts touched

- **`t-SNE (Dimensionality Reduction)`** — CP4 minis 2 + 3/3b (perplexity as 2^H on $P_i$; KL(P‖Q) objective + asymmetry; heavy-tail t/crowding justification). Mastery 0.80, interval_index 3, next_review 2026-11-08. No wiki writes by the Tutor — queued via `Core/Pending Ingest.json`. (Candidate row carried from 2026-10-08.)
- **`Perplexity`** — no graded attempt today (elicit was ungraded); existing row untouched by the Tutor. Mastery 0.81, next_review 2026-11-02 (from ops.py).
- **`KL Divergence`** — used as the bridge prereq (mastery 1.00); prereq edge recorded on t-SNE; no attempt row written.

## Learner understanding (verbatim, for wiki `## My understanding`)

- **t-SNE / perplexity:** "i think it will control how many true neighbors each point will keep." (plus the ceiling check-back: "now attention has to be made on effectively 30 points yet there are 20...")
- **t-SNE / objective:** "it is trying to bring the kl divergence to zero since bringing it to zero would mean there is no deviation between the two distributions"; check-back: "the distribution of the actual data supplies the weights. the mismatch that gets a big penalty is a high supplied weight(the data says a point is near) but the 2D map says the point is far(small probability)"
- **t-SNE / heavy tails:** "I think it is cheap for the map to place moderately related pairs far apart. It is cheap because, if they are far away, we are multiplying the moderate weight by a low probability; hence, it is cheap to do so. Based on that, the map will then spread out the crowded medium-distance pairs." (⚠️ conclusion right, reason flipped — repaired in-session to the log-ratio picture.)

## Position pointers (to reconcile at /ingest)

Lesson file `Status:`/`Resume from:` updated today (paused CP4 4/6 — minis 2 + 3/3b sealed; resume CP4 mini 4). `MISSION.md`, `CURRICULUM.md`, `Core/💡 Learning Profile.md`, `Core/📚 Active Concepts.md` still carry the 2026-10-08 position — Clerk to realign all four at next ingest: **paused at Checkpoint 4/6 — CP4 minis 2 and 3/3b sealed; resume CP4 mini 4 (Distill misreading protocol + Rohit contradiction)**; sync the t-SNE row from Attempts.json (mastery 0.80, interval_index 3, next_review 2026-11-08, last_reviewed 2026-10-09).

## Handoff

- Marker: `Core/Pending Ingest.json` (partial handoff — CP4 minis 2 + 3/3b; no wiki pages authored by the Tutor).
- Practice rule in force: paper walks / graded MCQ batches only; no code as a learning-system task (learner, 2026-10-05).
- Open items for CP4: mini 4 Distill misreading protocol (cluster sizes meaningless; cluster distances meaningless at arbitrary perplexity; distances meaningful only at tuned perplexity) + the ⚠️ Rohit-vs-Distill contradiction (resolved 2026-10-08 in draft: Rohit = safe default, Distill = fragile exception under tuning — surface loudly when taught); then the CP4 practice; carry the 3b "unpack more" pacing request.
- Mistakes: none today (no graded fail). **Dependency events: 0** (no just_tell_me / declined_generation; all State-rung generations made). No Feynman item (mid-checkpoint pause, not lesson end).
