# Review — Makefile: Targets, Prerequisites & Recipes — 2026-08-05

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d

**Question:** What's the difference between a target that names a real output file (like `monitor`) and one that names an action (like `clean`) — how does `make` behave differently when you run `make clean` vs `make monitor`?

**Answer:** File target runs its recipe only when prerequisites change; action target runs whenever invoked.

**Assessment:** Correct. Timestamp-driven rebuild vs always-run on explicit invocation.

**Next Review:** 2026-08-12 (7d)
