# Review — Background Jobs — 2026-08-08

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 3d → 3d (keep)

**Question:** What holds the PID of the most recent background job, and what command lists all background jobs?

**Answer:** `$!` holds the PID of the most recent background job; `jobs` lists background jobs (`fg %1` brings one to the foreground).

**Assessment:** Miss — said `$PID` (wrong; it's `$!`) and `pid` (wrong; it's `jobs`).

**Next Review:** 2026-08-11 (3d)
