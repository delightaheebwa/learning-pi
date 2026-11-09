# Review — Python distribution model — 2026-06-04

## Question
Why are Python standalone executables much larger than compiled binaries from Go, Rust, or C?

## User's answer
Python bundles the interpreter, compiler, and VM program. Go/Rust/C just contain the compiler/compiled code.

## Evaluation
Close but with corrections: Python bundles the CPython interpreter (not a compiler, not a VM). The interpreter is the whole runtime — it reads .pyc bytecode and executes it. Go/Rust/C executables contain only the compiled machine code — the compiler is a separate build-time tool, not bundled.

## Verdict
Mostly right but needed correction on terminology. Interval kept.

## Next review
2026-06-07
