# Session — Interpreter Mechanics and JIT Tradeoffs — 2026-05-30

## Overview

- **Date:** 2026-05-30
- **Topic:** How interpreters work internally, why they're slower than compilers, JIT compilation downsides, and the dev vs production workflow
- **Session Type:** Ingest (content ingestion, no retrieval)

## Prerequisites Reviewed

None — this was a pure ingest session.

## New Concepts

| Concept | Status | Key Idea |
|---------|--------|----------|
| Interpreter internals | developing | EVAL loop reads code as text and calls internal pre-compiled functions; the interpreter binary is the only executable — never creates new machine code |
| Interpreter overhead | developing | Translator metaphor: simultaneous "understand + execute"; line-by-line prevents optimization; trades speed for instant feedback |
| Compiler optimizations | developing | Whole-program view enables math simplification, dead code elimination, and register allocation — impossible for interpreters |
| JIT compilation tradeoffs | developing | Five real downsides: startup latency, memory footprint, CPU overhead, implementation complexity, platform constraints (iOS) |
| Dev vs Production workflow | developing | Interpreter for fast dev iteration; compiler for production binaries — the two complement each other |

## What Was Covered

- How the interpreter EVAL loop works (read → parse → call internal function → return)
- The "translator" analogy: interpreter as live translator vs compiler as pre-translated manual
- Why interpreters can't optimize: no big-picture view, line-by-line execution
- How interpreters execute without producing binaries: code-as-data, existing binary acts out your instructions
- Compiler vs Interpreter comparison table (speed, flexibility, output)
- The five real reasons to avoid JIT compilation (with debunking of common misconceptions about crashing and hacking)
- The complementary dev/production workflow

## Final Concept Statuses

- Interpreter internals: developing (next review 2026-06-02)
- Interpreter overhead: developing (next review 2026-06-02)
- Compiler optimizations: developing (next review 2026-06-02)
- JIT compilation tradeoffs: developing (next review 2026-06-02)
- Dev vs Production workflow: developing (next review 2026-06-02)

## Open Questions

None raised during this ingest.

## Related Wiki Pages

- [[Interpreter]] — enriched with EVAL loop, translator overhead, comparison table
- [[Compiler]] — enriched with optimization capabilities section
- [[JIT Compilation]] — enriched with downsides section
- [[Compiled vs Interpreted]] — enriched with dev vs production workflow
