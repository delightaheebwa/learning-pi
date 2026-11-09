# Review — JIT Compilation Tradeoffs — 2026-06-02

## Concept
JIT compilation tradeoffs

## Question Asked
"List the downsides/tradeoffs of JIT compilation."

## User's Answer
1. Many platforms don't support it (platform constraints) ✓
2. Apps are slow on first startup / cold start (startup latency) ✓
3. Tricky memory management implementation (implementation complexity) ✓

## Evaluation
**Result: Advanced to 7d (next: 2026-06-09)**

Got 3 of 5 — solid recall. Two missed: **memory footprint** (bytecode + compiler + generated machine code all in RAM) and **CPU overhead** (compiler thread steals cycles from the running program).
