# Review — Optimizer Selection (Rohit heuristic) — 2026-11-08

- **Track/Source:** aiefs — Rohit P1 L08 + handwritten notes 2026-09-10 (Python)
- **Type:** concept · **Q type:** `explain-back` (the mandatory clone/Feynman check, P1.1) → **Last Q Type `explain-back`**
- **Why this slot:** scheduled due review — `next_review` was 2026-10-24 (the longest overdue aiefs row after the mistake slots) and it still carried an open `active` row from the 2026-10-10 Feynman fail.
- **Question:** the verbatim prompt text was **not carried in the handoff envelope** — recorded as a handoff gap, not reconstructed. The envelope carried the item's type, the learner's verbatim answer and the clone receipt.
- **Target retrieved (recorded on the attempt, live in the graph ledger):** `n_05cfdf0c5b` (Plain SGD is chosen for control or tuned schedules).

## Learner answer (verbatim)

"reach for adam first with a small step size. i would pick sgd with momentum when final accuracy matters otherwsie i will stick with adam since there is less manual tuning."

## Verdict

**FAIL** — confidence `hunch`, 0 hints, miss_class `structural`, `pow: clone`, recorded `feynman_fail` (grade-audit agreed).

## Why

The **shape** of the heuristic survived: start from Adam, keep SGD+momentum as the control neighbour, and the lighter-tuning argument for staying on Adam is right. But it is not executable. "When final accuracy matters" names a **priority**, not an observable regime — nothing in a running training curve tells you you are in it, so there is no mid-run cue for the switch. Missing with it: the step-size carry-over (Adam at 1e-3 → SGD+momentum at ~1e-2 with 0.9 momentum), the failure regime of the Adam default, and the mechanism behind "maximum control". The naive-student clone run confirmed it: given the answer as a policy, the clone produced "Adam at 0.001 always, never switch" — `task_succeeded: false`, the switch rule could not execute.

## Battery / evidence

- `pow: clone` — naive-student clone, receipt `task_succeeded: false` (predicted "Adam at 0.001 always, never switch"). Recorded alongside the attempt, and the item's `feynman_fail` is stored on the concept's flag (stays `fail`).
- No `just_tell_me` reveal; no MCQ key (MCQ-free session).

## Recorded state

- **Attempts.json:** one attempt dated 2026-11-08 — `fail` (`explain-back`, `hunch`, hints 0, targets `n_05cfdf0c5b`), with `feynman_fail`. Net: `interval_index` 2 → **1**, `consecutive_correct` 0, `consecutive_wrong` 1 → **2**, `last_reviewed` 2026-10-10 → **2026-11-08**, `next_review` 2026-10-24 → **2026-11-15** (concept ladder, +7d at index 1), mastery **0.35** advisory, Feynman flag `fail` (re-recorded as fail).
- **Mistakes ledger:** **one new row** dated 2026-11-08 — `structural` / `[miss: structural]` / `[targets: n_05cfdf0c5b]` / `active` / retries 0 / next retry **2026-11-15**. The 2026-10-10 row of this thread stays `active` (retries 0) and was left untouched.
- **Active Concepts:** row synced — `last_reviewed` 2026-10-10 → **2026-11-08**; `next_review` 2026-10-24 → **2026-11-15**; `Last Q Type` stays **explain-back**; mastery 0.35 advisory.
- **Advisory mastery:** **0.35** — Feynman: `fail`.

## Carry-forward

The switch as a rule someone else could run: Adam at `lr = 1e-3` first (no tuning, fast early progress); if the run plateaus short of the accuracy you need **and** you have tuning budget, switch to SGD + momentum at `lr = 1e-2`, momentum 0.9, continued from the current weights — that is "maximum control" because every hyperparameter is yours to set, and its known failure regime is the tuning cost plus the sharp/flat minima default. "Final accuracy matters" has to become "the plateau you can see".
