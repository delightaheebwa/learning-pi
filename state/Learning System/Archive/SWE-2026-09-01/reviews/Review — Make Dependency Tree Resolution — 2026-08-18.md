# Review — Make Dependency Tree Resolution — 2026-08-18

**Track:** SWE (Make)
**Question Type:** definitional
**Interval:** 7d → 14d (advanced)

**Question:** When you run `make` with no arguments, it builds the *first* target. But that target's prerequisites may themselves be missing. How does make decide what to build first, and how does the order it reads rules relate to the order it executes them?

**Answer:** Make checks the top rule and builds its prerequisites first (recursively), then builds the top-level rule last. It reads rules top-down but executes bottom-up.

**Assessment:** ✅ Correct. Captured both load-bearing ideas: read top-down to build the dependency tree, execute bottom-up (dependencies/leaves first). The first rule is the default goal; missing prerequisites get their own rule recursively invoked first.

**Next Review:** 2026-09-01 (14d)
