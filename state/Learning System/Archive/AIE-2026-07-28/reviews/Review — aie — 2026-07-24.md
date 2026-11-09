# aie Review — 2026-07-24

**Date:** 2026-07-24
**Track:** aie

## Concepts Reviewed

### 1. Chain Rule & Backpropagation
- **Interval:** 7d (kept — mostly right)
- **Status:** developing
- **last_reviewed:** 2026-07-24 → **next_review:** 2026-07-31
- **Verdict:** Mostly right. Had both terms correct but merged two paths. Core insight: cos(x²+y)·2x·dz/dy — knew the chain rule structure, just got tangled on expression representation.

### 2. Forward-Mode Autodiff
- **Interval:** 7d → 14d (advanced — correct)
- **Status:** developing
- **last_reviewed:** 2026-07-24 → **next_review:** 2026-08-07
- **Verdict:** Correct. Forward mode = one forward pass per input dimension (O(n)), reverse mode = one backward pass (O(1) for scalar loss). Neural nets have millions of parameters but one loss → reverse mode wins.

### 3. Value Class Architecture
- **Interval:** 7d → 14d (advanced — correct)
- **Status:** developing
- **last_reviewed:** 2026-07-24 → **next_review:** 2026-08-07
- **Verdict:** Correct. Lean `Value` has no `_backward` — `_backward` is only set when produced by an operation. A leaf node is terminal; nothing to reverse.
