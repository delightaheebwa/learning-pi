<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Waterbed Theory

The **Waterbed Theory** (ascribed to Larry Wall; related to, but distinct from, Tesler's Law, the "Law of Conservation of Complexity") states that in complex systems — programming languages, tools, software designs — you cannot eliminate complexity. If you "push it down" in one place, it will "bulge" somewhere else, much like pressing on a waterbed.

Popularized by Larry Wall (creator of Perl) and others in the programming language design community.

## Core idea

Certain systems have an **irreducible minimum of complexity**. Any attempt to simplify one part of the system forces that complexity to resurface elsewhere — either in the interface, the implementation, or the user's mental model.

## Key insight for design

The goal is not to eliminate complexity, but to **place it where it is most manageable and least harmful** for the typical user. Good design acknowledges these trade-offs:

- **Hiding complexity behind defaults** works well — until those defaults fail, at which point the user must confront the hidden complexity
- **Explicit trade-offs** (e.g., Rust's borrow checker) make complexity visible but manageable
- **Leaky abstractions** are a manifestation of Waterbed Theory — the hidden complexity bulges through

## Examples in PL design

- **Manual memory management vs garbage collection**: GC "pushes down" memory complexity but creates new complexity around GC pauses, tuning, and allocation patterns
- **Static vs dynamic typing**: static typing pushes complexity into the type system and compile-time; dynamic typing shifts it to runtime errors and testing burden
- **Syntax sugar**: simplifies common patterns but adds to the language's surface area and cognitive load

## Related

- [[Runtime]]
- [[Compiler]]
- [[Virtual Machine]]
- [[Compiled vs Interpreted]]
- [[Programming paradigms comparison]]

---

*Source: [[2026-06-06 - waterbed-theory-runtime-components]]*

## Sources
- https://en.wikipedia.org/wiki/Waterbed_theory
