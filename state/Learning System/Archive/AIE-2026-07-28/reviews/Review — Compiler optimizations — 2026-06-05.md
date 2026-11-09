# Review — Compiler optimizations — 2026-06-05

## Performance
**Partial.** Correct: dead code elimination. Missed specific examples — math simplification (x*2 → x<<1) and register allocation (variables → CPU registers). Reasoning about why interpreters can't optimize was solid (line-by-line, no global view).

## Interval
Kept at **7d**. Next: 2026-06-12.
