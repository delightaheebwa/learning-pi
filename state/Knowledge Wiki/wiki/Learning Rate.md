<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Learning Rate

The scalar that controls how far each gradient-descent step moves: \(w \leftarrow w - \eta\,\nabla L(w)\). It is the single most important hyperparameter in optimization.

## The tradeoff

- **Too large** — the update overshoots the valley, bouncing between walls or diverging entirely.
- **Too small** — you crawl toward the answer over thousands of unnecessary steps.
- **No formula exists** — the right value is found by experiment.

## Starting points (Rohit rule of thumb)

| Optimizer | Starting lr |
|-----------|-------------|
| Adam | 0.001 |
| SGD with momentum | 0.01 (momentum=0.9) |

## Schedules

A fixed lr is a compromise — large steps early for fast progress, small steps late for fine-tuning. Common schedules: step decay, exponential decay, cosine annealing, warmup-then-decay (warmup is standard for large models to prevent early instability). See [[Learning-rate Schedules (four types)]] for the full curve-shape reference.

**Timescale insight (2026-09-10):** a decay factor that looks gentle isn't — \(0.999^{1000} \approx 0.368\), so \(0.999\) halves the rate every ~700 steps. Choosing the decay factor is choosing that characteristic timescale.

## Related pages

- [[Gradient descent]]
- [[Momentum (SGD with Momentum)]]
- [[Optimizers (SGD, Adam, AdamW)]]

## Sources

- **Lesson:** Rohit P1 L08 — Optimization (Gradient Descent Family), 2026-09-07
- **Source:** `phases/01-math-foundations/08-optimization/docs/en.md`
- https://en.wikipedia.org/wiki/Learning_rate

## lr and optimizer choice (CP3, 2026-09-08)

The "right" learning rate depends on the optimizer — Adam defaults to 0.001, SGD+momentum to 0.01. In the Rosenbrock race, Adam's lr=0.001 was effective without tuning; vanilla GD at lr=0.0005 never converged (wrong failure mode — zigzag, not overshoot). The optimizer choice and the lr choice are coupled, not independent.
