# Session — swe — 2026-08-11

**Date:** 2026-08-11
**Topic:** swe Review — Red-Green-Refactor, Wildcards & Globs, GCC Compilation Stages, Parameter Expansion, Static Fixtures & Boundary Cases
**Track:** swe

## Concepts Reviewed

| Concept | Status | Interval | Next Review |
|---|---|---|---|
| Red-Green-Refactor | developing | 3d → 7d (advanced) | 2026-08-18 |
| Wildcards & Globs | developing | 7d → 14d (advanced) | 2026-08-25 |
| GCC Compilation Stages | developing | 3d (reset — stages/flags missed) | 2026-08-14 |
| Parameter Expansion | developing | 3d (reset — suffix/prefix syntax missed) | 2026-08-14 |
| Static Fixtures & Boundary Cases | developing | 3d → 7d (advanced) | 2026-08-18 |

## Notes
- 28 concepts were due; shuffled, capped at 5.
- Strong on Red-Green-Refactor (why Red proves the test works), wildcard vs brace expansion distinction, and fixture purpose.
- Two resets: `GCC Compilation Stages` (couldn't recall the 4 stages or flags; confused `-o`/`-l`/`-c` with stage flags) and `Parameter Expansion` (`${report.##*}` instead of `${FILE%.txt}`).
- Interleaving: 5 concepts shuffled, 2 discriminative / 3 definitional.
- No open questions surfaced during review.

---

## Session 2 — 2026-08-11 (afternoon)

**Topic:** swe Review — sed, Black-box vs White-box Testing, C String Buffer Boundaries, sscanf %n & Line Advancement, xargs
**Track:** swe

## Concepts Reviewed

| Concept | Status | Interval | Next Review |
|---|---|---|---|
| sed (Stream Editor) | developing | 7d → 3d (reset — syntax & /g missed) | 2026-08-14 |
| Black-box vs White-box Testing | developing | 3d → 7d (advanced) | 2026-08-18 |
| C String Buffer Boundaries | developing | 3d (kept — fuzzy on strtok reason) | 2026-08-14 |
| sscanf %n & Line Advancement | developing | 3d (kept — missed %n stall half) | 2026-08-14 |
| xargs | developing | 3d (kept — missed wc-vs-xargs contrast) | 2026-08-14 |

## Notes
- 23 concepts were due; shuffled, capped at 5.
- Strong on black-box vs white-box (visibility split + refactor protection).
- sed reset: dropped `s///` substitution syntax, `-i` = in-place (same slip as 08-02), `/g` = global not "open the file".
- C String Buffer: +1 (null terminator) right; strtok reason missed overflow safety.
- sscanf: strchr non-line-aware right; %lu stopping at non-digits (the `" kB"` stall) missed.
- xargs: spaces issue right (second time partial on this concept); missed that without xargs `wc -l` counts the find output itself.
- Interleaving: 5 concepts shuffled, 2 definitional / 3 discriminative.
- No open questions surfaced during review.
