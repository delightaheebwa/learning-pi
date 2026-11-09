# SESSION: Automatic Differentiation Ingest — 2026-05-05

> **Purpose:** Capture the ingest of automatic differentiation screenshots and notes into the learning system.

## Session Info

- **Date:** 2026-05-05
- **Topic:** Automatic differentiation ingest
- **Prerequisites Reviewed:** Derivative; Chain rule (matrix form); Jacobian; Backpropagation
- **New Concepts Introduced:** Automatic differentiation; Directional derivative; Jacobian-vector product

---

## What We Covered

> Summary of the session content.

- Ingested screenshots and notes about differentiation methods, including symbolic, numerical, and automatic differentiation.
- Added a focused source note for forward-mode automatic differentiation and JVPs.
- Clarified that symbolic differentiation can suffer from expression swell and numerical differentiation can suffer from truncation and round-off error.
- Connected forward-mode AD to tangent propagation through a program.
- Added new concept pages for **Directional derivative** and **Jacobian-vector product**.
- Linked JVPs to the Jacobian, directional derivatives, and the practical case where you only need one direction instead of the full matrix.

---

## Concepts Status After Session

> Updated statuses for concepts discussed in this session.

| Concept | Previous Status | New Status | Mastery Type | Notes |
|---------|----------------|------------|--------------|-------|
| Automatic differentiation | developing | developing | pending | Expanded with forward-mode JVPs and differentiation-method comparison |
| Directional derivative | not_started | developing | pending | Added as the general “move in this direction” concept |
| Jacobian-vector product | not_started | developing | pending | Added as the forward-mode product J_f(x)r |

---

## Demonstrations of Understanding

> Proof that you could explain / apply the concepts. Zo will ask you to demonstrate — record the results here.

- **Concept:** Automatic differentiation
  - **Your confidence before evaluation:** confident
  - **Your explanation:** Automatic differentiation is algorithmic chain-rule propagation through basic ops, with forward mode carrying tangents and reverse mode carrying adjoints.
  - **Zo evaluated:** Pass
  - **Mastery type:** pending_mastery

- **Concept:** Directional derivative
  - **Your confidence before evaluation:** confident
  - **Your explanation:** A directional derivative is how the output changes if you move from a point in a chosen direction instead of just along one coordinate axis.
  - **Zo evaluated:** Pass
  - **Mastery type:** pending_mastery

- **Concept:** Jacobian-vector product
  - **Your confidence before evaluation:** confident
  - **Your explanation:** A JVP is J_f(x)r, so it gives the effect of one direction without building the whole Jacobian.
  - **Zo evaluated:** Pass
  - **Mastery type:** pending_mastery

---

## Open Questions

> Questions that came up but weren't fully resolved.

- [ ] When is it better to think about forward mode as a Jacobian column versus as a directional derivative?

---

## Gaps & Misconceptions

> Things that tripped you up or weren't fully clear.

- [ ] None yet

---

## Next Steps

> What to tackle in the next session.

- [ ] Review Automatic differentiation on 2026-05-07
- [ ] Revisit Directional derivative and Jacobian-vector product once more in practice

---

## Zo's Summary

> Zo will write a brief summary here at the end of the session.

Automatic differentiation was expanded to include forward-mode JVPs, the practical tradeoff versus full Jacobians, and the distinction between symbolic, numerical, and algorithmic differentiation.
