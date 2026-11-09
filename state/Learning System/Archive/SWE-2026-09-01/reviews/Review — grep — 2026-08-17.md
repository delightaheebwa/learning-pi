# Review — grep — 2026-08-17

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 3d → 3d (keep)

**Question:** What does `grep -c` do, and why can't a pattern like `<h3>.*</h3>` match across lines in a file?

**Answer:** `grep -c` gets the number of times a pattern appeared. A pattern like `<h3>.*</h3>` can't match across lines because some lines may not be under the h3 tag.

**Assessment:** ⚠️ Partial. `grep -c` correctly identified as counting — precision note: it counts matching **lines**, not total occurrences (a line with two matches counts once). The multiline reason missed: grep is **line-based** — it reads one line at a time and never looks past a newline, so `<h3>` on one line and `</h3>` a few lines later can't be seen by one pattern. Also `.` doesn't match the newline character itself.

**Next Review:** 2026-08-20 (3d)