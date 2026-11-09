# Review — Computational Graphs (Autodiff) — 2026-07-11

- **Track:** AI Engineering (aie)
- **Session:** 2026-07-11 — AIE Review Session
- **Result:** ❌ Concept fuzzy
- **Interval:** 3d → 3d (reset)

## Question Asked
"In micrograd's Value class, what single field IS the computational graph — no separate data structure needed?"

## User's Answer
"self._backward"

## Diagnostic
The user said they were confused about what defines the graph structure. Clarified that `_prev` (the set of child nodes) is the graph — every Value stores a reference to its operands, and the collection of these references across all nodes IS the DAG. `_backward` stores the local derivative function, not the graph.

## Correction
Reset to 3d. The graph = `_prev` set. The local derivative = `_backward`. Two distinct fields.
