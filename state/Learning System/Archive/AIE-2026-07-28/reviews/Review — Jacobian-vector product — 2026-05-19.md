# REVIEW: Jacobian-Vector Product — 2026-05-19

## Review Info

- **Date:** 2026-05-19
- **Concept:** Jacobian-vector product
- **Last Reviewed:** 2026-05-08
- **Review Interval:** 11 days
- **Status Before Review:** pending_mastery

---

## Zo's Prompt

*Zo asked: "A JVP represents something specific mathematically — what is it? And why can forward mode compute it alongside the function values in a single pass, while reverse mode can't?"*

---

## Your Answer

- **Confidence before evaluation:** uncertain
- **Answer:** Described JVP as the Jacobian applied to a vector giving a directional effect. On the second part, gave an efficiency-based answer (few inputs/many outputs) rather than the mechanistic reason.

---

## Zo's Evaluation

- **Result:** Needs More Work
- **Feedback:** The JVP definition was good. But the reason forward mode computes JVPs in a single pass isn't about efficiency ratios — it's that forward mode applies the chain rule from inputs → outputs, so the direction vector v naturally propagates forward. Reverse mode works outputs → inputs and computes VJPs, not JVPs.
- **Status After Review:** developing

---

## Updated Concept Record

- **status:** developing
- **last_reviewed:** 2026-05-19
- **next_review:** 2026-05-22
- **review_interval:** 3 days (reset)
- **notes:** Understands what a JVP is but conflates the efficiency argument (when to use forward mode) with the mechanistic reason it can compute JVPs in a single forward pass.

---

## Queue / Deferred Note

- **Queue position:** not queued
- **If deferred:** —

---

## Key Takeaway

Forward mode computes JVPs in one pass because the chain rule direction (inputs→outputs) matches the computation direction — v naturally propagates forward. The efficiency of this is a consequence, not the mechanism.
