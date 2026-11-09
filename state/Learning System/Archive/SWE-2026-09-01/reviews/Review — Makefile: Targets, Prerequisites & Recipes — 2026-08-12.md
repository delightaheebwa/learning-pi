# Review — Makefile: Targets, Prerequisites & Recipes — 2026-08-12

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 7d (keep)

**Question:** When you run `make`, how does it decide a target is out of date — and what must be true of every recipe line in a rule?

**Answer:** Rebuilds when any prerequisite's timestamp is newer than the target's. Every recipe line must start with a TAB (spaces → "missing separator"). Make never verifies the recipe actually produced the target.

**Assessment:** ⚠️ Partial. Timestamp comparison correct. Recipe rule wrong — said lines "must affect the target"; real rule is the TAB requirement. Also didn't mention make doesn't check whether the recipe produced the target.

**Next Review:** 2026-08-19 (7d)
