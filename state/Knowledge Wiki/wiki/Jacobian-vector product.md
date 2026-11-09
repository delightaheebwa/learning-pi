<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Jacobian-vector product

A Jacobian-vector product, or JVP, is the product \(J_f(x) r\): the Jacobian of \(f\) at \(x\) applied to a direction vector \(r\).

## Why it matters

- It gives the effect of one chosen input direction without forming the full Jacobian.
- It is the quantity computed by forward-mode automatic differentiation.
- It is practical when the input dimension is large but you only need a few directions.

## Connection to directional derivatives

- A JVP is the same thing as a directional derivative written in matrix form.
- If \(r\) is a coordinate basis vector, the JVP reduces to a partial derivative.

## Related pages

- [[Directional derivative]]
- [[Jacobian matrix]]
- [[Automatic differentiation]]

## Sources

- https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant
- https://jax.readthedocs.io/en/latest/automatic-differentiation.html
