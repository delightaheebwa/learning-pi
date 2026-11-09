# Review — Pipes & Pipeline Composition — 2026-08-12

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 7d → 7d (keep)

**Question:** `cat log.txt | uniq -c | sort -nr | head -5` gives wrong counts — duplicates split into separate rows. What's the bug, and the fix?

**Answer:** `uniq -c` only counts *consecutive* duplicates, so group first: `cat log.txt | sort | uniq -c | sort -nr | head -5`. The `sort -nr` ranks by count after counting.

**Assessment:** ⚠️ Partial. Diagnosed the core bug (uniq needs adjacent duplicates → sort first) but wrote the fix wrong: `sort -nr` before `uniq` sorts log lines numerically by content, and dropped the second `sort -nr` that ranks counts. Correct order: sort → uniq -c → sort -nr → head.

**Next Review:** 2026-08-19 (7d)
