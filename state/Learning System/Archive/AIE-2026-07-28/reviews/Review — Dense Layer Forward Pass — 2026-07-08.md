# Review — Dense Layer Forward Pass — 2026-07-08

**Date:** 2026-07-08
**Track:** aie
**Interval status:** Kept

## Question
What's the dense layer formula, and what shape is each piece?

## Response
(Wx + b) — W is m×n, x is n-sized vector, b is m-sized vector. Shapes correct but left out relu activation.

## Evaluation
Shapes spot on. Missing relu — confirmed it was a slip, not conceptual.

## Next Review: 2026-07-11
