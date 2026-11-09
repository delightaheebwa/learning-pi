<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Topological Sort for Backprop

The backward pass must process nodes in an order where each node receives **all** incoming gradient contributions **before** it propagates to its own children. Topological sort guarantees this.

**Algorithm:**
1. DFS post-order traversal from the output node, appending each node **after** its children
2. Result: `topo = [inputs_first, ..., outputs_last]`
3. Reverse: `reversed(topo) = [outputs_first, ..., inputs_last]` — exactly the backward pass order
4. Step through reversed list, calling each node's `_backward()`

**Why reverse?** The build function is post-order (append self after recursing into children), so topo has inputs first, outputs last. Reversing gives outputs first, inputs last — the correct gradient propagation order.

**Why it matters:** For `c = a*a + a`, if we processed `b` before `a`, `b`'s backward would push gradient to `a` before `a` receives its direct contribution from `c`'s `+a` — losing half the gradient. Topological sort prevents this.

The entire `backward()` method is ~8 lines: build topo, seed output.grad=1, iterate reversed.

## Source
- Lesson: [teach/lessons/0004-backward-pass-and-topological-sort.html](/home/workspace/teach/lessons/0004-backward-pass-and-topological-sort.html)
- Date learned: 2026-07-09

## Sources

- Wikipedia — Topological sorting: https://en.wikipedia.org/wiki/Topological_sorting

## Connections
- Prerequisites: Computational Graphs, Gradient Accumulation (+=), Value Class Architecture
- Used in: The `backward()` method of the Value class
