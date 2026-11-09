# Review — Learning-rate Schedules (four types) — 2026-11-08

- **Track/Source:** aiefs — Rohit P1 L08 + Ruder + handwritten notes 2026-09-10 (Python)
- **Type:** concept · **Q types asked:** `discriminative` (Q1) then `error-detect` (Q3, perturbation PoW) → **Last Q Type `error-detect`**
- **Why this slot:** priority-1 due mistake — the two 2026-09-10 ledger rows and the 2026-10-22 row all carried next retry 2026-11-05; the concept was the first mistake slot of the deterministic queue digest (`Learning System/.tmp/review-01a1b316-9376-7641-aa6c-71100ad9c6c7-aiefs.json`).
- **Questions:** the verbatim prompt text was **not carried in the handoff envelope** — the envelope carried each item's type, the learner's verbatim answer and the graded gap. Recorded as a handoff gap, not reconstructed.

## Q1 — discriminative (scheduled due review; the two runs read off their curves)

- **Learner answer (verbatim):** "run a- cosine annealing, it ends at a non zero floor. run b - exponential, it decays continuously toward zero with no floor."
- **Verdict:** **PASS** — confidence `hunch`, 0 hints, `pow: none` (grade-audit agreed).
- **Why:** both discriminators were read off the curve instead of the schedule names — cosine ends at a non-zero floor, exponential decays continuously toward zero with no floor. The 2026-09-10 name-pattern-matching slip did not recur.

## Q3 — error-detect + perturbation PoW (cross-session item: cosine to `eta_end = 0`, flat loss at step 40k/50k, live gradients)

- **Learner answer (verbatim):** "no it doesnt. the fix is to use a non zero floor."
- **Verdict:** **FAIL** — confidence `hunch`, 0 hints, miss_class `structural`, `pow: perturbation` (grade-audit agreed).
- **Why:** the verdict and the fix are both right (a non-zero `eta_min` floor), but the *what is happening* half was skipped: the per-step update `eta × gradient` collapses to 0, so the weights freeze while the gradients are alive. The held sentence predicts merely slower learning; the run shows none.

## Battery / evidence

- The `perturbation` PoW is recorded together with the Q3 `fail`: the clock that exposes the eta→0 freeze was the mechanism half and it did not appear.
- No `just_tell_me` reveal occurred, and no MCQ key existed (MCQ-free session) — nothing to grade mechanically.
- No `sure` confidence was paired with a fail on this concept (both items `hunch`), so no false-confidence flag.

## Recorded state

- **Attempts.json:** two attempts dated 2026-11-08, in envelope order — `pass` (`discriminative`, `hunch`, hints 0), then `fail` (`error-detect`, `hunch`, hints 0). Net: `interval_index` 2 → 3 → **2**; `consecutive_correct` 0 → 1 → 0; `consecutive_wrong` 0 → 1; `last_reviewed` 2026-10-22 → **2026-11-08**; `next_review` 2026-11-05 → **2026-11-22** (concept ladder, +14d at index 2); mastery **0.45** advisory.
- **Feynman:** the envelope carried `feynman: none` for both items even though this is a `concept` row — the stored flag was left as it is (`—`) and the P1.1 gap is surfaced in the session note.
- **Mistakes ledger:** **one new row** dated 2026-11-08, for the Q3 fail — `structural` / `[miss: structural]` / `active` / retries 0 / next retry 2026-11-22. This item supplied no `targets`, so there is no `[targets: …]` prefix. **No row for the Q1 pass.** The thread's pre-existing rows (2026-09-10 ×2, 2026-10-22) were left untouched — their status, retries and Next Retry were not rewritten by this session.
- **Active Concepts:** row synced — `last_reviewed` → **2026-11-08**; `next_review` → **2026-11-22**; `Last Q Type` definitional → **error-detect**; mastery 0.45 advisory.
- **Advisory mastery:** **0.45** (not blocking).

## Carry-forward

The exact-zero consequence, second consecutive structural fail on this thread (2026-10-22 perturbation PoW was the first): with `eta_min = 0`, `cos(π) = −1` gives `eta_T = 0` exactly, so `eta × gradient = 0` and parameter updates **cease** while gradients are alive. "Slower" is the wrong prediction; "freeze" is the right one, and the floor is what prevents it.
