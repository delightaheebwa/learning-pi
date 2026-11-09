# Session — AIE Review — 2026-07-23

**Date:** 2026-07-23
**Topic:** AI Engineering Track Review (Micrograd)
**Type:** Spaced Repetition

## Concepts Reviewed

| Concept | Status | Next Review |
|---|---|---|
| Gradient Checking | developing → developing | 2026-07-30 |
| Neural Network Training Loop | developing → developing | 2026-07-30 |
| Micrograd Architecture | developing → developing | 2026-07-26 |
| Numerical vs Analytical Derivatives | developing → developing | 2026-08-06 |
| Gradient Descent from Scratch | developing → developing (reset) | 2026-07-26 |

## Notes

- Delight nailed the central difference formula for gradient checking and the training loop update/zero-grad sequence
- Micrograd Architecture: said MLP→Neuron→Value, missed the Layer abstraction — corrected
- Numerical vs Analytical: swapped the speed tradeoff (thought analytical was slow, numerical fast) — corrected
- Gradient Descent from Scratch: wrote `data += self.grad * out.grad` instead of `data -= lr * self.grad` — reset to 3d

## Open Questions

- None surfaced

## Overdue (not reviewed, still queued)

- Forward-Mode Autodiff (due 2026-07-18)
- Value Class Architecture (due 2026-07-20)
