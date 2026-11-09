# Review — Learning Rate — 2026-09-23

- **Track/Source:** aiefs — Rohit P1 L08 + handwritten notes 2026-09-08 (Python)
- **Type:** concept · Q type: discriminative
- **Why this slot:** due review (next_review 2026-09-22)
- **Question:** One line: training loss spikes and oscillates instead of descending — learning rate too high or too low? And which symptom would the opposite choice show?
- **Expected:** Too high → overshoot: oscillate/spike/diverge. Too low → slow crawl.
- **Learner answer:** "learning rate is too high. the opposite (learning rate too low) would show that loss decreases very slowly."
- **Verdict:** ✅ pass (grade-audit agreed) — both halves clean, failure modes not conflated.
- **Attempts.json:** mastery 0.80, interval_index 3 (2 consecutive passes), next_review 2026-10-23
- **Note:** pairs with the open GD Failure Modes zigzag row (next retry 2026-09-24) — the LR symptoms are solid; the *direction* problem (zigzag) remains the open half.
