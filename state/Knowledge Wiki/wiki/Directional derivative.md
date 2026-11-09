<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Directional derivative

The directional derivative measures how a function changes at a point when you move in a chosen direction instead of only along a coordinate axis.

For \(f: \mathbb{R}^n \to \mathbb{R}^m\), the directional derivative at \(x\) in direction \(r\) is

- \(J_f(x) r\)

## Why it matters

- A partial derivative is just a directional derivative along a coordinate axis.
- Directional derivatives let you ask how the output changes along any direction in input space.
- In forward-mode automatic differentiation, seeding the tangent with \(r\) computes this quantity directly.

## Sources

- Wikipedia — Directional derivative: https://en.wikipedia.org/wiki/Directional_derivative
- Wikipedia — Jacobian matrix and determinant: https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant

## Related pages

- [[Jacobian matrix]]
- [[Jacobian-vector product]]
- [[Automatic differentiation]]
