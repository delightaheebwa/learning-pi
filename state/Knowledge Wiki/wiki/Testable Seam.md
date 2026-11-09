<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Testable Seam

## Overview

A **testable seam** is a deliberate boundary in your code where a real, unpredictable dependency (like a live OS file) can be swapped for a controlled input during tests. It's the difference between testing *your logic* and testing *the environment*.

## Why It Exists

Testing code that reads live system state is a moving target:

```c
// Free RAM changes every millisecond — a test asserting a fixed value fails
// almost every time, even though the code is correct.
```

The classic example: a monitoring program that reads free RAM from the OS. If the test asserts "free RAM equals exactly 4096 MB", it fails constantly — not because the code is wrong, but because the *environment* changed. The test outcome depends on machine state, not code correctness. That's a **flaky test**.

## The Pattern

Split the job in two:

1. **Fetch** — the part that reads the changing value from the live source (side effect).
2. **Parse** — the part that turns raw text into structured data (pure logic).

Feed the parser a fixed, static piece of sample text (a **fixture**). Now the moving target is gone: the parser sees predictable input, so a test failure means the parser is wrong — nothing else.

The seam is the boundary where the controlled input substitutes for the real environment.
## The Concrete Seam (Teach C Lesson 3)

```c
int read_meminfo(const char *path, struct memory *out);   // opens a file (I/O)
int parse_meminfo(const char *text, struct memory *out);  // interprets text (logic)
```

"The second is where most bugs live, so it is where most unit tests belong." The parser is a pure function of its text argument — the test hands it a fixture and asserts on the struct fields.

Keeping the seam reproducible: vendor the test framework into the project (`curl https://raw.githubusercontent.com/mity/acutest/master/include/acutest.h -o third_party/acutest.h`) so the test command works on any machine with only a C compiler.

## Key Insight

- A test that depends on the environment tests the environment, not your code.
- Side effects belong in their own layer, separate from logic, so logic can be tested in isolation (**isolated unit**).
- Related: [[Static Fixtures & Boundary Cases]] — what sample data to feed across the seam.

## Sources

- Teach C Course — Lesson 2: Your First Tests; Lesson 3: Acutest and the Parser Seam
- Acutest (mity/acutest): https://github.com/mity/acutest
- Gemini Socratic tutoring on testable seams (notebook: https://gemini.google.com/app/e21b1624e3b156a0)
