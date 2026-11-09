<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Momentum (SGD with Momentum)

Momentum accumulates past gradients into a velocity term instead of stepping on the current gradient alone:

- \(v \leftarrow \beta\,v + g\)
- \(w \leftarrow w - \eta\,v\)

with \(\beta\) typically 0.9 (keep 90% of last step's velocity, add the new gradient).

## Why it works (beyond the ball analogy)

The "heavy ball rolling downhill" picture is a fine intuition but an oversimplified cartoon (Goh, Distill 2017). The deeper mechanism: in a narrow valley, the cross-valley gradient oscillates in sign — so opposite-sign contributions **cancel** in the velocity sum — while the along-valley gradient is small but consistent, so it **accumulates**. Momentum is a selective accumulator: it keeps what is consistent and averages away what zigzags.

Geometrically, this rescales the effective step size per eigenvector direction of the Hessian, equalizing convergence rates across directions of different curvature.

## Notes

- Higher \(\beta\) = smoother paths but slower response to direction changes.
- The first step from zero velocity is identical to plain GD — momentum's advantage compounds over steps.
- Different lineage from adaptive methods (Adam tracks squared gradients too; see [[Optimizers (SGD, Adam, AdamW)]]).

## Related pages

- [[Gradient descent]]
- [[Learning Rate]]
- [[Optimizers (SGD, Adam, AdamW)]]
- [[Hessian matrix]]

## Sources

- **Lesson:** Rohit P1 L08 — Optimization (Gradient Descent Family), 2026-09-07
- **Source:** `phases/01-math-foundations/08-optimization/docs/en.md`
- Wikipedia — Stochastic gradient descent (momentum): https://en.wikipedia.org/wiki/Stochastic_gradient_descent#Momentum
- **Enrichment:** G. Goh, "Why Momentum Really Works" (Distill, 2017) — https://distill.pub/2017/momentum/


## Rosenbrock race result (CP3, 2026-09-08)

On the Rosenbrock function from \((-1,1)\), lr=0.0005, momentum converged first (~2941 steps), beating Adam (~6156 steps). Vanilla GD never converged (zigzag). This shows: in a clean, smooth two-dimensional valley, momentum's velocity accumulation is the most direct cure for oscillation — Adam's per-weight adaptivity adds overhead with no benefit on this structure.

SGD with momentum also tends to generalize better in practice (residual noise avoids sharp minima), a point relevant to later phases.


## Eigenvalue & step-size interpretation (handwritten notes, 2026-09-08)

Momentum rescales your effective step size per direction. Along the valley's long axis (small curvature, small eigenvalue λ), momentum lets you take big steps; across the steep walls (large λ), it keeps steps small. That is why it navigates the Rosenbrock valley — it gives you a **direction-dependent step size** which plain GD cannot do.

Momentum equalizes convergence across directions with different curvature: it balances out the speeds across directions so one high-curvature direction doesn't choke progress in low-curvature directions.
