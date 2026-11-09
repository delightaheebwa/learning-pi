# Review — C Preprocessor Macros — 2026-08-19

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 14d (advanced)

**Question:** Explain what a #define preprocessor macro is — timing, the two kinds, why dangerous, and the __FILE__/__LINE__ power.

**Answer (user):** #define simply substitutes text in at runtime; object-like macros applied to objects, function-like applied to functions; dangerous because dumb (can substitute things that don't make sense); thinks macros can report where substitution happened.

**Assessment:** ⚠️ Partial. Correct spirit on "dumb/mechanical" and the __FILE__/__LINE__ intuition (macros capture invocation-site file:line — how TEST_CHECK reports; a plain function can't). **Corrections: (1) timing** — substitution happens at the PREPROCESSING stage, BEFORE compilation, not at runtime (pure text find-and-replace on source; gone before the program runs). **(2) kinds** — object-like = flat constant (#define BUFFER_SIZE 1024); function-like = takes args, looks like a call (#define SQUARE(x) ((x)*(x))); names are about syntax/usage, not "objects vs functions." **(3) real danger** — no type checking + repeated-argument side-effect trap (SQUARE(x++) → increments twice). Smarter alternatives: inline/constexpr (C++), hygienic AST macros (Rust/Lisp). Load-bearing details (timing, kinds) need locking in.

**Next Review:** 2026-09-02 (14d)
