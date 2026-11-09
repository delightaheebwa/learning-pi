# Review — JIT Compilation — 2026-06-15

## Concept
JIT compilation — compiles code at runtime, balancing interpreter-style fast startup with compiler-style fast execution.

## Performance
**Result:** Solid — advancing
- Correctly explained the hybrid approach (no build time, compiler-speed execution after warm-up)
- Named 4 of 5 downsides: memory footprint, engineering complexity, platform constraints, cold starts
- Missed: CPU overhead (compiler thread steals cycles from running program)
- Minor correction on Apple: JIT allowed in browser engines (JavaScriptCore), but restricted for third-party app dynamic code gen

## Interval Change
7d → 14d. Next review: 2026-06-29.
