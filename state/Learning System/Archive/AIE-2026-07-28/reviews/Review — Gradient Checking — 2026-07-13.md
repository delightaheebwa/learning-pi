# Review — Gradient Checking — 2026-07-13

**Date:** 2026-07-13
**Track:** aie
**Interval:** 3d → 3d (kept — mostly right, formula slip)

## Question
What's the formula for central-difference gradient estimation, and why use it instead of forward difference?

## Response
(f(x+h) - f(x-h)) / h². Better approximation.

## Evaluation
Got the intuition right (better approximation) but formula off. Central difference: (f(x+h) - f(x-h)) / 2h, not h². The error is O(h²) vs forward difference O(h). Kept interval.

## Next Review: 2026-07-16
