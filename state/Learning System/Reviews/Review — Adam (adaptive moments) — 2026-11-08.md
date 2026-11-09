# Review — Adam (adaptive moments) — 2026-11-08

- **Track/Source:** aiefs — Rohit P1 L08 + Kingma & Ba 2015 + Ruder + handwritten notes 2026-09-08 (Python)
- **Type:** procedure · **Q type:** `free-recall` → **Last Q Type `free-recall`** (procedure → Feynman/explain-back exempt, P1.1)
- **Why this slot:** scheduled due review — the row's `next_review` was 2026-11-07 and it carried an open 2026-11-04 structural ledger row on the estimates-vs-ratio separation.
- **Question:** the verbatim prompt text was **not carried in the handoff envelope** — recorded as a handoff gap, not reconstructed. The envelope carried the item's type, the two-running-averages / step-1-numerics / W1-vs-W2 framing, the learner's verbatim answer and the graded gap.
- **Target retrieved (recorded on the attempt, live in the graph ledger):** `n_83c18bba5f` (Adam update rule and default hyperparameters).

## Learner answer (verbatim)

"it isnt compleete. the two runnign avergaes become so small because the gradient is zero initialised. i`m not sure why they have different step sizes."

## Verdict

**FAIL** — confidence `hunch`, 0 hints, miss_class `structural`, `pow: none` (grade-audit agreed).

## Why

The "incomplete" verdict is right and the zero-initialisation cue is right, but the mechanism was attributed backwards: the bias correction **divides** each zero-seeded average by `(1 − β^t)`, and at step 1 (`t = 1`) that division inflates `m₁ = 0.1g` and `v₁ = 0.001g²` back to the size of the raw gradient and its square. The first effective step is therefore ≈ `eta` regardless of how small the gradient is — the estimates are small, the corrected ratio is not. The W1-vs-W2 half was left unanswered entirely ("i'm not sure why they have different step sizes"): both step sizes are ≈ `eta` because `m̂/√v̂` is dimensionless and self-normalising (adaptive equalisation per weight). This is the third session in a row on the same thread (2026-10-20 discriminator, 2026-11-04 ratio) and the failure has moved from the names of the two averages to the arithmetic of the correction.

## Recorded state

- **Attempts.json:** one attempt dated 2026-11-08 — `fail` (`free-recall`, `hunch`, hints 0, targets `n_83c18bba5f`). Net: `interval_index` 0 → **0** (clamped), `consecutive_correct` 0, `consecutive_wrong` 1 → **2**, `last_reviewed` 2026-11-04 → **2026-11-08**, `next_review` 2026-11-07 → **2026-11-11** (procedure ladder, +3d at index 0), mastery **0.15** advisory.
- **Feynman:** exempt (procedure row, P1.1) — flag unchanged.
- **Mistakes ledger:** **one new row** dated 2026-11-08 — `structural` / `[miss: structural]` / `[targets: n_83c18bba5f]` / `active` / retries 0 / next retry **2026-11-11**. The pre-existing same-thread rows (2026-09-26, 2026-10-03, 2026-10-20, 2026-11-04) were left untouched.
- **Active Concepts:** row synced — `last_reviewed` 2026-11-04 → **2026-11-08**; `next_review` 2026-11-07 → **2026-11-11**; `Last Q Type` definitional → **free-recall**; mastery 0.15 advisory.
- **Advisory mastery:** **0.15**.

## Carry-forward

The correction arithmetic, in one line: `m̂_t = m_t / (1 − β₁^t)`, `v̂_t = v_t / (1 − β₂^t)` — at `t = 1`, `m̂₁ = g`, `v̂₁ = g²`, so `m̂/√v̂ = sign(g)` and the step is `≈ eta · sign(g)` whatever the gradient's size. W1 and W2 take **the same** step; that is the equalisation half.
