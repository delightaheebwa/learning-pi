<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Token

A **token** is the abstract unit of data in compiler design — a package that bundles a raw text string with its identity and location. Tokens are produced by the [[Lexer]] and consumed by the parser.

## Components

A token bundles three things into an object:

| Component | Description | Example |
| --- | --- | --- |
| **Token Type/Class** | Category of the token | `IDENTIFIER`, `KEYWORD`, `INTEGER_LITERAL` |
| **Lexeme Value** | The raw text string from source | `"age"`, `"if"`, `"42"` |
| **Metadata** | Location for error reporting | line number, column number, source file |

## Literal Value

For value-typed tokens (numbers, strings), the lexer also converts the lexeme into a live runtime object:

```markdown
Lexeme "42" → Literal integer 42
Lexeme "\"hello\"" → Literal string "hello"
```

This means the interpreter/compiler doesn't re-parse text later — it grabs the literal directly.

## Analogy

Think of it like a shipping package:

- **Lexeme** = the item inside the box (raw text)
- **Metadata** = the shipping label (line, column, file)
- **Token Type** = the barcode category
- **Token** = the entire sealed, labeled box ready to ship to the parser

## In Memory

A token looks like this conceptually:

```markdown
{
  "type": "IDENTIFIER",
  "lexeme": "age",
  "literal": null,
  "line": 14,
  "column": 5,
  "source_file": "main.c"
}
```

For a number:

```markdown
{
  "type": "NUMBER",
  "lexeme": "42",
  "literal": 42,
  "line": 1,
  "column": 0,
  "source_file": "main.c"
}
```

## Sources

- Wikipedia — Lexical analysis: https://en.wikipedia.org/wiki/Lexical_analysis

## Related

- [[Lexer]] — produces tokens from source text
- [[Compiler]] — the broader pipeline that uses tokens
- [[Expressions and statements]] — tokens form expressions