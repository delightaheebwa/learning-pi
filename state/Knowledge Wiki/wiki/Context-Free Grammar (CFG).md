<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Context-Free Grammar (CFG)

A **context-free grammar** is a formal grammar where each production rule maps a single non-terminal symbol to a string of terminals and non-terminals. The "context-free" property means the rule applies regardless of surrounding context — a non-terminal expands the same way everywhere.

## Key Insight

CFGs operate at the **token level** (not the character level). They define valid combinations of tokens like `NAME`, `PLUS`, `NUMBER` into expressions, statements, and entire programs. This higher level of abstraction gives them the power to handle deeply nested structures (e.g., math expressions inside other math expressions) that regular languages cannot.

## Why Regular Languages Aren't Enough

- Regular languages (finite automata, regex) can only match patterns with a fixed amount of state.
- They cannot count arbitrarily deep nesting — e.g., matching balanced parentheses `((()))` requires tracking an unbounded depth.
- CFGs use **recursive rules** to handle arbitrary nesting: `expr → '(' expr ')' | NUMBER`

## Relationship

- **Lexical grammar** (character-level) → implemented by the **scanner/lexer** — produces tokens
- **Context-free grammar / syntactic grammar** (token-level) → implemented by the **parser** — produces syntax trees

Both are formal grammars, differing only in the abstraction level of their alphabet.

## Analogy

- **Lexical Grammar:** Spelling rules — combines letters to make valid words
- **Context-Free Grammar:** Sentence grammar — combines words to make valid sentences

## Applications

- Programming language syntax specification
- Parsers in compilers and interpreters
- Data serialization formats (JSON, XML)
- Natural language processing

## Related concepts

- [[Parser]]
- [[Formal Grammar]]
- [[Lexer]]
- [[Token]]

## References

- Crafting Interpreters (Nystrom) — Chapter on parsing
- Dragon Book (Compilers: Principles, Techniques, and Tools)

## Sources

- https://en.wikipedia.org/wiki/Context-free_grammar
