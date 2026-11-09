# Session — swe — 2026-08-12

**Date:** 2026-08-12
**Topic:** swe Review — Shell Navigation & Paths, Testable Seam, Pipes & Pipeline Composition, C Preprocessor Macros, Makefile: Targets, Prerequisites & Recipes
**Track:** swe

## Concepts Reviewed

| Concept | Status | Interval | Next Review |
|---|---|---|---|
| Shell Navigation & Paths | developing | 7d (kept — dropped /var; ~ portability missed) | 2026-08-19 |
| Testable Seam | developing | 3d → 7d (advanced) | 2026-08-19 |
| Pipes & Pipeline Composition | developing | 7d (kept — fix order wrong) | 2026-08-19 |
| C Preprocessor Macros | developing | 3d → 7d (advanced) | 2026-08-19 |
| Makefile: Targets, Prerequisites & Recipes | developing | 7d (kept — TAB rule missed) | 2026-08-19 |

## Notes
- 25 concepts were due (backlog from missed days); shuffled, capped at 5.
- Strong on Testable Seam (dependency-injected parser → stable fixtures) and C Preprocessor Macros (dumb substitution, `SQUARE(++i)` increments twice).
- Shell Navigation: said "lib" instead of `/var/lib` — `..` resolves from cwd; `~` answered with "quicker to type" instead of portability to other usernames/HOME.
- Pipes: knew uniq needs adjacent duplicates but wrote the fix wrong (`sort -nr` before uniq instead of plain `sort`, dropped the count-ranking `sort -nr`).
- Makefile: timestamps right, recipe rule wrong — said lines "must affect the target"; real rule is TAB-indented recipe lines, and make never checks the recipe produced the target.
- Interleaving: 5 concepts shuffled, 3 discriminative / 2 definitional.
- No open questions surfaced during review.
