<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Value Class Architecture

The `Value` class is the core data structure of a micrograd-style autograd engine. Each instance has five fields:

- `data` — the actual numerical value (float)
- `grad` — accumulated gradient (∂loss/∂this), starts at 0
- `_prev` — a **set** (not list) of children that created this value — this IS the computational graph
- `_backward` — a closure that knows how to push gradient to children; starts as no-op, replaced by each operation
- `_op` — label for what operation created this (debugging/visualization)

**Key design decisions:**
- `_prev` as a set ensures each child appears once even if used multiple times
- `_backward` as a closure: each operation function defines its own backward rule and attaches it to the output node
- `grad` starts at 0 and uses `+=` — gradients accumulate across multiple paths

The graph is built **implicitly** — every operation returns a new `Value` pointing to its operands as children. No explicit graph data structure needed.

## Source
- Lesson: [teach/lessons/0003-value-class-and-operations.html](/home/workspace/teach/lessons/0003-value-class-and-operations.html)
- Date learned: 2026-07-09

## Sources
- https://github.com/karpathy/micrograd (reference implementation of the `Value` class)

## Connections
- Prerequisites: Computational Graphs, Chain Rule Decomposition
- Leads to: Local Autograd Derivative Rules, Gradient Accumulation (+=), Topological Sort for Backprop
