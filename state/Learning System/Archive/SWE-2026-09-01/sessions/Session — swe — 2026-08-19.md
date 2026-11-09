# Session — swe — 2026-08-19

**Date:** 2026-08-19
**Topic:** swe Review — Shell Navigation & Paths, Testable Seam, Make Timestamp Evaluation, C Preprocessor Macros, Arrange-Act-Assert
**Track:** swe

## Concepts Reviewed

| Concept | Status | Interval | Next Review |
|---|---|---|---|
| Shell Navigation & Paths | developing | 7d → 14d (advanced) | 2026-09-02 |
| Testable Seam | developing | 7d → 14d (advanced) | 2026-09-02 |
| Make: Timestamp Evaluation | developing | 7d → 14d (advanced) | 2026-09-02 |
| C Preprocessor Macros | developing | 7d → 14d (advanced) | 2026-09-02 |
| Arrange-Act-Assert (AAA) | developing | 7d → 14d (advanced) | 2026-09-02 |

## Notes
- Large due backlog surfaced (~24 concepts with Next Review on/before 2026-08-19, after today's reviews still ~19 queued, incl. Bash Quoting, File Permissions, PATH, bat, ripgrep, fd, Shell Conditionals, Command Substitution, Shebang, Background Jobs, Intermediate Object Files, Makefile Targets, What is the Shell, man, Shell Built-ins, Clean Targets, Make Variables, Git commit, Basic File Tools). Capped at 5 per the flow; the rest stay queued.
- **Shell Navigation & Paths:** ✅ correct — `cd` must be a built-in (child process can't propagate a cwd change back to the shell's `$PWD`), `ls` external (side-effects). Nudge: `pwd` is *also* a bash built-in. Advanced 7d → 14d.
- **Testable Seam:** ⚠️ partial — correct on brittleness of live data + controlled snapshot, but role assignment swapped: `read_meminfo` READS the live file (environment side), `parse_meminfo` RECEIVES text and interprets (pure logic side); the seam substitutes a fixture for the read. Bugs mostly live in parsing → most unit tests there. Advanced 7d → 14d.
- **Make: Timestamp Evaluation:** ✅ clean pass — all three rebuild cases + make never inspects content (mtime-only machine; comment-only save forces rebuild). Advanced 7d → 14d.
- **C Preprocessor Macros:** ⚠️ partial — got "dumb/mechanical" character + `__FILE__`/`__LINE__` intuition, but timing wrong (preprocessing, NOT runtime) and object-like (flat constant) vs function-like (takes args) meaning confused. Advanced 7d → 14d.
- **Arrange-Act-Assert:** ⚠️ partial — strong on "no fourth A" + "multiple asserts on one act fine"; conflated AAA (test structure: Given/When/Then) with Red-Green-Refactor (writing workflow: write-fail-first → pass). The AAA-vs-RGR distinction is the gap. Advanced 7d → 14d.
- Interleaving: 5 concepts shuffled, 1 discriminative / 4 definitional.
- No open questions surfaced during review.
