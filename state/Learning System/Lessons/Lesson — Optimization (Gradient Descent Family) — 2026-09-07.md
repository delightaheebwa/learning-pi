# Lesson — Optimization (Gradient Descent Family) — 2026-09-07

> **Track:** AIEFS · **Phase 1, Lesson 08** · **Lang:** Python
> **Status: DONE 2026-09-10** (all 5 checkpoints + SHIP + cumulative quiz + Feynman pass)

## Sources

- Rohit: `phases/01-math-foundations/08-optimization/docs/en.md`
- Ruder — gradient descent survey · Goh — Why Momentum Really Works (Distill) · Kingma & Ba — Adam (2015) · Li et al. — Loss Landscape (2018)
- Scout digest: `Learning System/.tmp/context-current-p1l08-optimization.json`

## Probe verdict (2026-09-07)

| Strand | State | Evidence |
|---|---|---|
| Gradient = steepest ascent, step opposite | **solid** | Q1 C sure, Q7 correct |
| Learning-rate overshoot | **solid** | Q2 A sure |
| Chain rule multiplies | **solid** | Q3 D sure + prior pass (2026-09-05) |
| Cross-entropy = −log | **solid** | Q5 D sure — *09-06 structural mistake resolved* |
| Why mini-batch noise helps | **unknown** | Q4 B hunch (lucky) + Q8 wrong reason ("overfitting") |
| Saddle point vs local min | **unknown** | Q6 answered "local minimum" |

## Checkpoints completed

### Checkpoint 1 — Loss landscape & vanilla gradient descent ✅

- \(w \leftarrow w - \eta\nabla L(w)\); gradient points uphill, we step opposite.
- Learning rate = most important hyperparameter (too large → diverge/bounce; too small → crawl).
- Rosenbrock \(f(x,y)=(1-x)^2+100(y-x^2)^2\), min at (1,1), narrow curved valley.
- Built `GradientDescent` + `rosenbrock_gradient`. Paper practice: one step from (−1,1), η=0.0005 → grad (−4,0) → (−0.998,1). Correct.

### Checkpoint 2 — Momentum ✅

- \(v \leftarrow \beta v + g,\ w \leftarrow w - \eta v\), β=0.9.
- Goh's deeper mechanism: momentum rescales effective step size per Hessian eigenvector direction, equalizing convergence across curvature.
- Velocity accumulates along-valley (x, consistent sign) and cancels across-walls (y, oscillates).
- Built `SGDMomentum`. Paper practice: v1=(−4,0), step → (−0.9996,1). Correct.
- Exit check (why x direction): **passed** — named direction + "toward minimum"; reason sharpened to selective accumulation.

## Exit ticket (pause) — 2026-09-07

| Item | Answer | Verdict |
|---|---|---|
| E1 (GD struggle in valley) | D sure | ❌ — said overshoot (lr) instead of zigzag |
| E2 (momentum accumulates along x) | B sure | ✅ |
| E3 (momentum update in words) | — | ✅ — "90% previous speed + gradient" |

## Re-seal (2026-09-08) — zigzag vs overshoot ✅ PASSED

- (A) large η → **overshoot** (diverge/bounce), fix = smaller η · (B) narrow curved valley → **zigzag**, fix = momentum.
- E1 conflation resolved.

### Checkpoint 3 — Adam ✅ (2026-09-08)

- Adam = momentum (m, β₁=0.9) + RMSprop (v, β₂=0.999) + bias correction, Kingma & Ba 2015.
- Lineage (Ruder): SGD → Adagrad (running sum of g², collapses lr to 0) → RMSprop (decaying avg fixes it) → Adam (adds momentum + bias correction).
- \\(m \\leftarrow \\beta_1 m + (1-\\beta_1)g\\); \\(v \\leftarrow \\beta_2 v + (1-\\beta_2)g^2\\); update \\(w \\leftarrow w - \\eta\\hat{m}/(\\sqrt{\\hat{v}}+\\epsilon)\\).
- Bias correction \\(\\hat{m}=m/(1-\\beta_1^t)\\) — fixes zero-init cold start (first steps too timid); fades to 1 as t grows.
- Built `Adam` class + ran 3-optimizer race on Rosenbrock: Vanilla GD never converged (5.7e-05, zigzag), Momentum converged ~2941 steps (2.2e-29), Adam ~6156 steps (4.6e-13). **Momentum fastest on this clean deterministic benchmark** — Adam slower, its per-weight adaptivity unneeded here.
- Exit check: Q1 (why vanilla GD stuck = zigzag, not sharpness — corrected 'sharp'→'narrow') ✅; Q2 (β₁=mean grad direction, β₂=mean grad² scale — corrected swapped roles/v-label) ✅.
- Attempts recorded: Adam, Momentum, Gradient Descent (vanilla) — all pass, interval_index 1.

## Exit ticket (pause) — 2026-09-08

| Item | Answer | Verdict |
|---|---|---|
| P1 (β₁/β₂ roles) | B sure | ✅ |
| P2 (race result) | C sure | ✅ |
| P3 (bias correction why) | — | ✅ — cold start, zero-init shrinks early steps, (1−βᵗ) un-shrinks until history accumulates |

## Checkpoint 4 — saddle points + mini-batch noise ✅ (sealed 2026-09-10)

