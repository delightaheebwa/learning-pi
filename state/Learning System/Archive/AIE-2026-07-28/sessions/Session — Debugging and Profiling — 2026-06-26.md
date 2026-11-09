# Session — Debugging and Profiling

- **Date:** 2026-06-26
- **Topic:** AI Engineering Phase 0, Lesson 12 — Debugging and Profiling
- **Source:** https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/12-debugging-and-profiling/docs/en.md
- **Status:** Ingest (no reviews run)

## Concepts Covered

| Concept | Status | Next Review |
|---------|--------|-------------|
| AI Debugging Levels | developing | 2026-06-29 |
| Print Debugging & breakpoint for AI | developing | 2026-06-29 |
| Python Logging for Training | developing | 2026-06-29 |
| Code Timing & Profiling | developing | 2026-06-30 |
| Memory Profiling (CPU & GPU) | developing | 2026-06-30 |
| Debugging Common AI Bugs | developing | 2026-07-01 |
| TensorBoard & Training Visualization | developing | 2026-07-01 |

## Key Takeaways

- AI bugs don't crash — they train silently on garbage. You need proactive debugging.
- Three levels of AI debugging: Python → Tensor Ops → Training Dynamics. 80% of bugs at levels 1-2.
- Core toolkit: debug_print, conditional breakpoint, logging, Timer, cProfile, memory profilers, TensorBoard.
- Four common AI bug patterns: shape mismatch, NaN loss, data leakage, wrong device.
- Debugging workflow: check shapes first → monitor first 10 steps → log during training → breakpoint on failure → profile for performance.
