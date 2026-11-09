<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Learning-Rate Schedules (Four Types)

A fixed learning rate is a compromise: large steps early for fast progress, small steps late for fine-tuning. A schedule changes \(\eta\) over time to get both. Read every schedule as a curve of \(\eta\) vs training step — they differ on **two axes**: the early phase and the end behavior.

| Schedule | Formula | Start | End behavior |
|---|---|---|---|
| Step decay | \(\eta \leftarrow \eta \cdot \text{factor}\) every \(N\) epochs | \(\eta_0\) | Drops in jumps (staircase) |
| Exponential decay | \(\eta = \eta_0 \cdot \text{decay}^{t}\) | \(\eta_0\) | Keeps shrinking toward **0 — no floor** |
| Cosine annealing | \(\eta = \eta_{\min} + \tfrac{1}{2}(\eta_{\max}-\eta_{\min})(1+\cos(\pi t / T))\) | \(\eta_{\max}\) | Lands on \(\eta_{\min}\) — a nonzero **floor** — and stays |
| Warmup + decay | Linear ramp **up**, then decay | small | Falls to a low rate |

Two discriminators worth memorizing:

- **Only warmup ramps up** — it's the answer whenever the stem mentions early instability (large models blow up if started large).
- **Only cosine has a floor parameter** — at \(t=T\), \(\cos\pi = -1\) kills the second term, leaving exactly \(\eta = \eta_{\min}\), the value you chose. Exponential never settles at any nonzero value.

## The timescale insight

A decay factor that looks gentle isn't: \(0.999^{1000} \approx 0.368\), and \(0.999^{5000} \approx 0.0067\) — under 1% of the starting rate. The factor \(0.999\) halves the rate every ~700 steps (\((1-1/n)^n \to e^{-1}\) with \(n=1000\)). Choosing the decay factor is choosing that characteristic timescale — a tuned hyperparameter, not a freebie.

## Use cases (from handwritten table, 2026-09-09)

- Step decay — simple manual control.
- Exponential decay — smooth reduction.
- Cosine annealing — transformers, modern training.
- Warmup + decay — large models, prevents early instability.

## Why schedules aren't enough (Ruder's critique)

Pre-defined schedules are a blunt instrument (Ruder): (1) the curve is drawn in advance before seeing how training actually unfolds, so it can't adapt to a dataset's characteristics, and (2) one size fits all — every weight gets scaled the same regardless of feature frequency or gradient size. That is exactly the gap per-parameter adaptivity (Adam) fills — schedules complement adaptivity, they don't replace it.

## Related pages

- [[Learning Rate]]
- [[Adam (adaptive moments)]]
- [[Optimizer Selection (Rohit heuristic)]]

## Sources

- **Lesson:** Rohit P1 L08 — Optimization (Gradient Descent Family), 2026-09-10
- **Source:** `phases/01-math-foundations/08-optimization/docs/en.md` + [Ruder's survey](https://ruder.io/optimizing-gradient-descent/)
- https://pytorch.org/docs/stable/optim.html
- https://ruder.io/optimizing-gradient-descent/
