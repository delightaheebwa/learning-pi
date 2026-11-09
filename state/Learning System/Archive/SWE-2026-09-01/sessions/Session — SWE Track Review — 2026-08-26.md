# Session — SWE Track Review — 2026-08-26

**Track:** swe (Shell & Terminal, MIT Missing Semester)
**Date:** 2026-08-26
**Mode:** Spaced-repetition review (Review flow)

## Queue (5 slots)

| Slot | Concept | Type | Last Q | This Q | Source | Result |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | What is the Shell *(mistake)* | concept | discriminative | definitional | course-shell | PASS |
| 2 | Shell Positional & Special Parameters | memory | definitional | discriminative | 2020/shell-tools | PASS |
| 3 | fd | memory | discriminative | definitional | course-shell | FAIL |
| 4 | jq | procedure | definitional | discriminative | course-shell | PASS |
| 5 | Shell Built-ins & Process Isolation | concept | discriminative | definitional | course-shell | PASS |

Interleaving: 5 concepts shuffled, 3 definitional / 2 discriminative. Source-adjacency guard largely unavoidable — 6 of 7 due concepts share the `course-shell` source (only Shell Positional uses `2020/shell-tools`).

## Results

- **What is the Shell** (priority-1 mistake, was `active`): PASS. `#` = root/superuser (max privileges), `$` = normal user — the old `#`=guest inversion is corrected. Mistake row → `review` (1 correct recall; graduates on next). Advanced 7d → 14d (next 2026-09-09).
- **Shell Positional & Special Parameters**: PASS. Unquoted `$@` word-splits (`"my file"` → `my`, `file`); fix = `"$@"`. Advanced to 7d (next 2026-09-02).
- **fd**: FAIL. Recalled identity (find alternative, easier syntax) but missed the load-bearing default — fd respects `.gitignore` (skips ignored files) for focused results. New mistake row (`structural`), retry 2026-08-29.
- **jq**: PASS. Filter must be ONE quoted shell argument; unquoted `|` is hijacked by the shell (`select(.name)` runs as a command). Advanced to 7d (next 2026-09-02).
- **Shell Built-ins & Process Isolation**: PASS. `cd` must be a built-in — it mutates shell state (cwd); a child process can't push a cwd change back (memory isolation). Advanced 7d → 14d (next 2026-09-09).

## Score: 4 / 5 pass

## Open questions / surfaced

- **Feynman explain-back debt:** all `concept` items (What is the Shell, Shell Built-ins, plus the broader concept backlog) still show `Feynman: —`. Advisory gate; not blocking yet, but required before a concept can be marked mastered.
- **Scheduler drift cohort:** Make cluster (Makefile Targets, Make Variables, Clean Targets, Make: Timestamp/Dependency) remains overdue (next_review 08-12 to 08-19) and was intentionally deprioritized with the archived C-project strand — flag for a future retrieval check.

## Writes

- Active Concepts: 5 rows synced (last_reviewed → 2026-08-26; next_review + Last Q Type from Attempts.json).
- 🧯 Mistakes.md: What is the Shell → `review`; +fd row.
- Log: 2026-08-26 entry appended.
