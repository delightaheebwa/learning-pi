<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Red-Green-Refactor

## Overview

The core **TDD loop**: write a failing test first (Red), write the minimal code to make it pass (Green), then clean up the design (Refactor). The cycle produces short feedback loops and a trustworthy test suite.

## The Three Steps

- **Red** — write a test that fails *for a meaningful reason* (a missing behavior or a suspected bug).
- **Green** — write the minimal code needed to pass the test. No gold-plating.
- **Refactor** — clean up code and improve design without breaking the now-passing test.

## Why Red Must Come First

Seeing a test fail before writing the implementation proves two things:

1. **The test actually runs your new code** — not an old version, cached build, or a test that was never wired up.
2. **The assertion can catch a failure** — it isn't a false positive that passes unconditionally no matter what the code does.

The smoke-detector analogy: if you never expose the detector to smoke, you don't know it works — it might sit on the ceiling dead, always returning Green. A test that passes with broken code is worse than no test: it manufactures false confidence.

## Relationship to Other Patterns

- Red is a failing [[Arrange-Act-Assert (AAA)]] test; Green makes it pass.

## Practical Notes

- A meaningful Red requires the failure to be about the *behavior*, not a test bug — check the failure message before writing the fix.
- In terminal-based tests, a nonzero exit code = Red, exit 0 = Green.
- The pattern is useful even without formal TDD discipline — e.g., write a test for a suspected bug, watch it fail, fix, watch it pass.
- **Red can be a compile-time failure.** In Teach C Lesson 3, `parse_meminfo` doesn't exist when the test is first written — the missing symbol is the Red. That's still useful: the test compiles only if the interface you declared matches, so the test doubles as an interface spec before implementation details distract.
- **Lesson 3 practice loop:** add a test asserting a missing `MemAvailable` line returns an error (starter code only checks `MemTotal`, so the test goes Red) → change the return condition to require both fields → `make test` goes Green.

## Sources

- Teach C Course — Lesson 2: Your First Tests; Lesson 3: Acutest and the Parser Seam
- Gemini Socratic tutoring on testing (notebook: https://gemini.google.com/app/e21b1624e3b156a0)
- https://martinfowler.com/bliki/TestDrivenDevelopment.html
