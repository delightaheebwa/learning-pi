# Session — swe — 2026-08-17

**Date:** 2026-08-17
**Topic:** swe Review — grep, GCC Compilation Stages, Shell Loops, sscanf %n & Line Advancement, jq
**Track:** swe

## Concepts Reviewed

| Concept | Status | Interval | Next Review |
|---|---|---|---|
| grep | developing | 3d (kept — multiline mechanism missed) | 2026-08-20 |
| GCC Compilation Stages | developing | 3d (kept — link-only + -S assembly missed) | 2026-08-20 |
| Shell Loops | developing | 7d → 14d (advanced) | 2026-08-31 |
| sscanf %n & Line Advancement | developing | 3d (kept — stuck mechanism fuzzy, no fix) | 2026-08-20 |
| jq | developing | 3d (kept — jq . / filter / -r all reset) | 2026-08-20 |

## Notes
- 26 concepts were due (backlog); shuffled, capped at 5.
- grep: `grep -c` counts matching **lines** (not occurrences); multiline miss — grep is line-based, `.` doesn't match newline. Kept at 3d.
- GCC Compilation Stages: `gcc -c` = preprocess → compile → assemble (stops before link). Second command is **link-only** — execution is not a gcc stage. `gcc -S` emits `main.s` assembly, not an executable. Kept at 3d.
- Shell Loops: backup loop pattern understood; technique names were "regex" (actual: glob + parameter expansion + command substitution). Quotes = word-splitting protection, not an error. Advanced 7d → 14d.
- sscanf %n: `%n` = bytes consumed ✓; stuck mechanism fuzzy (`%lu` stops at first non-digit, `kB` suffix unconsumed, next sscanf silently succeeds on shifted junk); no fix given. Kept at 3d.
- jq: `jq .` pretty-prints (validity check), filter is `.[] | select(.version > 6) | .name` kept inside single quotes, `-r` = raw output (not recursive). All three reset. Kept at 3d.
- Interleaving: 5 concepts shuffled, 2 discriminative / 3 definitional.
- No open questions surfaced during review.