<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant | verified-by=fact-check-agent | date=2026-10-26 -->

# Jacobian matrix

The Jacobian matrix is the matrix of all first-order partial derivatives of a multivariable function.

If \(f: \mathbb{R}^n \to \mathbb{R}^m\), then the Jacobian is an \(m \times n\) matrix. Entry \((i,j)\) is

- \(\frac{\partial f_i}{\partial x_j}\)

## What the entries mean

- Each **column** tells how the output changes when one input coordinate changes a little.
- Each **row** tells how one output component responds to the input variables.

So the Jacobian packages all the local directional sensitivities into one matrix.

## Local interpretation

At a specific point, the Jacobian is the best linear approximation to the function near that point. Building on that idea, a tiny input step gets mapped to an output step by the matrix, which is why the transformation looks linear when you zoom in.

## Example

For

- \(f(x,y) = (x + \sin(y),\; y + \sin(x))\)

the Jacobian is

- \(J_f(x,y) = \begin{bmatrix} 1 & \cos(y) \\ \cos(x) & 1 \end{bmatrix}\)

At \((-2,1)\), this becomes

- \(J_f(-2,1) = \begin{bmatrix} 1 & \cos(1) \\ \cos(-2) & 1 \end{bmatrix}\)

That is the matrix shown in the earlier screenshots.

## Related pages

- [[Local linearity]]
- [[Jacobian determinant]]

## Sources
- Wikipedia, "Jacobian matrix and determinant": https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant
- Khan Academy, "The Jacobian": https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives/jacobian/v/the-jacobian-determinant
