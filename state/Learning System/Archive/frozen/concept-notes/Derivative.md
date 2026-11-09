# Derivative

> **Status:** mastered | **Domain:** Calculus Foundations
> **Prerequisites:** Difference quotient, limit intuition

## Definition

The derivative \( f'(x) \) of a function \( f \) at a point \( x \) is the **instantaneous rate of change**:

\[
f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}
\]

Geometrically, it is the slope of the **tangent line** to the graph at \( x \).

## Why It Matters

The derivative is the fundamental concept behind all of optimization. Gradient descent, Newton's method, backpropagation — every ML training algorithm ultimately relies on the derivative. When you compute \( \frac{\partial L}{\partial w} \) for a weight update, you're computing a derivative.

## Key Insights

- **Zero derivative** = the tangent line is horizontal = critical point (max, min, or saddle)
- **Positive derivative** = function increasing = moving right increases output
- **Negative derivative** = function decreasing = moving right decreases output

## Common Mistakes

- Confusing the derivative with the difference quotient — the derivative is the *limit*, not the ratio
- Forgetting the limit exists only when left and right limits agree
- Treating the derivative as just "the slope formula" without understanding it as a limit

## Related Concepts

- [[Difference quotient]] — the pre-limit form
- [[Partial differentiation]] — extends to functions of multiple variables
- [[Gradient]] — vector of partial derivatives
- [[Automatic differentiation]] — computes derivatives of arbitrary programs
