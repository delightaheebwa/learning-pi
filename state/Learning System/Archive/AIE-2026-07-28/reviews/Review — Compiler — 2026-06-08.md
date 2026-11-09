# Review — Compiler

- **Date:** 2026-06-08
- **Concept:** Compiler
- **Status:** developing (3d)

## Retrieval Question
What is a compiler and what are its key stages?

## User Response
Takes source code, translates to machine code at build time. Stages: scanning, parsing, semantic analysis → IR → optimization → translation to machine code. Said it then executes that code.

## Evaluation
Mostly correct. Pipeline is right. One error: the compiler doesn't execute code — it produces the executable (binary/assembly/bytecode) and the CPU runs it separately. The compiler's job ends at code generation.

## Result
Kept at 3d. Next review: 2026-06-11.
