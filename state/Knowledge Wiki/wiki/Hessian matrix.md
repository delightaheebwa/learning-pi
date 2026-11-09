<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Hessian_matrix | verified-by=fact-check-agent | date=2026-10-26 -->

# Hessian matrix

The Hessian matrix is the matrix of second-order partial derivatives of a scalar-valued function.

If (f: \\mathbb{R}^n \\to \\mathbb{R}), then the Hessian is an (n \\times n) matrix whose ((i,j))-th entry is

- (\\frac{\\partial^2 f}{\\partial x_i \\partial x_j})

## Symmetry

If (f) is twice continuously differentiable, then the Hessian is symmetric by Clairaut's theorem:

- (\\frac{\\partial^2 f}{\\partial x_i \\partial x_j} = \\frac{\\partial^2 f}{\\partial x_j \\partial x_i})

The key condition is continuity of the mixed second partials, not just the existence of second derivatives.

## Taylor-series view

In the [[Multivariate Taylor series]], the Hessian is the second-order term:

- (T_2(x) = f(x_0) + \\nabla f(x_0)(x-x_0) + \\tfrac{1}{2}(x-x_0)^\\top H(x_0)(x-x_0))

So the Hessian is what turns the linear approximation into a local quadratic bowl.

## What it tells you

The gradient tells you which way to move to decrease the function fastest. The Hessian tells you how the gradient itself changes locally, which is the curvature information.

Building on [[Directional derivative]] and [[Jacobian matrix]], the Hessian is the second-order analogue: instead of describing local linear change, it describes local curvature.

## Why it matters for optimization

The Hessian can be used to scale updates differently in different directions. That is the idea behind Newton's method:

- (x \\leftarrow x - H^{-1} \\nabla f(x))

This makes the step size adaptive to curvature: larger steps in flatter directions and smaller steps in sharper directions.

## Why full Hessians are hard

For (n) parameters, the Hessian has (n^2) entries.

- Memory: (O(n^2))
- Inversion: (O(n^3))

That becomes infeasible for large models.

## Practical approximations

Common workarounds include:

- Hessian-vector products (HVPs)
- Quasi-Newton methods like L-BFGS
- Diagonal or low-rank approximations

An HVP gives curvature along a chosen direction without explicitly forming the full matrix.

## Related pages

- [[Jacobian matrix]]
- [[Directional derivative]]
- [[Gradient descent]]
- [[Automatic differentiation]]
- [[Backpropagation]]

## Sources
- Wikipedia, "Hessian matrix": https://en.wikipedia.org/wiki/Hessian_matrix
- DataCamp, "Hessian matrix": https://www.datacamp.com/tutorial/hessian-matrix