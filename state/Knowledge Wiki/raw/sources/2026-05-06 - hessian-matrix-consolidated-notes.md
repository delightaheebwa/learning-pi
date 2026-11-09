# Source: Hessian Matrix — Consolidated Notes

## Raw notes

### Definition & Structure

The Hessian matrix is a collection of second-order partial derivatives of a scalar-valued function \(f: \mathbb{R}^n \to \mathbb{R}\). Formally, its \((i,j)\)-th entry is

- \(\frac{\partial^2 f}{\partial x_i \partial x_j}\)

so the Hessian is an \(n \times n\) matrix.

### Symmetry

If \(f\) is twice continuously differentiable, then by Clairaut's theorem, the Hessian is symmetric. That is,

- \(\frac{\partial^2 f}{\partial x_i \partial x_j} = \frac{\partial^2 f}{\partial x_j \partial x_i}\)

It is the continuity of the second-order partial derivatives that guarantees this symmetry, not mere twice-differentiability alone.

### Curvature & Optimization Role

The Hessian encodes the local curvature of the loss surface around a point. The gradient alone tells you the direction of steepest descent, but uses a hand-tuned, global learning rate \(\eta\) that applies the same step size to every direction. Adding Hessian (or approximate Hessian) information lets you scale the gradient differently per direction based on curvature — taking larger steps where the surface is flat and smaller steps where it is sharp. This is the essence of Newton's method:

- \(x \leftarrow x - H^{-1} \nabla f(x)\)

which gives geometry-aware, adaptive steps toward a minimum.

### Scalability Problem

Storing the full Hessian requires \(O(n^2)\) memory, and inverting it costs \(O(n^3)\). For a model with \(n = 10^6\) parameters, the Hessian alone would require roughly terabytes of storage — computationally infeasible at deep learning scales.

### Practical Workarounds

To avoid forming the full Hessian, practical methods use:

- **Hessian-vector products (HVPs):** Computing \(Hv\) for a specific direction \(v\) gives the directional curvature — how the gradient changes if you move in direction \(v\). This costs roughly \(O(n)\) in time and memory, comparable to a forward/backward pass, and avoids the \(O(n^2)\) storage of the full matrix.
- **Quasi-Newton methods (e.g., L-BFGS):** Maintain a low-rank approximation of the Hessian using only a small history of gradient vectors.
- **Diagonal or low-rank approximations:** Used in large-scale deep learning to capture curvature structure at a fraction of the cost.

## Extracted notes

- The Hessian is the matrix of second-order partial derivatives of a scalar function.
- For sufficiently smooth functions, the Hessian is symmetric.
- Symmetry comes from continuity of mixed partial derivatives.
- The Hessian describes local curvature and helps adapt step sizes by direction.
- Newton's method uses the inverse Hessian to make curvature-aware updates.
- Full Hessians are too expensive to store or invert for large neural networks.
- Practical alternatives include HVPs, quasi-Newton methods, and diagonal or low-rank approximations.
