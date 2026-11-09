<!-- provenance: status=verified | source=https://github.com/karpathy/micrograd ; https://pytorch.org/docs/stable/autograd.html | verified-by=fact-check-agent | date=2026-10-26 -->

# Gradient Accumulation (+=)

When a variable is used in multiple operations, it receives gradient contributions from **each** path through the computational graph. The total gradient is the **sum** of all path contributions — this is the multivariable chain rule.

This is why all backward functions use `+=` instead of `=`:

```python
def _backward():
    self.grad += 1.0 * out.grad    # += NOT =
```

If you use `=`, the last operation to run overwrites all previous contributions. Using `+=` accumulates them correctly.

**Example:** `x = Value(3.0); y = x + x; z = y * x`

x reaches z through two paths:
- Path 1: z = y·x → contribution from x-direct = y = 6
- Path 2: z = y·x → through y = x+x → contribution = x·(∂y/∂x) = 3·2 = 6
- Total: 6 + 6 = 12

This is the single most common bug in autograd engines — and the fix is always `+=`.

## Source
- Lesson: [teach/lessons/0003-value-class-and-operations.html](/home/workspace/teach/lessons/0003-value-class-and-operations.html)
- Date learned: 2026-07-09
- Karpathy micrograd (autograd engine): https://github.com/karpathy/micrograd
- PyTorch autograd mechanics: https://pytorch.org/docs/stable/autograd.html

## Connections
- Prerequisites: Chain Rule Decomposition, Value Class Architecture
- Used in: Every _backward closure in the autograd engine
