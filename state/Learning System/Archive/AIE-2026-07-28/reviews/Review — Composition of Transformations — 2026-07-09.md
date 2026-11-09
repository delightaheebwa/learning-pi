# Review — Composition of Transformations

**Date:** 2026-07-09
**Concept:** Composition of Transformations
**Track:** AI Engineering (aie)

## Question
S scales by 2, R rotates 90°. Which order doubles the rotation radius — S @ R or R @ S?

## Response
R @ S

## Evaluation
**Correct — but the question was flawed.** Uniform scaling commutes with rotation in terms of radius from origin (both orders double it). The real insight: B @ A = apply A first then B, and S @ R ≠ R @ S (different final positions). The user clearly understands the core concept of right-to-left application order. Advanced.

## Outcome
- **Status:** developing → developing
- **Interval:** 3d → 7d
- **Next Review:** 2026-07-16