- Critical-point triage via Hessian: local min (PSD, all λ≥0) · local max (NSD) · saddle (mixed-sign λ).
- High-dim: saddle points dominate ~exponentially in d (Dauphin et al. 2014, via Ruder) — NOT Li et al. 2018 (that's filter-norm loss-surface smoothing).
- Vanilla GD stalls at a saddle (∇=0). Mini-batch noise makes the gradient a non-zero random variable → nudge off saddle. This is an *optimization* effect (escape stall), distinct from noise's *regularization* effect (train-test gap).
- **Resolved probe Q6** (local min → saddle) & **Q8** (overfitting → escape-stall mechanism).

### Exit check (2026-09-10) → re-seal

| Item | Answer | Verdict |
|---|---|---|
| Q1 (classify + stall) | B sure | ✅ |
| Q2 (why saddles dominate) | C hunch | ❌ → re-seal R1 B sure ✅ |
| Q3i (stuck + unstick) | free recall | ✅ |
| Q3ii (OTHER effect = generalization) | free recall | ❌ → re-seal R2 ✅ |

- Q2 miss: answered "loss surface convex in most directions" (wrong premise). Correct = counting argument: local min needs all d eigenvalue signs positive ≈ (1/2)^d, exponentially tiny; saddle needs one sign to differ. (Coin-flip model = heuristic, not exact law.)
- Q3ii miss: correction-over-rotation from 09-07 — restated the optimization (escape-stall) half, dropped the generalization half. Noise has TWO distinct effects: (1) optimization — noisy gradient never exactly zero, no stall; (2) generalization — prevents settling into sharp minima (sharp generalize poorly, flat generalize well).
- Re-seal passed → CP4 sealed. Attempts recorded (Saddle Points, Mini-batch Noise — both fail→pass, mastery 0.62). Mistake logged (Mini-batch Noise two effects, structural).

## Checkpoint 5 — LR schedules + sharp/flat minima ✅ (sealed 2026-09-10)

- Schedules exist because a fixed lr is a compromise: large steps early, small steps late. Four types: step decay · exponential (lr = lr_0·decay^t, no floor) · cosine annealing (lr = lr_min + 0.5(lr_max−lr_min)(1+cos(πt/T)); starts at lr_max, lands on lr_min = nonzero FLOOR) · warmup+decay (linear ramp-up → decay; only one with ramp-up, for large-model early instability).
- Ruder critique: schedules set in advance (can't adapt to dataset) + same rate for all params — the gap Adam's adaptivity fills.
- Sharp vs flat minima (Li et al. 2018 filter-norm visualization): sharp generalize poorly, flat generalize well — the CP4 generalization effect.
- Exponential-decay insight: 0.999^1000 ≈ 0.368, 0.999^5000 ≈ 0.0067 → decay factor sets a characteristic timescale (half-life ≈ 693 steps).

### Exit check → re-seal → rebuild

- Q2 (Ruder two limits) ✅ · Q3 (sharp vs wide) ✅ · Q4 (why schedule + what Adam fixes) ✅.
- Q1 miss (cosine when warmup correct — 'sure'). Re-seal R1 miss (exponential when cosine correct — 'sure'). **Two consecutive confident misses → dropped a rung, rebuilt schedules as η-vs-t curves on two axes (early phase / end behavior).**
- Numeric re-check: 3/4 (missed floor value — transposed 0.999 decay factor into floor slot; floor = η_min itself). Final confirm 0.05 ✅. **Floor concept sealed.**
- Attempts recorded (Learning-rate Schedules: fail×2 → pass, mastery 0.44). Mistake logged (structural).

## SHIP — optimizer choice ✅ (2026-09-10)

- Rosenbrock race (CP3) is an **artifact** of a clean deterministic low-dim *ill-conditioned* test function (narrow curved valley) with run-specific hyperparameters — NOT general evidence momentum > Adam in practice. Note: Rohit's own defaults expect Adam fastest; the ordering flips with lr choices.
- Rohit heuristic: start Adam (lr=0.001) → switch SGD+M (lr=0.01, β=0.9) for best final accuracy → AdamW (decoupled weight decay) for transformers; always schedule long runs.
- "SGD for best accuracy" ties back to sharp/flat minima (CP4/CP5): Adam can settle in sharp minima, SGD's noise → flat minima.
- Four knobs: Adam (adaptivity) · SGD+M (flat minima) · AdamW (transformers) · LR schedule (large-early/small-late).

## Final quiz (cumulative) — 2026-09-10

- Q1–Q6 MCQ: **6/6 sure** (CP1 minus sign · CP2 momentum · CP3 bias correction · CP4 saddles · CP5 floor · SHIP AdamW).
- Q8 optimizer selection ✅ (Adam prototype / SGD+M ship).
- Q7 (two effects of noise) ❌ 4th recurrence → final re-seal ✅ (optimization=saddle escape / generalization=sharp-minima avoidance).

## Feynman explain-back — ✅ PASS (2026-09-10)

- Own-words synthesis: "talking bird on your shoulder tells you the next best step down the mountain (loss)" + "what's the best minima I can be in, and the fastest route to reach it" — reproduced the lesson's closing synthesis.

## Concepts banked (2026-09-08 + 2026-09-10)

- Gradient Descent (vanilla) — procedure ✅ (Feynman pass 2026-09-10, mastery 0.80)
- Learning Rate — concept ✅ · Momentum — procedure ✅ · Adam — procedure ✅ (2026-09-08)
- Saddle Points (critical point triage) — concept ✅ (2026-09-10, mastery 0.62)
- Mini-batch Noise (two effects) — concept ✅ (2026-09-10, mastery 0.61 — 4 recurrences, final re-seal pass)
- Learning-rate Schedules (four types) — concept ✅ (2026-09-10, mastery 0.44 — dropped rung, rebuilt as curves)
- Optimizer Selection (Rohit heuristic) — concept ✅ (2026-09-10, mastery 0.80)

## Concepts (banked today, 2026-09-08)

- Gradient Descent (vanilla) — procedure ✅
- Learning Rate — concept ✅
- Momentum (SGD with Momentum) — procedure ✅
- Adam (adaptive moments) — procedure ✅ (NEW today)
