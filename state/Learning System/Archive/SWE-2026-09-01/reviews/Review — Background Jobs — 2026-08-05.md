# Review — Background Jobs — 2026-08-05

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 3d (partial)

**Question:** `cmd &` and `$!` vs `jobs` and `%1` — what does each pair give you, and when would you actually reach for the `%1` syntax?

**Answer:** First pair frees the CLI; second pair launches and kills background processes.

**Assessment:** Partial. Got `&` = non-blocking, but missed `$!` = PID of most recent bg job (script-friendly kill route). `jobs`/`%1` don't launch anything — `&` does. `%1` is interactive job-control syntax: `fg %1`, `bg %1`, `kill %1` without knowing the PID.

**Next Review:** 2026-08-08 (3d)
