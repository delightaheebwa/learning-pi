<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Orthogonality

> Related: [[ETC (Easier To Change)]], [[DRY Principle]], [[Self-Contained Components]], [[Global Data Avoidance]]

## Definition

**Orthogonality** is a design principle that says components should be independent, loosely coupled, and self-contained. The term comes from geometry — two lines at right angles (orthogonal) don't influence each other. In software, orthogonal systems are easier to change because modifying one component doesn't ripple into others.

## Key principles

- **Make things easier to change** — orthogonality is the practical implementation of ETC
- **Don't depend on properties you can't control** — every dependency ties you to something else's behavior
- **Loosely coupled** — minimize the number of connections between modules
- **Explicit over implicit** — pass context directly rather than reaching into shared state

## Testing orthogonality

Unit testing itself is a test of orthogonality. Ask: *What does it take to get a unit test to build and run?* If you have to import a large percentage of the rest of the system, that module is not well decoupled.

Unit (module-level) testing is easier to specify and perform than integration testing. These tests should run automatically as part of the regular build process.

## Why it matters

- **Change one thing, break nothing** — orthogonal components isolate changes
- **Parallel development** — independent modules can be built simultaneously
- **Reuse** — self-contained components are naturally more reusable
- **Testability** — decoupled code is testable in isolation

## Sources

- Wikipedia — Orthogonality (programming): https://en.wikipedia.org/wiki/Orthogonality_(programming)
- Pragmatic Programmer — Orthogonality: https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/
