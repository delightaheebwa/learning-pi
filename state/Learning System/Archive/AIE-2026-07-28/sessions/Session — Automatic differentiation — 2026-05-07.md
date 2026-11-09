# SESSION: Automatic differentiation — 2026-05-07

> **Purpose:** Capture what happened in this learning session. Zo will use this to update the Knowledge Base at the end of the session.

## Session Info

- **Date:** 2026-05-07
- **Topic:** Automatic differentiation
- **Prerequisites Reviewed:** Derivative, chain rule (matrix form), Jacobian, backpropagation
- **New Concepts Introduced:** None

---

## What We Covered

> Summary of the session content.

- Reviewed automatic differentiation as chain rule through primitive operations.
- Distinguished forward mode as left-to-right tangent propagation.
- Distinguished reverse mode as a forward pass for intermediates followed by a backward pass for gradients.
- Connected reverse mode to neural-network training because there are many parameters and a scalar loss.

---

## Concepts Status After Session

> Updated statuses for concepts discussed in this session.

| Concept | Previous Status | New Status | Mastery Type | Notes |
|---------|----------------|------------|--------------|-------|
| Automatic differentiation | developing | pending_mastery | provisional | Mostly correct recall; one correction on reverse-mode efficiency |

---

## Demonstrations of Understanding

> Proof that you could explain / apply the concepts. Zo will ask you to demonstrate — record the results here.

- **Concept:** Automatic differentiation
  - **Your confidence before evaluation:** 6/10
  - **Your explanation:** Automatic differentiation breaks expressions into primitive operations and differentiates them; forward mode does values and derivatives left to right in one pass; reverse mode does a forward pass for intermediates and then a backward pass for derivatives.
  - **Zo evaluated:** Pass
  - **Mastery type:** provisional_mastery

---

## Open Questions

> Questions that came up but weren't fully resolved.

- [ ] None

---

## Gaps & Misconceptions

> Things that tripped you up or weren't fully clear.

- [ ] Reverse mode was described as reusing intermediates to get derivatives, but the sharper point is that it is efficient for scalar losses with many parameters.

---

## Next Steps

> What to tackle in the next session.

- [ ] Continue to the next due review items: directional derivative and Jacobian-vector product.

---

## Zo's Summary

> Zo will write a brief summary here at the end of the session.

Automatic differentiation is in place at pending mastery. The session focused on the chain-rule view, the difference between forward and reverse mode, and why reverse mode is the standard choice for neural-network gradients.
