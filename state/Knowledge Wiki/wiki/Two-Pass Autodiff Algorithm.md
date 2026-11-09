<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Two-Pass Autodiff Algorithm

Every autodiff system follows the same two-pass algorithm:

1. **Forward Pass** — Compute every node's value in topological order from inputs → output. Build the computational graph implicitly by recording which values produced which outputs.

2. **Backward Pass** — Seed `output.grad = 1.0` (since ∂output/∂output = 1), then walk through the graph in reverse order. At each node, compute `grad_to_children = local_derivative × upstream_gradient`.

This is the universal algorithm behind backpropagation. For `y = sin(x²)`:
- Forward: x=2 → a=x²=4 → y=sin(4)≈-0.7568
- Backward: dy/dy=1 → dy/da=cos(4)×1≈-0.6536 → dy/dx=2x×(-0.6536)≈-2.6146

## Source
- Lesson: [teach/lessons/0001-chain-rule-and-computational-graphs.html](/home/workspace/teach/lessons/0001-chain-rule-and-computational-graphs.html)
- Date learned: 2026-07-08

## Sources
- https://en.wikipedia.org/wiki/Automatic_differentiation

## Connections
- Prerequisites: Computational Graphs, Chain Rule & Backpropagation
- Leads to: Reverse-Mode Autodiff & Backprop, Topological Sort for Backprop
