# Review — PMF vs PDF — 2026-11-08

- **Track/Source:** aiefs — Rohit P1 L06 + CS229 (Python)
- **Type:** concept · **Q type:** `discriminative` → **Last Q Type `discriminative`**
- **Why this slot:** priority-1 due mistake — the 2026-09-11, 2026-10-17 and 2026-11-04 ledger rows all carried next retry 2026-11-07, and the concept was the second mistake slot of the deterministic queue; the longest-running thread in the ledger (this is its fifth graded review item on the density→probability conversion).
- **Question:** the verbatim prompt text was **not carried in the handoff envelope** — recorded as a handoff gap, not reconstructed. The envelope carried the item's type, the delivery-delay density `f(2.5) = 0.13` framing, the learner's verbatim answer and the graded gap.
- **Targets retrieved (recorded on the attempt, all live in the graph ledger):** `n_2fa8fc5801` (Probability mass function), `n_b4a16474b3` (PMF assigns point probabilities).

## Learner answer (verbatim)

"that sentence assumes 0.13 is a probability but it is density which is being measured. to get proabialty i would mutliply the desnity with the number of hours."

## Verdict

**FAIL** — confidence `hunch`, 0 hints, miss_class `execution`, `pow: none` (grade-audit agreed).

## Why

The separation itself was made — "0.13 is density, not a probability" is exactly the reading that failed on 2026-10-08, 2026-10-17 and 2026-11-04, so the label inversion did **not** recur this time. What failed is the conversion half: "multiply the density with the number of hours" never becomes an integral over an interval around 2.5, `P(X exactly 2.5) = 0` is never stated, and no direction/extreme check is run (a probability must land in [0, 1]). This is the same point-reading/conversion thread narrowing again — from the point reading to the probability-conversion step.

## Recorded state

- **Attempts.json:** one attempt dated 2026-11-08 — `fail` (`discriminative`, `hunch`, hints 0, targets `n_2fa8fc5801,n_b4a16474b3`). Net: `interval_index` 0 → **0** (clamped), `consecutive_correct` 0, `consecutive_wrong` 1 → **2**, `last_reviewed` 2026-11-04 → **2026-11-08**, `next_review` 2026-11-07 → **2026-11-11** (concept ladder, +3d at index 0), mastery **0.15** advisory, Feynman flag `fail` unchanged (no explain-back result carried).
- **Mistakes ledger:** **one new row** dated 2026-11-08 — error_type `application` / `[miss: execution]` / `[targets: n_2fa8fc5801,n_b4a16474b3]` / `active` / retries 0 / next retry **2026-11-11**. The envelope's `error_type` `execution` is not in the ledger enum (`structural / deviation / application / metacognitive`) and was canonicalized to `application` = "knew but applied wrong", the envelope's own diagnosis preserved in the `[miss: execution]` prefix. The pre-existing same-thread rows (2026-09-11, 2026-10-17, 2026-11-04) were left untouched.
- **Active Concepts:** row synced — `last_reviewed` 2026-11-04 → **2026-11-08**; `next_review` 2026-11-07 → **2026-11-11**; `Last Q Type` stays **discriminative**; mastery 0.15 advisory.
- **Advisory mastery:** **0.15** — Feynman: `fail` (unchanged).

## Carry-forward

The conversion step, asked in the same breath as the label reading next time: `P(a < X < b) ≈ f(2.5) × (b − a)` — a density times a **width**, not a density times a count of hours — and `P(X = 2.5) = 0`. The label half is now banked; only the operation is open.
