# Review — Token

**Date:** 2026-06-13
**Concept:** Token (compiler/lexer)
**Status:** developing
**Interval:** 3d

## Retrieval Attempt

The user said a token bundles the datatype and the raw string, but couldn't recall the third component. The user correctly identified that a lexeme is a raw string.

## Evaluation

**Incomplete.** The user got:
- Token type/class ✓
- Lexeme/raw string ✓

**Missed/incorrect:**
- Metadata (line number, column, file name) — the "shipping label"
- Literal value — tokens store the *converted* live object (e.g., lexeme "42" → integer 42), not just the raw string
- A lexeme is just the raw text substring; the token bundles the lexeme + its converted literal value + type + metadata

## Decision

Reset interval to 3d. Re-explained metadata and literal value components. Next review: 2026-06-16.
