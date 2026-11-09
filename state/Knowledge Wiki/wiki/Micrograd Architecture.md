<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Micrograd Architecture

A five-level hierarchy that builds from a single scalar autograd Value to a full neural network training loop:

1. **Value** — scalar storing data, grad, _prev (children = the graph), _backward (local derivative), and _op label. The autograd engine.
2. **Neuron** — w·x + b → tanh. One weighted sum + activation.
3. **Layer** — list of Neurons. Parallel computation.
4. **MLP** — list of Layers. Sequential depth.
5. **Training Loop** — forward → loss.backward() → update → repeat.

Each level is built entirely on the one below it. PyTorch's architecture follows the same pattern — tensors instead of scalars, modules instead of neurons, but the exact same structural hierarchy.

**Key insight:** the hardest part (Level 1 — the autograd engine) is already done. Levels 2-5 are composition and training infrastructure.

## Source
- Lesson: [Teach/lessons/0005-gradient-checking-and-micrograd.html](teach/lessons/0005-gradient-checking-and-micrograd.html)
- Date learned: 2026-07-10
- https://github.com/karpathy/micrograd

## Connections
- Prerequisites: [[Value Class Architecture]], [[Local Autograd Derivative Rules]], [[Topological Sort for Backprop]]
- Related: [[Neural Network Training Loop]], [[Gradient Descent from Scratch]]
