# Review — Parameter Expansion — 2026-08-18

**Date:** 2026-08-18
**Next Review:** 2026-08-21 (3d — held tight)
**Q Type asked:** discriminative

## Result: Needs reinforcement — held at 3d

- ⚠️ Core model mix-up: `${FILE%.txt}`, `${FILE##*/}` etc. were treated as **filesystem globbing** ("all .txt files"). They are **pure string manipulation on the variable's value** — never touch the filesystem.
- Q5 answers wrong on all counts; follow-up 4-part check **0/4** (all off; `#`/`%`, ends, longest/shortest, and results all crossed).
- Anchor given + user restated correctly:
  - `#` = **left** end (prefix) · `%` = **right** end (suffix)
  - Single `#`/`%` = **shortest** · double `##`/`%%` = **longest**
  - Everything in `${...}` = string surgery on the value, never the FS.
  - Worked on `P="/a/b/c.txt"`: `${P%.txt}`→`/a/b/c`, `${P##*/}`→`c.txt` (basename), `${P#*/}`→`a/b/c.txt`, `${P%/*}`→`/a/b`.
- User's final mnemonic: "## trims longest match from the left (prefix), % trims shortest match from the right (suffix)" — ✅ correct anchor.

## Interval
Held at 3d (was scheduled 14d; demoted due to gap). Next review 2026-08-21.
