<!-- provenance: status=verified | source=https://xp123.com/3a-arrange-act-assert/ (Bill Wake, 2001/2011) | verified-by=fact-check-agent | date=2026-10-26 -->

# Arrange-Act-Assert (AAA)

## Overview

The **AAA pattern** (observed and named by Bill Wake, 2001, and later mentioned in Kent Beck's *Test Driven Development: By Example*) gives tests a consistent three-phase structure so failures are sharp and the test itself reads like a specification.

## The Three Phases

1. **Arrange** — set up the object and its collaborators (construct objects, put them in a known state, insert data).
2. **Act** — execute the behavior under test: a single targeted command/mutator on the object.
3. **Assert** — make claims about the observable outcome (object state, return values, collaborator interactions). Global state is rarely asserted.

## What AAA Gives You

- **Single responsibility per test.** When a test breaks, the failing test's name tells you exactly what broke — the test runner stops at the first failed assertion, so bundling many independent checks into one test destroys diagnostic precision.
- **A visible structure.** If you can't point to the Act line, the test checks too much; split it.

## Practical Nuances (from Bill Wake's 3A guide)

- **Two write-order approaches (Bill Wake):** (1) *Assert First / Frame First* (Jim Newkirk / Industrial Logic) — start with the Assert, asking "suppose it worked, how would I tell?", then fill in Arrange and Act; (2) *Act first* — when systematically working through an object's behaviors, write the Act line first. Both are valid; either beats starting with setup.
- **Not dogmatically "one assert per test".** A series of asserts can explore dimensions of a *single* act — e.g., after one insert, check both `size()` and `max()`.
- **Setup/teardown belong to Arrange**, not a fourth A. Unit tests touch only the object under test, so no external cleanup is needed.
- **Multi-act tests should usually be split** — they're really testing several behaviors.
- If the Assert section itself looks like a second implementation, the test is tangled.
- Related: **Command-Query Separation** (Bertrand Meyer) — commands change state, queries return state; tests exercise both cleanly.

## Relationship to Other Patterns

- Used by [[Red-Green-Refactor]]: Red is a failing AAA test; Green makes it pass.
- The terminal monitor from the Teach C course: fixture text in Arrange, parser call in Act, one outcome in Assert.
- Related: [[Testable Seam]] — Arrange feeds the seam.

## Sources

- Bill Wake — Arrange, Act, Assert: https://xp123.com/3a-arrange-act-assert/
- Teach C Course — Lesson 2: Your First Tests
- Gemini Socratic tutoring on testing (notebook: https://gemini.google.com/app/e21b1624e3b156a0)
