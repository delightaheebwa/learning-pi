<!-- provenance: status=verified | source=https://github.com/karpathy/micrograd ; https://timvieira.github.io/blog/how-to-test-gradient-implementations/ | verified-by=fact-check-agent | date=2026-10-26 -->

# Gradient Checking

Comparing autodiff gradients against numerical finite-difference approximations to verify the backward pass is correct. The core method: compute the central difference f'(x) ≈ (f(x+h) - f(x-h))/(2h) with h ≈ 10⁻⁶, giving O(h²) accuracy. Compare against autodiff gradient; if the difference exceeds a tolerance (~10⁻⁵), there's a bug in a backward rule.

**When to use:** every time you implement a new operation's backward pass. Every major framework (PyTorch, JAX, TensorFlow) has gradient checking in its test suite.

**Key insight:** gradient checking catches silent bugs — mismatches where autodiff produces wrong gradients that would corrupt training without any visible error.

## Source
- Lesson: [Teach/lessons/0005-gradient-checking-and-micrograd.html](teach/lessons/0005-gradient-checking-and-micrograd.html)
- Date learned: 2026-07-10
- Karpathy micrograd: https://github.com/karpathy/micrograd
- Numerical gradient checks: https://timvieira.github.io/blog/how-to-test-gradient-implementations/

## Connections
- Prerequisites: [[Local Autograd Derivative Rules]], [[Numerical vs Analytical Derivatives]]
- Related: [[Chain Rule Decomposition]], [[Topological Sort for Backprop]]
