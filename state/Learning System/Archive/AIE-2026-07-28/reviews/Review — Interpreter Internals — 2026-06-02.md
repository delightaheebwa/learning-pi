# Review — Interpreter Internals — 2026-06-02

## Concept
Interpreter internals

## Question Asked
"what are the key steps of the EVAL loop?"

## User's Answer
Suggested it "evaluates how to better optimize the current line of code when executing it"

## Evaluation
**Result: Reset to 3d (next: 2026-06-05)**

User conflated interpretation with optimization. The interpreter never optimizes — it reads text, parses it, and dispatches to pre-compiled C functions in a loop. The interpreter binary is the only executable; source code is data fed into it, never transformed into new machine code.

## Correct Answer
The EVAL loop: Read → Parse → Dispatch → Loop. No optimization, no code generation. The interpreter is a live translator executing one line at a time.
