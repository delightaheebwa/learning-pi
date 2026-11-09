# Review — Broadcasting

**Date:** 2026-07-09
**Concept:** Broadcasting
**Track:** AI Engineering (aie)

## Question
When broadcasting a bias vector b of shape (256,) onto a batch matrix of shape (32, 256), which dimension gets aligned — and what's the rule that determines this?

## Response
bias vector b of shape (256,) becomes of shape (1, 256) and then (32, 256). It is aligned on the right dimension.

## Evaluation
**Mostly right.** The transformation (256,) → (1, 256) → (32, 256) is correct. The rule: aligned from the rightmost dimension. Said "right dimension" — close, but the precise phrasing is "rightmost dimension" (the rule starts alignment from the last axis, matching right-to-left). Kept interval.

## Outcome
- **Status:** developing → developing
- **Interval:** 3d (kept)
- **Next Review:** 2026-07-12
