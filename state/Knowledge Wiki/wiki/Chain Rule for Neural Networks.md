<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Chain Rule for Neural Networks

> **Type:** procedure · **Track:** AIEFS · **Source:** Rohit P1 L05 + CS231n optimization-2 · **Lang:** Python
> **Insight:** Gradients multiply across layers (not add) because intermediate variables are dependent.

## Definition

The chain rule states: if y = f(g(x)), then dy/dx = f'(g(x)) · g'(x).

For a multi-layer neural network with layers a1 → a2 → a3 → loss:

```
∂Loss/∂w1 = ∂Loss/∂a3 × ∂a3/∂a2 × ∂a2/∂a1 × ∂a1/∂w1
```

Each factor is a **local derivative** — how much the next variable changes given this one.

## Why Multiplication, Not Addition

Variables in a neural network are **dependent** (chained): a2 depends on a1, which depends on w1. The effects compound multiplicatively. Addition would only be correct if the variables were independent.

**Analogy (soccer):** Pass the ball through Player A (×5) then Player B (×3). Total displacement = 5 × 3 = 15, not 5 + 3 = 8. Each player scales what they receive.

## Role in Backpropagation

Backpropagation IS the chain rule applied layer by layer, from loss backward to each weight.

## Common Mistake

Using **addition** (+) instead of **multiplication** (×) when computing gradients through layers.

## Related

- [[Backpropagation]]
- [[Reverse-Mode Autodiff & Backprop]]
- [[Chain Rule Decomposition]]

## Sources

- Backpropagation: https://en.wikipedia.org/wiki/Backpropagation
- Chain rule: https://en.wikipedia.org/wiki/Chain_rule
- CS231n optimization: https://cs231n.github.io/optimization-2/

## Retrieval log (2026-09-26)

- Review FAIL (first graded retrieval of the two-path chain rule since L05): df/dx for f = (x+y)·x² at (2,3) answered as the fused product 2x(x+y)(x²+1) — which evaluates to 100 — instead of the two-path sum (x+y)(2x) + x² = 20 + 4 = **24** (closed form 3x² + 2xy). Repair delivered same session: x is one pipe feeding f through two parallel valves (u = x+y and z = x²); one nudge of x changes f through both slots simultaneously and the changes ADD (the additive form IS the product rule g′h + gh′); the multiplicative fusion also fails the plug-in test (100 ≠ 24). Nudge-y contrast seeded (y reaches f only through u: df/dy = x² = 4, single path). New Mistakes row (application); retry 2026-10-03.
