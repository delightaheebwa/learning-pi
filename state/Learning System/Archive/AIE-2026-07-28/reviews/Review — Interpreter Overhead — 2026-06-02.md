# Review — Interpreter Overhead — 2026-06-02

## Concept
Interpreter overhead

## Question Asked
"Why does the line-by-line EVAL loop cause overhead compared to compiled execution?"

## User's Answer
Identified that the read-parse-dispatch loop is done for each line of code while compiled code is executed at once. Used the translator metaphor correctly.

## Evaluation
**Result: Advanced to 7d (next: 2026-06-09)**

Correct. User understands the core mechanism: the interpreter re-does the full read-parse-dispatch dance for every line, while compiled code skips all that by decoupling translation from execution.
