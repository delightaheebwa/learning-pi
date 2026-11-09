# SESSION: Spaced Repetition Review — 2026-05-19

## Session Info

- **Date:** 2026-05-19
- **Topic:** Spaced Repetition Review
- **Prerequisites Reviewed:** None (pure review session)
- **New Concepts Introduced:** None

---

## What We Covered

Ran a 5-concept spaced repetition review session covering the most overdue AI/ML math concepts:

1. **Automatic differentiation** — Forward vs reverse mode, JVP vs VJP, efficiency rationale for neural networks
2. **Directional derivative** — Formula correction (∇f · v, not "derivative × JVP")
3. **Backpropagation** — Tried to trace gradient chain through a two-layer network; struggled with the specific chain (thought weights depend on each other)
4. **Jacobian-vector product** — Definition was solid but conflated efficiency argument with mechanistic reason forward mode computes JVPs in one pass
5. **Hessian matrix** — Definition correct; missed the Newton's method connection (quadratic approximation + direct solve)

---

## Concepts Status After Session

| Concept | Previous Status | New Status | Notes |
|---------|----------------|------------|-------|
| Automatic differentiation | pending_mastery | mastered | Promoted after two successful retrievals; solid on forward/reverse mode, JVP/VJP, efficiency |
| Directional derivative | developing | developing | Formula corrected to ∇f(x) · v; needs to internalize |
| Backpropagation | pending_mastery | developing | Demoted; can describe two-pass structure but can't trace specific chain through activations |
| Jacobian-vector product | pending_mastery | developing | Demoted; knows what JVP is but doesn't grasp why forward mode computes it in a single pass |
| Hessian matrix | pending_mastery | developing | Demoted; definition solid but no connection to Newton's method quadratic approximation |

---

## Demonstrations of Understanding

- **Concept:** Automatic differentiation
  - **Your confidence before evaluation:** confident
  - **Zo evaluated:** Pass
  - **Promoted to:** mastered

- **Concept:** Directional derivative
  - **Your confidence before evaluation:** uncertain
  - **Zo evaluated:** Needs More Work
  - **Status:** developing (3-day reset)

- **Concept:** Backpropagation
  - **Your confidence before evaluation:** uncertain
  - **Zo evaluated:** Needs More Work
  - **Status:** developing (3-day reset)

- **Concept:** Jacobian-vector product
  - **Your confidence before evaluation:** uncertain
  - **Zo evaluated:** Needs More Work
  - **Status:** developing (3-day reset)

- **Concept:** Hessian matrix
  - **Your confidence before evaluation:** uncertain
  - **Zo evaluated:** Needs More Work
  - **Status:** developing (3-day reset)

---

## Open Questions

- [ ] Practice tracing backpropagation gradient chains through a concrete two-layer network
- [ ] Connect Hessian to Newton's method quadratic approximation and direct-solve update

---

## Gaps & Misconceptions

- [ ] Backprop: Thinks weights depend on each other (W₁ → W₂) — need to reinforce that the chain flows through activations, not weights
- [ ] JVP: Conflates "when to use forward mode" (efficiency) with "why forward mode can compute JVPs in one pass" (chain rule direction matches computation direction)
- [ ] Hessian: Knows it describes curvature but doesn't connect to the quadratic approximation that Newton's method minimizes directly
- [ ] Directional derivative: Formula was "derivative × JVP" — needs ∇f · v to become automatic

---

## Next Steps

- [ ] Next review: 2026-05-22 for directional derivative, backpropagation, JVP, and Hessian (3-day reset)
- [ ] Next review: 2026-05-26 for automatic differentiation (7-day interval)
- [ ] Consider working through a concrete backprop example on paper before the next review
