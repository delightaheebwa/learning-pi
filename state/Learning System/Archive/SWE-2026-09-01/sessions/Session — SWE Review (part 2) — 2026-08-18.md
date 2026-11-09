# Session — SWE Review (part 2) — 2026-08-18

**Date:** 2026-08-18
**Track:** swe
**Type:** Review (5 concepts — remaining due after the earlier 5-concept review today)

## Concepts Reviewed

| Concept | Q Type | Outcome | New Interval |
|---------|--------|---------|--------------|
| Shell Redirections & Streams | Discriminative | Mostly correct | 3d → 7d |
| Acutest Unit Testing | Definitional | Mostly correct | 3d → 7d |
| xargs | Definitional | Correct | 3d → 7d |
| Black-box vs White-box Testing | Definitional | Correct | 7d → 14d |
| Parameter Expansion | Discriminative | **Needs reinforcement** | **held 3d** |

## Notes

- **Shell Redirections:** streams 0/1/2 ✅; `cp` vs `>` direction right. Correction: `notes.txt > notes.txt` fails because the shell truncates the redirect target *before* execution (wipes the file to empty), not "no stdin". A file can't be both content source and redirect target.
- **Acutest:** isolation ✅. Scope correction: `TEST_ASSERT` aborts **this test's child only** — suite continues; `TEST_CHECK` logs and keeps going.
- **xargs:** clean — stdin→args; without it `wc -l` counts filenames; `-print0`/`-0` fixes space-splitting via NUL (never in a filename).
- **Black-box vs White-box:** clean — axes independent (HOW: visibility; WHAT: scope); cstack black-box integration via process I/O lets internals refactor freely.
- **Parameter Expansion (flagged):** core model mix-up — treated `${...}` as filesystem globbing instead of pure string trimming on the variable value. Follow-up 4-part check 0/4 (`#`/`%`, ends, longest/shortest all crossed). Re-anchored: `#`=left/prefix, `%`=right/suffix, single=shortest, double=longest. User restated the mnemonic correctly → held at 3d (was scheduled 14d, demoted). Next review 2026-08-21.
- Large overdue backlog still exists (What is the Shell, man & Documentation, PATH, Basic File Tools, bat, ripgrep, find, fd, curl, Shell Conditionals, etc.) — will be swept in future sessions.

## Interleaving
5 concepts shuffled, 2 discriminative / 3 definitional. Same-source adjacency mostly unavoidable (majority MIT Missing Semester); interleaved the non-MIT sources (github/mity, Gemini+cstack) to break it where possible.

## Open Questions
- None currently.
