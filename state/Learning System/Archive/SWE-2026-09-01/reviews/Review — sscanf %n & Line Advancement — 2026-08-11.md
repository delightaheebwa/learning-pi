# Review — sscanf %n & Line Advancement — 2026-08-11

**Track:** SWE (C / Shell)
**Question Type:** discriminative
**Interval:** 3d → 3d (keep)

**Question:** When parsing a `/proc/meminfo`-style file, why does whole-line advancement win over `strchr(line, '\n')` and `sscanf`-`%n` token-skipping — what breaks with each?

**Answer:** Whole-line advancement wins because some lines in the file may not have `'\n'`.

**Assessment:** ⚠️ Close but fuzzy. strchr half correct (not line-aware — missing `'\n'` jumps to the next newline, skipping lines). Missed the `%n` half: `%lu` stops at the first non-digit so `"123 kB"` leaves `" kB"` unconsumed and the whitespace-skip loop stalls on `'k'`.

**Next Review:** 2026-08-14 (3d)
