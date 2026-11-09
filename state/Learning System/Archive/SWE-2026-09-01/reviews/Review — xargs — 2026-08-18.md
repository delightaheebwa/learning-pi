# Review — xargs — 2026-08-18

**Date:** 2026-08-18
**Next Review:** 2026-08-25 (7d)
**Q Type asked:** definitional

## Result: Clean pass

- `xargs` converts stdin lines into **command-line arguments**.
- Without xargs: `find ... | wc -l` feeds filenames as stdin lines → `wc -l` counts *lines of input* = number of filenames (not lines inside files). With xargs, `wc -l` runs on each `.sh` file's contents → per-file line counts.
- Whitespace bug: xargs splits on whitespace by default, so `my script.sh` → two args (`my`, `script.sh`), breaking the command or hitting the wrong file.
- Fix: `find -print0` terminates names with NUL; `xargs -0` splits only on NUL. NUL can never appear in a filename, so delimiters are unambiguous regardless of spaces/newlines.

## Interval
3d → 7d (advanced).
