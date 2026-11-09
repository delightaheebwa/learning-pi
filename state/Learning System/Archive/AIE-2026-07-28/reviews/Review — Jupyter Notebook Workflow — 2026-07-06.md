# Review — Jupyter Notebook Workflow — 2026-07-06

**Track:** AI Engineering (aie)
**Interval:** 3d (kept)
**Next Review:** 2026-07-09

## Question
What's the single most important discipline to follow when using notebooks for ML work, and what command restores a clean state?

## Response
"Restart the kernel."

## Evaluation
Mostly right — restarting the kernel is the key step, but the full discipline is *Restart Kernel & Run All*. Just restarting leaves an empty kernel; "Run All" re-executes everything top-to-bottom to catch out-of-order execution bugs and stale outputs.

**Result:** Kept current interval (3d).
