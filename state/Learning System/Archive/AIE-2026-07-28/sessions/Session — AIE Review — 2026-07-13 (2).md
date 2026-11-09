# Session — AIE Review — 2026-07-13 (2)

**Date:** 2026-07-13
**Track:** aie
**Type:** Review
**Cap:** 5

## Concepts Reviewed

| Concept | Result | Old Interval | New Interval | Next Review |
|---|---|---|---|---|
| Shell Basics | Wrong — Ctrl+R is reverse search, not clear screen | 3d | 3d (kept) | 2026-07-16 |
| Broadcasting | Mostly right — expanded to (4,3) not (3,3) | 3d | 3d (kept) | 2026-07-16 |
| Value Class Architecture | Correct — _prev and _backward | 3d | 7d (advanced) | 2026-07-20 |
| Topological Sort for Backprop | Correct — reverse topo ensures complete gradients | 3d | 7d (advanced) | 2026-07-20 |
| Micrograd Architecture | Wrong — gave training loop instead of hierarchy | 3d | 3d (kept, user request) | 2026-07-16 |

## Notes

- Shell Basics: Need to nail down Ctrl+R (reverse search) vs Ctrl+L (clear screen).
- Broadcasting: Right-aligned shape matching — (3,) vector → (4,3) not (3,3) when paired with (4,3) matrix.
- Micrograd: Hierarchy is Value → Neuron → Layer → MLP → Training Loop. Not the loop steps.

## Archived Reviews

- `Reviews/Review — Shell Basics — 2026-07-13.md`
- `Reviews/Review — Broadcasting — 2026-07-13.md`
- `Reviews/Review — Value Class Architecture — 2026-07-13.md`
- `Reviews/Review — Topological Sort for Backprop — 2026-07-13.md`
- `Reviews/Review — Micrograd Architecture — 2026-07-13.md`
