# Session — swe — 2026-08-20

**Date:** 2026-08-20
**Topic:** swe Review — Bash Quoting, GCC Compilation Stages, grep, sscanf %n & Line Advancement, Background Jobs
**Track:** swe

## Concepts Reviewed

| Concept | Status | Interval | Next Review |
|---|---|---|---|
| Bash Quoting | developing | held @7d | 2026-08-27 |
| GCC Compilation Stages | developing | held @7d | 2026-08-27 |
| grep | developing | 3d → 7d (advanced) | 2026-08-27 |
| sscanf %n & Line Advancement | developing | 3d → 7d (advanced) | 2026-08-27 |
| Background Jobs | developing | → 7d | 2026-08-27 |

## Notes
- Large due backlog still queued (next-Round candidates incl. What is the Shell, PATH, bat, curl, Makefile Targets, Intermediate Object Files, Make Variables, Clean Targets, Git commit, Shell Built-ins, Command Substitution, Shebang, File Permissions, fd — most overdue from pre-8/19). Capped at 5 per the flow; the rest stay queued.
- **Bash Quoting:** ❌ held — flipped semantics: thought ANSI-C `$'...'` expands variables; actually DOUBLE quotes `"..."` expand `$`/`$(cmd)` while single `'...'` is total literal and ANSI-C is escapes-only. Gap: single vs double vs ANSI-C roles.
- **GCC Compilation Stages:** ❌ held — stage→flag mapping wrong: `-E`=preprocess, `-S`=compile→asm, `-c`=assembler→`.o`, link=no-flag final. "Stop early for object files" scenario was correct.
- **grep:** ✅ pass — regex `*` repeats previous char, not glob match-anything (direction right; over-applied what `*` covers).
- **sscanf %n & Line Advancement:** ✅ pass — whole-line advancement safest; `%n` only reflects partial-match point → silent line drift.
- **Background Jobs:** ✅ pass — bg job still child of shell → SIGHUP on close; nohup (before) / disown (after).
- Interleaving: 5 concepts shuffled, 3 discriminative / 2 definitional.
- No open questions surfaced during review; two concepts (Bash Quoting, GCC) flagged for a possible follow-up deep-dive.
