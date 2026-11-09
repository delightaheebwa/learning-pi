# Review — Shell Conditionals — 2026-08-19

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 7d → 14d (advanced)

**Question:** For `[ -f "notes.txt" ]` in an `if` — what does `[` actually do under the hood, why the space and the trailing `]`, and why are the quotes around `"$FILE"` load-bearing (what breaks with a space in the filename)?

**Answer (user):** `[` is a command of its own; it needs a space and `]` because it's a standalone command. Quotes make `$FILE` a single argument; without them a filename with a space is read as two or more arguments.

**Assessment:** ✅ Correct on the core 20%: `[` is a command (a builtin in bash, equivalent to `test`) whose exit status IS the condition; the trailing `]` is its final argument. Quotes prevent word-splitting so `"my notes.txt"` stays one argument. Refinement only: `[` is more precisely a shell *builtin* than "a command of its own" — essence stands. Clean pass.

**Next Review:** 2026-09-02 (14d)
