# Review — Shell Navigation & Paths — 2026-08-19

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 7d → 14d (advanced)

**Question:** For `cd ..`, `pwd`, `ls` — which are built-ins vs external programs, and why does the distinction matter for `cd` specifically?

**Answer (user):** built-ins → cd; external → pwd, ls. Distinction matters because built-ins change internal shell state while external programs cause side effects; external programs run in child processes.

**Assessment:** ✅ Correct on the core 20%: a child process inherits the parent's memory but cannot modify it — if `cd` ran as an external program it would change its own cwd and exit, leaving the shell's `$PWD` unchanged. `cd` = built-in (must mutate shell state); `ls` = external (side-effects). Minor nudge: `pwd` is *also* a built-in in bash (needn't be, but provided for speed/consistency) — refined framing: built-ins are required for anything that must change or read shell state a child can't propagate back (`cd`, `export`, variable assignment, `source`, `set`). No misconception on the core principle.

**Next Review:** 2026-09-02 (14d)
