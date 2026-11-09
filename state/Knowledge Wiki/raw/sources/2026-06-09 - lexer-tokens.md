# Raw Source — 2026-06-09 — Lexer and Tokens

> User-provided notes about lexical analyzers, token structure, and the lexeme-vs-literal distinction.

## Lexer (Lexical Analyzer)

When a program reads a source file, everything is just a massive wall of text. The compiler or interpreter sees your code as a single string of characters. For example, the number `42` in source code is initially just the character `'4'` followed by the character `'2'` — you cannot add them together.

The lexer "walks" through source code character by character. When it encounters a number, it does two things:
1. Tracks the text (lexeme) — keeps the string `"42"`
2. Converts and stores it (literal value) — converts the text into a real binary integer `42`

## Token Components

A token bundles:
- **Token Type/Class**: The category (KEYWORD, IDENTIFIER, INTEGER_LITERAL, ASSIGN_OP)
- **Lexeme Value**: The actual text string (e.g., `if`, `totalScore`, `42`, `=`)
- **Metadata**: Line number, column number, source file path — used for error reporting

## Analogy

- Lexeme = the item inside the box (raw text)
- Metadata = the shipping label (line, column, file)
- Token Type = the barcode category
- Token = the entire sealed, labeled box shipped to the parser

## Literal Field

The token class usually has a field named `literal` or `value` that stores the live object. This means the interpreter doesn't re-parse text later — it grabs the literal directly and performs operations immediately.
