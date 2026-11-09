<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Parser

The **parser** is the compiler/interpreter stage that consumes the flat token stream produced by the lexer and builds a structured representation (syntax tree) of the program according to a context-free grammar.

## Role in the Pipeline

```
Source code → [Lexer] → Token stream → [Parser] → Syntax tree → ...
```

## What It Does

- Reads tokens one at a time from the lexer
- Matches them against grammar rules (productions)
- Handles nested structures — brackets, parentheses, control flow nesting
- Reports syntax errors when tokens don't match any rule
- Produces a parse tree or abstract syntax tree (AST) for the next stages

## Contrast with the Lexer

| Aspect | Lexer/Scanner | Parser |
|--------|--------------|--------|
| Input | Characters | Tokens |
| Output | Tokens | Syntax tree |
| Grammar | Regular language | Context-free grammar |
| Handles nesting? | No | Yes |

## Types of Parsers

- **Recursive descent:** Top-down, hand-written, intuitive (Crafting Interpreters approach)
- **LR / LALR:** Bottom-up, table-driven, more powerful but harder to debug
- **Pratt parsing:** Precedence-climbing, good for expressions
- **Packrat (PEG):** Parsing expression grammars with backtracking

## Related concepts

- [[Context-Free Grammar (CFG)]]
- [[Lexer]]
- [[Token]]
- [[Compiler]]
- [[Interpreter]]

## Sources

- https://en.wikipedia.org/wiki/Parsing
