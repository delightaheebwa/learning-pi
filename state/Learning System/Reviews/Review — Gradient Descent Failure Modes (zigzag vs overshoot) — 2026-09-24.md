# Review — Gradient Descent Failure Modes (zigzag vs overshoot) — 2026-09-24

- **Track/Source:** aiefs — Rohit P1 L08 + Ruder + handwritten notes (Python)
- **Type:** concept · **Q type:** definitional
- **Why this slot:** due review and retry of the recurring zigzag/overshoot conflation.
- **Question:** Explain why vanilla GD zigzags in a narrow Rosenbrock valley, distinguish overshoot, and name an intervention for each.
- **Learner answer:** "it zigzags because gradient points across the valley. this differs from overshoot in that overshoot just means you bypassed the minima. the intervention for the first is to use adam with momentum leading to forward adaptive step movement rather than movement that goes from wall to wall and for the second i would use a lower learning rate."
- **Verdict:** PASS — grade-audit corrected the claimed fail. The learner identified the cross-valley gradient direction, the overshoot distinction, and valid interventions; the mechanism wording was imprecise but did not invalidate the requested distinction.
- **Attempts.json:** mastery 0.69, interval_index 1, next_review 2026-10-02, Feynman: pass
- **Mistakes ledger:** the active zigzag row has one post-fail correct recall and remains `review`, retries 1, next retry 2026-10-02; a second consecutive correct recall is still required for graduation.
- **Calibration:** retain the distinction that momentum addresses directional zigzag, while lowering the learning rate addresses overshoot.
