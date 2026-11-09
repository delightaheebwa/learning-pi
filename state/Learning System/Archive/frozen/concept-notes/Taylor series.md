# Taylor Series

> **Status:** mastered | **Domain:** Calculus Foundations
> **Prerequisites:** Derivative, higher-order derivatives

## Definition

A Taylor series expands a function \( f(x) \) into an **infinite polynomial** centered at a point \( a \):

\[
f(x) = \sum_{k=0}^{\infty} \frac{f^{(k)}(a)}{k!} (x - a)^k
\]

Each term adds more local information:
- \( k = 0 \): function value at \( a \)
- \( k = 1 \): slope (first derivative)
- \( k = 2 \): curvature (second derivative)
- ...and so on

## Why It Matters

Taylor series are why we can do polynomial regression, kernel approximations, and local optimization. When a loss function \( L(\theta) \) near a minimum \( \theta^* \) is approximated as:

\[
L(\theta) \approx L(\theta^*) + \frac{1}{2}(\theta - \theta^*)^{\top} H (\theta - \theta^*)
\]

That's a second-order Taylor expansion — the linear term vanishes because the gradient at the minimum is zero, leaving the Hessian to capture local curvature.

## Key Insight

At a minimum, the gradient is zero, so the first-order Taylor term disappears. This is why Newton's method uses the Hessian — it's the first non-zero term capturing how the function curves around the minimum.

## Common Mistakes

- Forgetting the \( k! \) in the denominator
- Not distinguishing Taylor series (centered at any \( a \)) from Maclaurin series (centered at 0)
- "Zero gradient at minimum → only the quadratic term matters" is a Taylor series insight, not a Hessian insight

## Related Concepts

- [[Maclaurin series]] — Taylor series centered at 0
- [[Derivative]] — the first term
- [[Hessian matrix]] — provides the second-order term for multivariate functions
- [[Multivariate Taylor series]] — extends to vector inputs
