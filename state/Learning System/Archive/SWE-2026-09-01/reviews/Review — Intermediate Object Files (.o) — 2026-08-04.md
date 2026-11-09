# Review — Intermediate Object Files (.o) — 2026-08-04

**Q Type:** discriminative
**Concept:** Intermediate Object Files (.o)
**Source:** MIT Missing Semester — Shell

**Question:** Why does splitting compilation into `.o` files then linking speed up rebuilds in large C projects? What's the actual mechanism?

**Answer:** Only changed source files are recompiled to .o, then all .o files are linked. Incremental recompilation.

**Assessment:** ✅ Correct. The mechanism is incremental recompilation — only dirty .c files get rebuilt.

**Score:** Correct
