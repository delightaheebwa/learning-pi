<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Automatic_differentiation ; https://en.wikipedia.org/wiki/Dual_number | verified-by=fact-check-agent | date=2026-10-26 -->

# Forward-Mode Autodiff

Forward-mode autodiff computes derivatives **alongside** values during the forward pass using **dual numbers**: each value carries a *primal* (actual value) and a *tangent* (derivative with respect to the input of interest).

**Cost:** O(n) passes for n input variables — seed one input to 1, all others to 0, run a full forward pass. For n=2 inputs, you need 2 passes to get both derivatives.

**Memory:** O(1) — no graph needs to be stored.

**Best for:** Few inputs, many outputs (e.g., sensitivity analysis, Jacobian-vector products).

**Why not for neural nets:** A network has millions of weight inputs. Computing all gradients via forward mode would require millions of forward passes — computationally impossible.

## Source
- Lesson: [teach/lessons/0002-forward-vs-reverse-autodiff.html](/home/workspace/teach/lessons/0002-forward-vs-reverse-autodiff.html)
- Date learned: 2026-07-08

## Connections
- Prerequisites: Computational Graphs, Two-Pass Autodiff Algorithm
- Contrasts with: Reverse-Mode Autodiff & Backprop

## Sources

- https://en.wikipedia.org/wiki/Automatic_differentiation
- https://en.wikipedia.org/wiki/Dual_number
