# Review — Shell Built-ins & Process Isolation — 2026-08-08

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d

**Question:** Why must `cd` be a shell built-in, while `ls` works fine as an external program?

**Answer:** `cd` mutates internal shell state (cwd) — child processes inherit memory but can't modify the parent's, so an external `cd` would change its own cwd and exit, leaving the shell untouched. `ls` only creates filesystem side-effects (disk reads/stdout), which external programs do fine.

**Assessment:** Correct — nailed the memory-isolation mechanism and the side-effects distinction.

**Next Review:** 2026-08-15 (7d)
