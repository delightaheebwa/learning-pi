<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Neural Network Training Loop

The complete cycle that every deep learning framework implements: (1) **Forward pass** — compute predictions and loss; (2) **Backward pass** — loss.backward() computes gradients for all parameters via autodiff; (3) **Parameter update** — w -= lr × w.grad (gradient descent step); (4) **Zero gradients** — reset all .grad values to 0 before the next iteration.

In equation form: θ ← θ - η·∇θL(θ), repeated thousands of times over batches of data. The backward pass and update step are what the autograd engine enables.

**Key insight:** this loop IS training. Everything else — architectures, loss functions, optimizers — are variations built on this foundation. In micrograd, the full loop is ~10 lines of pure Python.

## Source
- Lesson: [Teach/lessons/0005-gradient-checking-and-micrograd.html](teach/lessons/0005-gradient-checking-and-micrograd.html)
- Date learned: 2026-07-10

## Connections
- Prerequisites: [[Gradient Descent from Scratch]], [[Topological Sort for Backprop]], [[Value Class Architecture]]
- Related: [[Gradient Accumulation (+=)]], [[Two-Pass Autodiff Algorithm]], [[Parameter Update Rule]]

## Sources

- PyTorch docs — Autograd: https://pytorch.org/docs/stable/autograd.html
- Karpathy micrograd: https://github.com/karpathy/micrograd
