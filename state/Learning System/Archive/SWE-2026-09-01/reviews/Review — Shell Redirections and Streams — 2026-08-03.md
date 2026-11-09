# Review — Shell Redirections & Streams — 2026-08-03

**Concept:** Shell Redirections & Streams
**Source:** MIT Missing Semester — Shell
**Q Type:** Discriminative
**Confidence:** 2/5

**Q:** You have a log file. You want to search for "ERROR" lines, count them, and save both the count and the filtered lines to a file — without losing the filtered output on screen. How would you chain this?

**A:** `grep "ERROR" log.txt | tee file.txt | wc -l`

Key insight: `tee` reads stdin, writes to a file, AND passes through to stdout. Without tee, `>` kills stdout and you lose screen output. `2>&1` is for stderr, not relevant here.

**Next Review:** 2026-08-10 (7d)
