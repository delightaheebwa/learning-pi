<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Formal_grammar ; https://en.wikipedia.org/wiki/Chomsky_hierarchy | verified-by=fact-check-agent | date=2026-10-26 -->

# Formal Grammar

A **formal grammar** is a set of production rules that define which strings of symbols from an alphabet are valid in a given language. It provides the mathematical foundation for both lexical analysis and parsing.

## The Levels

Formal grammars operate at two levels in a compiler/interpreter:

| Level | Alphabet | String | Implemented by |
|-------|----------|--------|----------------|
| Lexical grammar | Individual characters (a, +, 5) | A single word/token | Scanner/Lexer |
| Syntactic grammar | Entire tokens (NAME, PLUS, NUMBER) | A full expression or line of code | Parser |

A **regular grammar** (lower complexity) handles the lexical level. A **context-free grammar** (higher complexity) handles the syntactic level.

## Structure

A formal grammar G is defined as a tuple (N, Σ, P, S) where:
- **N** — Non-terminal symbols (variables that can be replaced)
- **Σ** — Terminal symbols (the alphabet — actual characters or tokens)
- **P** — Production rules (how non-terminals expand)
- **S** — Start symbol (the top-level non-terminal)

## The Goal

Given a pile of pieces (the alphabet), a formal grammar decides which combinations (strings) are valid. In English, "eggs are tasty" is valid, but "tasty are eggs for" is not. The parser uses a context-free grammar to do the same for code — distinguishing valid programs from invalid ones.

## Classification (Chomsky Hierarchy)

- **Type 3 — Regular:** Finite automata, regex — lexical grammar
- **Type 2 — Context-Free:** Pushdown automata — syntactic grammar, most programming languages
- **Type 1 — Context-Sensitive:** Linear-bounded automata (rarely used in compilers)
- **Type 0 — Unrestricted:** Turing machines (unconstrained)

## Related concepts

- [[Context-Free Grammar (CFG)]]
- [[Parser]]
- [[Lexer]]

## Sources

- https://en.wikipedia.org/wiki/Formal_grammar
- https://en.wikipedia.org/wiki/Chomsky_hierarchy
