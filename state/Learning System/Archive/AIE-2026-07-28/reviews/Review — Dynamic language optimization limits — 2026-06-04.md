# Review — Dynamic language optimization limits — 2026-06-04

## Question
Why does PyPy's tracing JIT excel at stable-type loops but struggle with real-world Python code, and what's the tradeoff with Cython's approach?

## User's answer
Stable-type loops are deterministic and easy to plan for on the fly. Real-world Python code changes unpredictably, causing "cold starts" as the JIT has to optimize and account for changes. Cython: faster on stable-type loops, slower on real-world code.

## Evaluation
PyPy part: mostly correct, but the issue isn't "cold starts" — it's deoptimization. The JIT inserts type guards and falls back to slow interpretation when they fail. Cython part: wrong. The Cython tradeoff is manual effort vs performance — it gives near-C speeds only when you manually annotate types (cdef int, cdef double), essentially writing C with Python syntax. For unannotated code, it runs at regular Python speed.

## Verdict
Incomplete — missed the Cython tradeoff entirely. Reset to 3 days.

## Next review
2026-06-07
