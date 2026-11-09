# Review — Transpiler

- **Date:** 2026-06-08
- **Concept:** Transpiler
- **Status:** developing (3d)

## Retrieval Question
What is a transpiler and how is it different from a compiler?

## User Response
Translator from one source language to another source language — e.g. Python → JavaScript, or high-level to low-level like C. Different from a compiler in that it simply does translation and nothing else.

## Evaluation
Mostly correct. One error: a transpiler stays at the same abstraction level (TypeScript → JavaScript, Sass → CSS). Going high-level to low-level (Python → C) is a compiler's job, not a transpiler's. The defining line is abstraction level, not just "it translates."

## Result
Kept at 3d. Next review: 2026-06-11.
