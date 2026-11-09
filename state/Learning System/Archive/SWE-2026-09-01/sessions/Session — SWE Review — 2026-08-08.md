# Session — SWE Review — 2026-08-08

**Date:** 2026-08-08
**Track:** swe
**Type:** Review (5 concepts, capped)

## Concepts Reviewed

| Concept | Q Type | Outcome | New Interval |
|---------|--------|---------|--------------|
| Shell Built-ins & Process Isolation | Discriminative | Correct | 3d → 7d |
| man & Documentation | Definitional | Correct | 3d → 7d |
| Parameter Expansion | Discriminative | Miss | kept 3d |
| Background Jobs | Definitional | Miss | kept 3d |
| Clean Targets & .PHONY | Definitional | Correct | 3d → 7d |

## Notes

- 8 concepts were due (all from MIT Missing Semester); capped at 5 and shuffled.
- Shell Built-ins: nailed memory-isolation mechanism (child can't mutate parent shell state) and the side-effects distinction.
- man: `man` + `--help` both right.
- Parameter Expansion: conflated `%`/`#` with value-vs-expression substitution — they're suffix removal vs prefix removal. Reviewed with examples.
- Background Jobs: said `$PID`/`pid` instead of `$!`/`jobs`. Both mistakes are command-recall misses — flagged for next review.
- Clean Targets & .PHONY: full understanding of file-vs-command and the skip behavior.

## Interleaving
5 concepts shuffled, 3 discriminative / 2 definitional. Same-source adjacency unavoidable (all MIT Missing Semester).

## Open Questions
- None currently.
