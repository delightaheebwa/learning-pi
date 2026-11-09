# Review — Parameter Expansion — 2026-08-11

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 3d → 3d (reset — syntax missed)

**Question:** `FILE=report.txt`. Write the parameter expansion that strips the `.txt` extension. Bonus: what does `${file##*/}` extract?

**Answer:** `${FILE%.txt}` — `%` removes a matching suffix, `#` removes a prefix. `${file##*/}` strips everything before the last `/` → basename.

**Assessment:** Miss — wrote `${report.##*}`, which is greedy prefix removal (nukes everything). Part 2 correct: basename.

**Next Review:** 2026-08-14 (3d)
