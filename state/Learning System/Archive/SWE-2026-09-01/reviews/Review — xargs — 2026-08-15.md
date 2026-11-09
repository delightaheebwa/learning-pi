# Review — xargs — 2026-08-15

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 3d (keep)

**Question:** What does `find . -type f -name '*.sh' | xargs wc -l` actually count, and what would happen with `find . -type f -name '*.sh' | wc -l` instead? Then: how do you make the xargs version safe for filenames with spaces?

**Answer:** Counts the number of `.sh` files. `find | wc -l` struggles with filenames containing spaces. Fix: use awk or regex.

**Assessment:** ❌ Reset. Both core mechanisms missed (same gaps as 08-11):
1. `xargs wc -l` counts the **lines inside each .sh file** (xargs converts stdin lines into arguments; wc -l counts lines per file + total). It does NOT count files — `find | wc -l` counts filenames (wc reads find's output from stdin, one filename per line).
2. The spaces fix is not awk/regex — it's `find ... -print0 | xargs -0`: NUL-delimited paths, since NUL can never appear in a filename. Default xargs splits stdin on whitespace, which is the actual bug.

**Next Review:** 2026-08-18 (3d)
