<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Reverse-Mode Autodiff & Backprop

Reverse-mode autodiff computes derivatives **after** the forward pass by walking backward through the computational graph. It propagates **adjoints** (∂output/∂this_node).

**The critical advantage:** One backward pass computes gradients for **all** inputs simultaneously. For a function with n inputs and m outputs:
- Forward mode needs **n** passes (one per input variable)
- Reverse mode needs **m** passes (one per output variable)

**Neural network asymmetry:** millions of weight inputs → one scalar loss output. This makes reverse mode the only practical choice — one backward pass = all weight gradients. Forward mode would need millions of passes.

**Memory cost:** O(ops) — the entire computational graph must be stored during the forward pass to walk backward through it.

Backpropagation **is** reverse-mode autodiff applied to a neural network's computational graph. It's not a separate algorithm.

## Source
- Lesson: [teach/lessons/0002-forward-vs-reverse-autodiff.html](/home/workspace/teach/lessons/0002-forward-vs-reverse-autodiff.html)
- Date learned: 2026-07-08

## Connections
- Prerequisites: Computational Graphs, Two-Pass Autodiff Algorithm, Forward-Mode Autodiff
- Leads to: Value Class Architecture, Topological Sort for Backprop

## Sources (verified)

- https://en.wikipedia.org/wiki/Automatic_differentiation
- https://ocw.mit.edu/courses/18-s096-matrix-calculus-for-machine-learning-and-beyond-january-iap-2023/
