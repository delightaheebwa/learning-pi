# Review — PMF vs PDF — 2026-11-04

- **Track/Source:** aiefs — Rohit P1 L06 + CS229 (Python)
- **Type:** concept · **Q type:** `discriminative`
- **Why this slot:** priority-1 due mistake — ledger rows 2026-09-11 and 2026-10-17 both carried next retry 2026-10-24; the row is the longest-running label-inversion thread in the ledger.
- **Question:** the verbatim prompt text was **not carried in the handoff envelope** — recorded as a handoff gap, not reconstructed. The envelope carried the item type, the learner's verbatim answer and the graded gap quoted under *Why*.
- **Learner answer (verbatim):** "the first claim is the one which is wrong but the second is correct. 0.4 is measuring probability per metre. to get near 1.70 i would simply get the density in the range near 1.70."
- **Verdict:** **FAIL — confidence `hunch`, 0 hints, miss_class `structural` (grade-audit agreed).**
- **Why:** claim (ii) was held as **correct**: a density value is not the CDF (F(1.70) is the running integral up to 1.70), so the density reading was again allowed to stand in for an accumulated probability. The per-metre unit reading held; the missing half is the last step — a near-1.70 probability needs the density integrated over a small interval around 1.70, not read off the value. Graded gap, verbatim: "held claim (ii) as correct: density value ≠ CDF (running integral up to 1.70); correct on per-metre unit; near-1.70 needs integrating over a small interval".
- **Attempts.json:** one attempt recorded 2026-11-04 — `fail` (`discriminative`, `hunch`, hints 0). Net state: mastery **0.35** advisory, `interval_index` 1 → **0**, `consecutive_correct` 1 → **0**, `consecutive_wrong` 0 → **1**, `last_reviewed` 2026-10-17 → **2026-11-04**, `next_review` 2026-10-24 → **2026-11-07** (concept ladder, +3d at index 0), Feynman flag `fail` unchanged (no explain-back result carried in the handoff).
- **Mistakes ledger:** **one new row** dated 2026-11-04 — `structural` / `[miss: structural]` / `active` / retries 0 / next retry 2026-11-07. The two pre-existing same-thread rows (2026-09-11 retries 2; 2026-10-17 retries 1) were patched in place — status and retries untouched, Next Retry realigned to 2026-11-07.
- **Active Concepts:** row synced — `last_reviewed` 2026-10-17 → **2026-11-04**; `next_review` 2026-10-24 → **2026-11-07**; `Last Q Type` definitional → **discriminative**; mastery 0.35 advisory noted.
- **Advisory mastery:** **0.35** — Feynman: `fail` (unchanged).
- **Carry-forward:** the CDF reading — F(1.70) as the running integral up to 1.70, and the interval-integration step as the settling operation for a near-1.70 probability.
