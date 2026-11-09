# Session — Mixed Practice — 2026-05-19

## Session Info

- **Date:** 2026-05-19
- **Topic:** Mixed Practice (interleaved retrieval)
- **Prerequisites Reviewed:** None — this is a transfer-focused session
- **New Concepts Introduced:** None

---

## What We Covered

Mixed practice session drawing from the 5 active mastered math concepts:

1. **Automatic differentiation** — performance characteristics
2. **Derivative** — conceptual definition
3. **Difference quotient** — secant approximation
4. **Taylor series** — quadratic approximation in optimization
5. **Maclaurin series** — special case identification

---

## Demonstration of Understanding

| Concept | You were asked | Result | Notes |
| --- | --- | --- | --- |
| Derivative | What does the derivative measure, and what does it mean for it to be zero at a point? | Pass | Instantaneous rate of change; zero derivative means the tangent line is horizontal — the function is flat at that point (critical point: max, min, or saddle). |
| Difference quotient | Without computing anything: if you shrink h in the difference quotient, what happens geometrically? | Pass | The secant line connecting (x, f(x)) and (x+h, f(x+h)) approaches the tangent line at x — the average rate of change approaches the instantaneous rate. |
| Taylor series | A loss function L(θ) near a minimum θ* can be approximated by L(θ*) + ½(θ-θ*)ᵀH(θ-θ*). Why is there no linear term? | Pass with help | At a minimum, the gradient ∇L(θ*) = 0, so the first-order term vanishes. The quadratic term captures the curvature via the Hessian H. |
| Maclaurin series | If I give you the series 1 + x + x²/2! + x³/3! + …, what function is this, and how do you know? | Pass | This is eˣ — the Maclaurin series of eˣ because all derivatives of eˣ at 0 equal 1, so every coefficient is 1/k!. |
| Automatic differentiation | You're training a GAN with one generator and one discriminator. Which AD mode is more efficient for the generator's update step, and why? | Pass | Reverse mode — the generator has many parameters (weights) and produces a scalar loss. Reverse mode computes all parameter gradients in one backward pass. Forward mode would need one forward pass per parameter. |

---

## Final Concept Statuses

| Concept | Status | Next Review |
| --- | --- | --- |
| Derivative | mastered | 2026-06-16 (+30 days) |
| Difference quotient | mastered | 2026-06-16 (+30 days) |
| Taylor series | mastered | 2026-06-16 (+30 days) |
| Maclaurin series | mastered | 2026-06-16 (+30 days) |
| Automatic differentiation | mastered | 2026-06-16 (+30 days) |

---

## Gaps & Misconceptions

- [ ] Taylor/Hessian connection: remembered that gradient is zero at minimum but needed a prompt to connect it directly. The reasoning was correct but not yet automatic.
- [ ] GAN application for AD: reasoning was solid (many params, scalar loss → reverse mode wins) but took a moment to map the abstract rule to the concrete scenario.

---

## Next Steps

- [ ] Next mixed practice: Session #20 (current counter at 18 after this session)
- [ ] Target next mixed practice concepts: Partial differentiation, Gradient, Backpropagation, Jacobian-vector product, Hessian matrix
- [ ] Open question to resolve: Connect Hessian to Newton's method with a concrete worked example
