# Review — Clean Targets & .PHONY — 2026-08-08

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 3d → 7d

**Question:** Why do you need `.PHONY: clean`? What breaks without it?

**Answer:** `.PHONY: clean` tells make that `clean` is a command, not a real file — so it always runs the recipe even if a file named `clean` exists on disk. Without it, make sees the existing file, finds no newer prerequisites, and skips the recipe as "up to date".

**Assessment:** Correct — fully understood the file-vs-command confusion and why the recipe gets skipped.

**Next Review:** 2026-08-15 (7d)
