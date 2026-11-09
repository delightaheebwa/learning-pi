# Review — Two-Pass Autodiff Algorithm — 2026-07-11

- **Track:** AI Engineering (aie)
- **Session:** 2026-07-11 — AIE Review Session
- **Result:** ⚠️ Close but missed the general-case term
- **Interval:** 3d (kept)

## Question Asked
"The backward pass walks the computational graph in what order?"

## User's Answer
"right to left"

## Assessment
Captured the direction correctly but "right to left" is a spatial metaphor that breaks on branching graphs. The correct answer is **reverse topological order** — a topological sort puts inputs first, outputs last; reversing it guarantees every node receives all incoming gradient contributions before propagating. This is the general case, while "right to left" only works for simple linear chains.

## Correction
Kept current interval — the user had the right intuition (terminology gap, not conceptual).
