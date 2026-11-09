# Review — Basic File Tools — 2026-08-19

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 14d (advanced)

**Question:** `uniq fruit.txt` on files with this order — apple, banana, apple, banana, apple — what does it output and why? Then what's the standard trick to get a true count of each unique word?

**Answer (user):** Outputs all 5 lines unchanged because `uniq` removes consecutive duplicates and these aren't adjacent. Trick: `sort | uniq -c`.

**Assessment:** ✅ Correct on the core 20%: `uniq` only collapses *adjacent/consecutive* duplicates, so alternating apple/banana leaves everything unchanged. `sort | uniq -c` groups identical lines (making them consecutive) then collapses each run with a count prefix. Nudge: add `sort -nr` to rank counts descending (top-counts pattern). Clean pass.

**Next Review:** 2026-09-02 (14d)
