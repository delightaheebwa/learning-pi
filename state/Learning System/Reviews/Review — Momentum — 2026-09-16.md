# Review — Momentum (SGD with Momentum) — 2026-09-16

- Track: aiefs · Type: procedure · Last Q Type: discriminative (was definitional)
- Q: Vanilla GD zigzags across a narrow valley while momentum cruises through. What does the velocity term keep vs cancel, and why?
- A: keeps influence of previous gradients; cancels the cross-valley (zigzag) component to move forward. Legitimate.
- Verdict: pass (grade-audit agreed). Selective accumulator: keeps consistent along-valley, cancels oscillating across-valley.
- mastery 0.80 — Feynman: — · last 2026-09-16 · next 2026-09-30.
