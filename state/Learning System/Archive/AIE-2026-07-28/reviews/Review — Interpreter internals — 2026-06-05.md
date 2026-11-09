# Review — Interpreter internals — 2026-06-05

## Performance
**Correct.** Core flow: EVAL loop reads → parses → executes via pre-compiled C functions. Key insight: interpreter is the only executable, never creates machine code. Minor refinement: parsing step was conflated with "consulting internal functions" — it's actually lexing + parsing first, then execution.

## Interval
3d → **7d**. Next: 2026-06-12.
