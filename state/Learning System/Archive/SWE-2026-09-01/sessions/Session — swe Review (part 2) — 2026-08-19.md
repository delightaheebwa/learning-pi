# Session — swe Review (part 2) — 2026-08-19

**Date:** 2026-08-19
**Track:** swe
**Type:** Review (5 concepts — swept more of the due backlog after the earlier 5-concept review today)

## Concepts Reviewed

| Concept | Q Type | Outcome | New Interval |
|---------|--------|---------|--------------|
| man & Documentation | Discriminative | Needs More Work | held 7d |
| Basic File Tools | Definitional | Correct | 7d → 14d |
| Shell Conditionals | Discriminative | Correct | 7d → 14d |
| ripgrep | Definitional | Correct | 7d → 14d |
| find | Discriminative | **Needs breadth** | held 7d |

## Notes

- **man & Documentation (flagged):** correct on `tldr` (practical examples) and `--help` (quick flag list); missed `man <program>` as the authoritative manual-page layer. Re-anchored the 4-layer ladder: man (reference) → --help (flags) → tldr (examples) → LLM (conversational). Held at 7d.
- **Basic File Tools:** clean pass — `uniq` only collapses *consecutive* duplicates; alternating apple/banana → all 5 lines unchanged. True dedup/count via `sort | uniq -c`. Nudge: `sort -nr` for top-counts. Advanced to 14d.
- **Shell Conditionals:** clean pass — `[` is a shell builtin (≡ `test`) whose exit status IS the condition; quotes prevent word-splitting of a space-containing filename. Refinement: "[`] is a builtin" more precise than "a command". Advanced to 14d.
- **ripgrep:** clean pass — recursive by default + respects `.gitignore` (skips ignored files) = fast & focused; plain `grep` isn't recursive and has no ignore awareness. Advanced to 14d.
- **find (flagged):** got `-type f` (regular file vs dir/symlink) and `-name` right. But part (2) reason wrong: quotes here prevent **glob/pathname expansion** (shell would expand `*.zip` into cwd matches before find runs), NOT word-splitting. Distinction — `$VAR` unquoted → word-splits; `*.glob` unquoted → expands — is the gap. Held at 7d.
- Large overdue backlog still exists (What is the Shell, PATH, bat, find→held, fd, curl, Command Substitution, Shebang, Background Jobs, Intermediate Object Files, Makefile Targets, Clean Targets, Make Variables, Git commit, Shell Built-ins, File Permissions, Bash Quoting, etc.) — will be swept in future sessions.

## Interleaving
5 concepts shuffled, 2 discriminative / 3 definitional. All same source (MIT Missing Semester) → adjacency constraint impossible; shuffled anyway.

## Open Questions
- None currently.
