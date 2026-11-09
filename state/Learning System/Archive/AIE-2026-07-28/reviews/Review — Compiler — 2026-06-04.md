# Review — Compiler — 2026-06-04

## Question
Walk through the stages of a compiler, from source code to output. What does it produce, and what's the key advantage over an interpreter?

## User's answer
Code → tokenizer (tokens) → parser (AST) → optimization at AST stage → bytecode → interpreter executes bytecode to produce output.

## Evaluation
Two issues:
1. The frontend (tokenization → parsing → AST) was correct. But optimization typically happens on an intermediate representation (IR) after lowering from AST, not directly on the AST itself.
2. Critical confusion: a compiler does NOT feed output to an interpreter. A compiler outputs machine code (or assembly, or bytecode for a VM) — the output runs directly on hardware (or a VM), not through an interpreter. The user mixed up the compiler pipeline with the interpreter execution model.

## Verdict
Incomplete — confused compiler output with interpreter execution. Reset to 3 days.

## Next review
2026-06-07
