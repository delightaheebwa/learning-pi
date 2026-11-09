# Review — xargs — 2026-08-08

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 3d (keep)

**Question:** When would you pipe into `xargs` vs just using a `for` loop? And what breaks with `find ... | xargs wc -l` when filenames contain spaces?

**Answer:** xargs converts stdin lines into command arguments — good for batching/parallelism (`-P`) or when the tool takes filenames as args; a for loop gives shell-native control (variables, conditionals) per item. Default xargs splits on whitespace, so spaces break filenames into multiple args — fix with `find -print0 | xargs -0`.

**Assessment:** Partial — spaces issue correct. Missed the xargs-vs-loop contrast (answered "multiple arguments" vaguely).

**Next Review:** 2026-08-11 (3d)
