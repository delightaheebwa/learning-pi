# Session — MIT Missing Semester Shell (remaining ingest)

- **Date:** 2026-07-30
- **Topic:** MIT Missing Semester — Course Overview + Introduction to the Shell (remaining concepts)
- **Type:** Ingest
- **Source:** https://missing.csail.mit.edu/2026/course-shell/

## Action

Completed ingestion of all remaining concepts from the course-shell page that had not been previously added to Active Concepts.

## Concepts Added (15)

| # | Concept | Prerequisites | Next Review |
|---|---------|--------------|-------------|
| 1 | awk | grep, sed | 2026-08-02 |
| 2 | Pipes & Pipeline Composition | Basic File Tools | 2026-08-02 |
| 3 | Shell Redirections & Streams | What is the Shell | 2026-08-03 |
| 4 | Shell Conditionals | Shell Navigation & Paths | 2026-08-03 |
| 5 | Shell Loops | Shell Conditionals | 2026-08-04 |
| 6 | Command Substitution & Arithmetic | Shell Navigation & Paths | 2026-08-04 |
| 7 | Shebang & Script Execution | What is the Shell | 2026-08-05 |
| 8 | Background Jobs | What is the Shell | 2026-08-05 |
| 9 | Globs/Pattern Matching | Shell Navigation & Paths | 2026-08-06 |
| 10 | Quoting in Shell | Globs/Pattern Matching | 2026-08-06 |
| 11 | Exit Status & Short-circuit | What is the Shell | 2026-08-07 |
| 12 | Script Arguments & Special Params | Shebang & Script Execution | 2026-08-07 |
| 13 | xargs | Pipes & Pipeline Composition | 2026-08-08 |
| 14 | curl | What is the Shell | 2026-08-08 |
| 15 | jq | curl | 2026-08-08 |

## Notes

- All concepts set to `developing` status, `definitional` Last Q Type
- Reviews staggered from 2026-08-02 to 2026-08-08 to avoid overload
- Wiki page (`MIT Missing Semester — Shell.md`) already had sections for most of these; full page verified
- Mastery Summary updated: 27 developing total

## Open Questions

None from this session.

## Total SWE Concepts Tracked

27 developing

## Correction (2026-07-30)

Per user request, removed 7 exercise-only concepts from Active Concepts:
- Globs/Pattern Matching, Quoting in Shell, Exit Status & Short-circuit
- Script Arguments & Special Params, xargs, curl, jq

**Rationale:** These come from the exercises section of the page, which hasn't been studied yet.

**Richer detail added** for the user's provided breakdown of:
1. Background Jobs (&, $!, kill) — jobs, fg, SIGTERM, ephemeral PID
2. Shell Redirections (2>&1 order-of-evaluation) — left-to-right evaluation, `&>` shortcut
3. Arithmetic Expansion ((()) vs $(())) — statement syntax vs value substitution

## Updated Count

20 developing (all from Lecture 1: Course Overview + Introduction to the Shell)
