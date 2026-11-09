# Review — Momentum (SGD with Momentum) — 2026-09-30

- **Track/Source:** aiefs — Rohit P1 L08 + Goh Distill + handwritten notes 2026-09-08 (Python)
- **Type:** procedure · **Q type:** definitional (free recall)
- **Why this slot:** due review (Attempts.json next_review 2026-09-30) — no ledger row; this concept has never been graded wrong.
- **Question:** Definitional free recall — what does momentum add to plain SGD, and which failure of plain SGD does it address?
- **Learner answer:** "it enables the step to have forward motion but plain sgd can get stuck in oscillations since it is relying only on mini batch noise."
- **Verdict:** PASS — grade-audit agreed (batch verdict agrees: true, item 3). Why: both halves are present — the accumulated velocity carries a step forward along the consistent direction, and the oscillation story is right (plain SGD steps on the current mini-batch gradient alone, so it flips direction across a narrow valley). Wording loose: "relying only on mini batch noise" is the learner's shorthand for "no memory of past gradients".
- **Attempts.json:** mastery 1.00, interval_index 2 (procedure schedule [3,7,14]d, capped at index 2), next_review 2026-10-14, Feynman: — (procedure type — no Feynman flag).
- **Mistakes ledger:** none — no row was opened (and none is due) for this concept.
- **Carry-forward:** Last Q Type is now `definitional`, so the next queue entry is a discriminative item; the two-step update (v ← βv + g; w ← w − ηv) remains the thing worth probing next.
