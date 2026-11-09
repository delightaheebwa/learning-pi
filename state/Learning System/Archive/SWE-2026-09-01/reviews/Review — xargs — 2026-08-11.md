# Review — xargs — 2026-08-11

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 3d → 3d (keep)

**Question:** What does `find . -type f -name '*.sh' | xargs wc -l` do — and what would happen without xargs? Then: how do you make it safe for filenames containing spaces?

**Answer:** Finds all .sh files and puts them in a list with their total counts. Without xargs, filenames with spaces would be treated as different arguments rather than one.

**Assessment:** ⚠️ Partial. Spaces issue correct. Missed the core contrast: xargs converts stdin lines into *arguments*, so `wc -l` counts each file's lines; without xargs, `wc -l` reads stdin and counts the find output itself (the filenames). Did not name the fix (`find -print0 | xargs -0`).

**Next Review:** 2026-08-14 (3d)
