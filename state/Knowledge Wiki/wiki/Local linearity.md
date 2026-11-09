<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Local linearity

A smooth multivariable function looks linear if you zoom in close enough around a point. The matrix that captures that local linear behavior is the [[Jacobian matrix]].

## The core idea

For a small input change \(\Delta \mathbf{x}\), we have the approximation

- \(f(\mathbf{x} + \Delta \mathbf{x}) \approx f(\mathbf{x}) + J_f(\mathbf{x})\,\Delta \mathbf{x}\)

So the curved map is replaced, near one point, by a constant linear map.

## Why this matters

This explains why tiny x- and y-direction steps in the input space become output vectors with two components.

It is the multivariable version of a tangent line: instead of one best-fit line, you get one best-fit linear transformation.

## Example

For

- \(f(x,y) = (x + \sin(y),\; y + \sin(x))\)

the Jacobian at \((-2,1)\) is

- \(\begin{bmatrix} 1 & \cos(1) \\ \cos(-2) & 1 \end{bmatrix}\)

That matrix gives the local grid-like picture shown in the earlier screenshots.

## Related pages

- [[Jacobian matrix]]

## Sources

- https://en.wikipedia.org/wiki/Linearization
- https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant
