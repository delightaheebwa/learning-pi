<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Chain Rule Decomposition

The chain rule decomposes a complex derivative into a product of **simple local derivatives**. For `y = f(g(x))`:

```
dy/dx = f'(g(x)) · g'(x)
```

The key mental model: **each node in the computation only needs to know two things:**
1. Its own local derivative (e.g., d(a+b)/da = 1, d(a·b)/da = b, d(sin(x))/dx = cos(x))
2. The upstream gradient flowing from the output side

Multiply them and pass downstream. That's it. This decentralized design is why autograd engines scale to arbitrary computation graphs — no node needs global knowledge of the full expression.

## Source
- Lesson: [teach/lessons/0001-chain-rule-and-computational-graphs.html](/home/workspace/teach/lessons/0001-chain-rule-and-computational-graphs.html)
- Date learned: 2026-07-08

## Sources

- Chain rule: https://en.wikipedia.org/wiki/Chain_rule
- Automatic differentiation: https://en.wikipedia.org/wiki/Automatic_differentiation

## Connections
- Prerequisites: Derivative for ML, Chain Rule & Backpropagation
- Leads to: Local Autograd Derivative Rules, Gradient Accumulation (+=)
