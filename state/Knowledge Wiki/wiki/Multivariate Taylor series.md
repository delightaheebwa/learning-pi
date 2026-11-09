<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Multivariate Taylor series

The multivariate Taylor series approximates a smooth scalar function near a point by combining its value, gradient, Hessian, and higher-order derivative tensors.

If \(f: \mathbb{R}^n \to \mathbb{R}\) and \(x_0\) is the expansion point, define

- \(\delta = x - x_0\)

Then the compact tensor form is

- \(f(x) = \sum_{k=0}^{\infty} \frac{1}{k!} D_x^k f(x_0)\,\delta^k\)

Here:

- \(D_x^k f(x_0)\) is the \(k\)-th derivative tensor of \(f\) at \(x_0\)
- \(\delta^k = \delta \otimes \cdots \otimes \delta\) is the \(k\)-fold outer product of the displacement vector
- the tensor term is contracted over all matching indices to produce a scalar

## The first few terms

- \(k=0\): \(f(x_0)\)
- \(k=1\): \(\nabla f(x_0)\,\delta\)
- \(k=2\): \(\frac{1}{2}\,\delta^\top H(x_0)\delta\)
- \(k=3\): \(\frac{1}{6}\,D_x^3 f(x_0)\,\delta^3\)

In index notation, the general contraction is

- \(D_x^k f(x_0)\,\delta^k = \sum_{i_1=1}^{n} \cdots \sum_{i_k=1}^{n} D_x^k f(x_0)[i_1,\dots,i_k] \; \delta[i_1]\cdots\delta[i_k]\)

## Geometric meaning

- The gradient term is the local slope or tangent-plane approximation.
- The Hessian term is the local curvature along the direction \(\delta\).
- The cubic term describes how that curvature itself starts to change as you move away from \(x_0\).

A useful 1-D view is to follow the line

- \(g(t) = f(x_0 + t\delta)\)

Then the Taylor coefficients are just derivatives of \(g\) at \(t=0\):

- \(g'(0) = \nabla f(x_0)\,\delta\)
- \(g''(0) = \delta^\top H(x_0)\delta\)
- \(g^{(3)}(0) = D_x^3 f(x_0)\,\delta^3\)

## Truncation

The degree-\(n\) Taylor polynomial is the truncation

- \(T_n(x) = \sum_{k=0}^{n} \frac{1}{k!} D_x^k f(x_0)\,\delta^k\)

Two especially important cases are:

- \(T_1\): a linear approximation, which keeps the value and gradient only
- \(T_2\): a quadratic approximation, which also keeps curvature through the Hessian

This is why gradient descent behaves like it is following a local plane, while Newton's method uses the Hessian to fit a local quadratic bowl.

## Related pages

- [[Directional derivative]]
- [[Gradient descent]]
- [[Hessian matrix]]
- [[Local linearity]]

## Sources

- Wikipedia — Taylor series (multivariate case): https://en.wikipedia.org/wiki/Taylor_series
- Math Insight — Taylor's theorem for multivariable functions: https://mathinsight.org/taylors_theorem_multivariable_introduction
