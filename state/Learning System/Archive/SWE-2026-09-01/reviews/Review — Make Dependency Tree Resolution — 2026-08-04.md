# Review — Make: Dependency Tree Resolution — 2026-08-04

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d (2nd review)

**Question:** How does make decide which rule to build first when a target depends on other targets that also have rules?

**Answer:** Make reads rules top-down to build a dependency tree, then executes bottom-up (leaves first). If a prerequisite is missing, make recursively finds its rule and builds it first.

**Assessment:** Correct. The user understood the bottom-up execution model — make builds dependencies before their dependents.

**Notes:** First rule is the default goal (what `make` builds with no arguments). Tree is built top-down, executed bottom-up.

**Next Review:** 2026-08-11 (7d interval)
