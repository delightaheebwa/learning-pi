# Review — Basic File Tools (cat, sort, uniq, head, tail) — 2026-08-05

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d

**Question:** Why does `uniq file` sometimes leave duplicates in the output — and what does `sort` have to do with fixing it?

**Answer:** uniq only collapses adjacent duplicate lines; unsorted input leaves scattered duplicates. sort makes duplicates adjacent so uniq completes the dedup.

**Assessment:** Correct. Core insight nailed — uniq = consecutive-only, sort first.

**Next Review:** 2026-08-12 (7d)
