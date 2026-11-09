<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Gradient_descent ; https://en.wikipedia.org/wiki/Rosenbrock_function | verified-by=fact-check-agent | date=2026-10-26 -->

# Gradient descent

Gradient descent is a first-order optimization method that updates parameters by moving in the direction of steepest decrease predicted by the local linear model.

For a smooth scalar function \(f: \mathbb{R}^n \to \mathbb{R}\), the first-order Taylor approximation around \(x\) is

- \(f(x + \delta) \approx f(x) + \nabla f(x)^\top \delta\)

If you ask for the direction \(\delta\) that gives the largest decrease among small steps of fixed size, the answer points opposite the gradient:

- \(\delta \propto -\nabla f(x)\)

So the key idea is:

- the gradient points uphill
- the negative gradient points downhill fastest in the local linear approximation

## Why it matters

- It uses only first-order information.
- It ignores curvature, so it is cheaper than Newton-style methods.
- It is the simplest default method for many smooth optimization problems.

## Related pages

- [[Multivariate Taylor series]]
- [[Hessian matrix]]
- [[Local linearity]]
- [[Directional derivative]]

## The update rule (Rohit P1 L08)

- \(w \leftarrow w - \eta\,\nabla L(w)\) — one line. Compute the gradient over every weight, move opposite it, scale by the [[Learning Rate]].
- **Two distinct failure modes:** zigzag (narrow curved valley, gradient points across the walls — fixed by [[Momentum (SGD with Momentum)]]) vs overshoot (learning rate too large, diverges/bounces).

## Batch vs stochastic vs mini-batch

| Variant | Batch size | Gradient | Note |
|---------|-----------|----------|------|
| Batch GD | Entire dataset | Exact, slow | Stable but slow |
| SGD | 1 sample | Very noisy, fast | Noise escapes shallow minima/saddles |
| Mini-batch | 32–256 | Good estimate | What everyone actually uses |

## Rosenbrock benchmark

\(f(x,y) = (1-x)^2 + 100\,(y-x^2)^2\) — global minimum at (1,1) inside a narrow curved valley. Easy to find the valley, hard to follow it. The canonical test for comparing GD vs momentum vs Adam.

## Related pages

- [[Learning Rate]]
- [[Momentum (SGD with Momentum)]]
- [[Optimizers (SGD, Adam, AdamW)]]

## Sources (P1 L08 addition)

- Rohit P1 L08 — Optimization, 2026-09-07
- Wikipedia, "Gradient descent": https://en.wikipedia.org/wiki/Gradient_descent
- Rosenbrock function: https://en.wikipedia.org/wiki/Rosenbrock_function


## Three-optimizer race on Rosenbrock (CP3, 2026-09-08)

Three optimizers (vanilla GD, SGD+momentum, Adam) raced from \((-1, 1)\) on the Rosenbrock function:\n
- **Vanilla GD** never converged after 20,000 steps (final loss 5.7e-05) — trapped in zigzag oscillation.
- **SGD with momentum** converged first (~2941 steps, loss 2.2e-29) — momentum's selective accumulation cured the zigzag.
- **Adam** converged second (~6156 steps, loss 4.6e-13) — correct and stable, but slower because the problem does not need per-weight adaptivity.

Takeaway: on a clean two-dimensional deterministic benchmark, vanilla GD's zigzag is the critical failure; momentum's velocity accumulation cures it fastest.


## Learning rate failure modes (handwritten notes, 2026-09-08)

There is no formula for the right η — it must be tuned empirically.

- **Too big:** step overshoots the minimum or bounces off the valley walls (divergence / oscillation).
- **Too small:** convergence is painfully slow or effectively freezes.

Vanilla GD's characteristic failure in a narrow curved valley: it repeatedly step-oscillates side to side across the valley walls, making almost no net progress along the trough toward the minimum. Every step mostly cancels out the previous one's perpendicular motion — it is crawling. This is exactly the geometry that momentum and Adam were designed to fix.
