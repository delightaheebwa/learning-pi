# Session — Optimization (Gradient Descent Family) — 2026-09-08

> **Track:** AIEFS · **Phase 1 L08** · **Status:** paused at Checkpoint 4/5 (exit-check pending)

## Resume (2026-09-08)

- Re-seal zigzag vs overshoot: **PASSED** — (A) large η → overshoot, fix smaller η; (B) narrow valley → zigzag, fix momentum.
- CP3 Adam: taught (lineage Adagrad→RMSprop→Adam + bias correction), built `Adam`, ran 3-optimizer race. Exit check passed.
- CP4 saddle points + mini-batch noise: **taught** (corrected attribution: Dauphin 2014 not Li 2018), **exit check not yet administered**.

## Race result (emerged in CP3)

- Vanilla GD: never converged (5.7e-05, zigzag) · Momentum: ~2941 steps (2.2e-29) · Adam: ~6156 steps (4.6e-13).
- Momentum fastest on clean deterministic Rosenbrock — Adam's per-weight adaptivity unneeded here.

## Exit ticket (2026-09-08)

- P1 β₁/β₂ roles: B sure ✅ · P2 race result: C sure ✅ · P3 bias correction: ✅ in own words.
- Attempts recorded (all pass): Adam, Momentum, Gradient Descent. Adam de-duplicated to single pass.

## Corrections made during teach

- CP3 exit Q1: "sharp" → "narrow" (sharpness is CP5, generalization term).
- CP3 exit Q2: β₁/β₂ roles briefly swapped ("velocity" label → momentum; "step size based on m" → based on v).
- CP4/Adam fact-check: saddle dominance attributed to Dauphin et al. 2014, NOT Li et al. 2018 (filter normalization).

## Resume from

CP4 exit check (3 items, already written in lesson file) → CP5 (LR schedules + sharp/flat minima) → SHIP (Rosenbrock race artifact + optimizer-choice prompt).
