<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Functional_programming | verified-by=fact-check-agent | date=2026-10-26 -->

# Functional Programming

## Core Idea

Treat computation as the evaluation of mathematical functions. Data is **read-only** (immutable) — instead of changing existing variables, you pass old data into a function and get brand-new data back.

## The "Save As" Analogy

- **Traditional programming**: like editing a shared Google Doc directly. You overwrite text, old version is gone. Two people editing at once = chaos.
- **Functional programming**: like using "Save As..." every time. You get `Report_v2.docx`, original stays untouched.

## Key Properties

- **Immutability**: never change an existing variable's value. Eliminates bugs where one part of the program accidentally overwrites data another part is using.
- **Pure functions**: same input → same output, always. No side effects. Makes testing trivial.
- **No shared state**: avoids entire categories of concurrency bugs.

## Pros & Cons

**Pros:**
- Highly predictable (pure functions are deterministic)
- Concurrency-safe (immutable data can be read by multiple threads simultaneously)
- Declarative, readable code that reads like a problem description

**Cons:**
- Higher memory usage (copying data structures instead of mutating in place)
- Steep learning curve (recursion, composition instead of loops and assignments)

## When to Use

- Big data processing and data streams
- Highly concurrent or distributed systems
- Projects requiring mathematical accuracy and heavy automated testing

## Related

- [[Imperative and declarative programming]]
- [[Closures]]
- [[Expressions and statements]]

## Sources

- https://en.wikipedia.org/wiki/Functional_programming
