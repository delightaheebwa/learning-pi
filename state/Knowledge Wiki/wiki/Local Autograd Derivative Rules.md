<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Local Autograd Derivative Rules

Each operation in an autograd engine only needs to know its own local derivative rule. The graph handles composing them via the chain rule.

| Operation | Forward | ∂out/∂a | ∂out/∂b |
|-----------|---------|---------|---------|
| a + b | a + b | 1 | 1 |
| a · b | a × b | b | a |
| x^n | x^n | n·x^(n-1) | — |
| tanh(x) | tanh(x) | 1 − tanh²(x) | — |
| ReLU(x) | max(0, x) | 1 if x>0, 0 if x<0 (undefined at 0) | — |
| e^x | e^x | e^x | — |
| ln(x) | ln(x) | 1/x | — |

**Composition pattern:** Subtraction and division don't need custom backward rules — compose them from primitives:
- `a - b = a + (-1 · b)`
- `a / b = a · b^(-1)`

Each backward is **self-contained** — only needs its own input value(s) and the upstream gradient (`out.grad`). This decentralized design is why autograd engines scale.

## Source
- Lesson: [teach/lessons/0003-value-class-and-operations.html](/home/workspace/teach/lessons/0003-value-class-and-operations.html)
- Date learned: 2026-07-09

## Connections
- Prerequisites: Chain Rule Decomposition, Value Class Architecture
- Used in: Every operation's _backward closure

## Sources

- https://en.wikipedia.org/wiki/Automatic_differentiation
- https://pytorch.org/docs/stable/autograd.html
