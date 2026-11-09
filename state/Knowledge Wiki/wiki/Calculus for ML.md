<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Calculus for Machine Learning

> Derivatives tell you which way is downhill. That is all a neural network needs to learn.

**Source:** [ai-engineering-from-scratch — Phase 1, Lesson 04: Calculus for ML](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/04-calculus-for-ml/docs/en.md)
**Prerequisites:** [[Linear Algebra Intuition]], [[Matrix Operations from Scratch]], [[Matrix Transformations]]
**Time:** ~60 minutes

## Key Insight

A neural network has millions of weights. Each weight is a knob. You need to know which direction to turn every single knob to make the model less wrong. **Calculus gives you that direction** — the derivative tells you exactly how each weight affects the error.

---

## Core Concepts

### Derivative
The derivative f'(x) measures the rate of change: if you nudge x by a tiny amount, how much does y change? Geometrically, it's the slope of the tangent line at a point.

**ML derivatives you'll see constantly:**
| Function | Derivative | Where |
|----------|-----------|-------|
| f(x) = x² | f'(x) = 2x | MSE loss |
| f(x) = wx + b | f'(w) = x, f'(b) = 1 | Linear layer |
| f(x) = eˣ | f'(x) = eˣ | Softmax, attention |
| f(x) = ln(x) | f'(x) = 1/x | Cross-entropy loss |
| σ(x) = 1/(1+e⁻ˣ) | σ'(x) = σ(x)(1-σ(x)) | Sigmoid activation |

### Partial Derivatives & Gradient
For functions with many inputs, a partial derivative holds all variables constant except one. The **gradient** collects every partial derivative into one vector — it points in the direction of **steepest ascent**. To minimize, go in the opposite direction (-gradient).

### Numerical vs Analytical Derivatives
- **Analytical:** Apply calculus rules by hand (exact, fast) — e.g. f'(x²) = 2x
- **Numerical:** Central difference approximation — `(f(x+h) - f(x-h)) / 2h` (works for any function, slower)
- **Automatic differentiation:** Third approach used by PyTorch/TensorFlow — computes exact derivatives mechanically through the computation graph

### Chain Rule & Backpropagation
When functions are composed: dy/dx = f'(g(x)) · g'(x). Neural networks are chains of functions (linear → activation → linear → activation → loss). **Backpropagation is the chain rule applied repeatedly from output to input.** That's the entire algorithm.

### Gradient Descent
The core optimization loop: `w = w - lr · dL/dw` for every weight. Compute the gradient, negate it, take a small step. Repeat millions of times. The learning rate controls step size — too big overshoots, too small crawls.

### Hessian Matrix
The matrix of second-order partial derivatives. Describes **curvature**:
| Hessian property | Meaning |
|-----------------|---------|
| All eigenvalues > 0 | Local minimum |
| All eigenvalues < 0 | Local maximum |
| Mixed eigenvalues | Saddle point |

Newton's method uses the Hessian for better steps (accounts for curvature) but is too expensive for large models (N×N matrix for N parameters).

### Taylor Series for Optimization
Any smooth function can be approximated locally by a polynomial. The order of approximation determines the optimization method:
- **1st order** (linear) → **Gradient descent**
- **2nd order** (quadratic) → **Newton's method**

This is why small learning rates work — they keep the linear approximation accurate.

### Optimizer Tradeoffs
| Method | Cost | Convergence | Used in practice? |
|--------|------|-------------|-------------------|
| Gradient descent | O(N) | Slow (linear) | Sometimes |
| Newton's method | O(N³) | Fast (quadratic) | No (too expensive) |
| L-BFGS | O(N) | Medium | Yes (small models) |
| **Adam** | O(N) | Medium | **Default for deep learning** |
| Natural gradient | O(N²) | Fast | Specialized |

Adam is the default optimizer — it approximates second-order information cheaply by tracking running mean and variance of gradients per parameter.

### Jacobian Matrix
When a function maps Rⁿ → Rᵐ, its derivative is an m×n **Jacobian** matrix containing every partial derivative of every output w.r.t. every input. Gradient flows backward through the transpose of this matrix during backpropagation.

---

## Code Implementations

The full source implements:
1. Numerical derivative from scratch (central difference)
2. Numerical gradient for multi-variable functions
3. Gradient descent in 1D (f(x) = x²) and 2D (f(x,y) = x² + y²)
4. Numerical Hessian computation (saddle vs bowl)
5. Taylor approximation (sin(x) at x₀=0)
6. Full gradient descent training loop for linear regression

**Core pattern (every gradient-based training loop):**
```python
# predict → compute loss → compute gradients → update weights
pred = w * x + b
error = pred - y
loss = mean(error ** 2)
dw = mean(2 * error * x)
db = mean(2 * error)
w -= lr * dw
b -= lr * db
```

---

## Connections
- [[Matrix Transformations]] — prerequisite linear algebra
- [[Linear Algebra Intuition]] — prerequisite for understanding vector operations
- [[Matrix Operations from Scratch]] — matmul, broadcasting used in dense layers

## Open Questions
- None currently

## Source
[Full lesson →](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/04-calculus-for-ml/docs/en.md)

## Sources

- Rohit lesson (calculus for ML): https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/04-calculus-for-ml/docs/en.md
- Automatic differentiation (autograd): https://pytorch.org/docs/stable/autograd.html
- Calculus (derivatives): https://en.wikipedia.org/wiki/Derivative
