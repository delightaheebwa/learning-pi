<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Total differential

The total differential is the linearized change of a multivariable scalar function.

For a function \(F(x,y)\), it is

- \(dF = F_x\,dx + F_y\,dy\)

This is the first-order approximation to how the output changes when the inputs change a little.

## Level sets

If you move along a level set where \(F(x,y)=c\), then the value of \(F\) stays constant. That means

- \(dF=0\)

This is why the differential is useful for curves defined implicitly, such as circles and other contours.

## Example

For

- \(S(x,y)=x^2+y^2\)

we get

- \(dS = 2x\,dx + 2y\,dy\)

If you stay on the circle \(S=25\), then \(dS=0\), so the input changes must satisfy the same first-order balance.

## Connection to Jacobians

For a scalar function, the total differential is the Jacobian row applied to the input displacement vector. Building on that, the Jacobian matrix generalizes the same idea to vector-valued functions.

## Sources

- Wikipedia — Differential of a function: https://en.wikipedia.org/wiki/Differential_of_a_function

## Related pages

- [[Implicit differentiation]]
- [[Jacobian matrix]]
- [[Local linearity]]
