<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# C Preprocessor Macros

## Overview

A **macro** is a piece of code given a name. Before your code is compiled, the **C preprocessor** finds every use of that name and literally copies-and-pastes the replacement text into that spot — an automatic Find & Replace that runs right before the compiler sees your source.

Macros are defined with `#define`.

## Two Flavors

**Object-like macros (constants):**

```c
#define BUFFER_SIZE 1024
```

Every `BUFFER_SIZE` in the source becomes `1024` before the compiler sees it.

**Function-like macros (inline code generators):**

```c
#define SQUARE(x) ((x) * (x))
int result = SQUARE(5);  // expands to ((5) * (5))
```

## The Power: Source Metadata

Macros can capture things ordinary functions can't — `__FILE__` and `__LINE__`. That's how `TEST_CHECK(memory.total_kb == 1000)` reports `test_meminfo.c:19: failed`: the macro expands into code that records its own location.

They also eliminate boilerplate: `TEST_LIST = { ... }` expands into the registry code that hands the array of test functions to Acutest's auto-generated `main()`. The three classic reasons to reach for a macro: eliminate repetitive boilerplate, avoid function-call overhead for tiny operations, and capture source metadata ordinary functions can't see.

## The Catch: Dumb Text Replacement

- **No type checking** — the preprocessor operates before the compiler parses types; `SQUARE` happily "accepts" anything.
- **Side-effect hazards:** `SQUARE(x++)` expands to `((x++) * (x++))` — x increments **twice**. Text substitution duplicates the expression.

## Variadic Macros (C99+)

Macros that accept a variable number of arguments using `...` and forward them via `__VA_ARGS__`:

```c
#define TEST_MSG(...) acutest_print_msg(__VA_ARGS__)
TEST_MSG("Expected total %lu, but got %lu", expected, actual);
```

Variadic macros became standard in **C99** (1999). Modern projects compiled with `-std=c17` are fine; only pre-C99 compilers lack support — the note in the Acutest README is about exactly this.

## Smarter Alternatives

Modern ecosystems replaced text macros with type-safe, scope-aware features:

- **C/C++:** `inline` functions (type-checked, no call overhead), `constexpr`/`consteval` (compile-time evaluation with full type safety), templates (generics without text replacement).
- **Compile-time evaluation:** C++ `constexpr`/`consteval`, Zig `comptime` — normal language code executed at build time with type safety.
- **Other languages:** hygienic/AST-based macro systems that manipulate syntax trees instead of text — Rust `macro_rules!` and procedural macros, Lisp/Scheme homoiconic macros, Elixir and Julia metaprogramming.

## Key Insight

Macros are a text-level feature: fast, flexible, and able to capture source location — but they bypass the type system and can bite via repeated evaluation. Prefer language features (`inline`, `constexpr`, hygienic macros) when you need "smart" behavior.

## Sources

- Gemini Socratic tutoring on C macros (notebook: https://gemini.google.com/app/8870dcd71e2919f5)

Related: [[Acutest Unit Testing]]

## References

- https://en.wikipedia.org/wiki/C_preprocessor
- https://en.cppreference.com/w/c/preprocessor/replace
