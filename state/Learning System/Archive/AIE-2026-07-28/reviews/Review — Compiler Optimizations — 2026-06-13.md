# Review — Compiler Optimizations

**Date:** 2026-06-13
**Concept:** Compiler optimizations
**Status:** developing
**Interval:** 7d

## Retrieval Attempt

The user listed dead code elimination, semantic substitution, and register allocation as compiler optimizations. The user said interpreters can't do these because it's a deliberate tradeoff for quick feedback.

## Evaluation

**Good answer with minor nuance gap.** The user correctly identified:
- Dead code elimination
- Semantic substitution/swapping
- Register allocation
- The tradeoff principle

**Nuance added:** The interpreter's limitation isn't just a deliberate choice — it's a mechanical impossibility. Interpreters never see the full program at once (line-by-line), so global optimizations can't be applied regardless of design intent.

## Decision

Keep current interval (7d). Corrected the nuance. Next review: 2026-06-20.
