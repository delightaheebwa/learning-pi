# Review — Broadcasting — 2026-07-16

**Date:** 2026-07-16 | **Track:** aie | **Interval:** 3d → 7d ✅

**Question:** You have a tensor `x` of shape `(64, 784)` and a bias `b` of shape `(784,)`. What shape is `x + b` and why does it work?

**Response:** "(64, 784) because b is aligned rightmost to lead to (1, 784) and then the 1 is scaled to 64 to enable pairwise addition"

**Evaluation:** Correct. Broadcasting aligns to the right, pads missing dims with 1, stretches 1s to match. Advancing to 7d next review.

**Next Review:** 2026-07-23
