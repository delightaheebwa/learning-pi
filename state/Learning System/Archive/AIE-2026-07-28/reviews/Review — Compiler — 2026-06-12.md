# Review — Compiler — 2026-06-12

## Retrieval
User described compiler stages as: Scanning → Parsing → Semantic analysis → IR → optimizations → machine code.

## Evaluation
Mostly correct but stages were merged (no frontend/backend grouping). Missed the key insight that compilers see the entire program at once, enabling optimizations impossible for interpreters.

## Verdict
Kept at 3-day interval. Core idea solid, staging needs tightening.
