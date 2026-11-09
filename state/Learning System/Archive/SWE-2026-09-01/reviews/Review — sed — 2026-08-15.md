# Review — sed — 2026-08-15

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d (advance)

**Question:** `sed 's/foo/bar/' notes.txt` prints to the terminal, but `sed -i 's/foo/bar/' notes.txt` doesn't. Why the difference? And what does appending `/g` to the substitution change?

**Answer:** `-i` (inline) edits the file in place, so nothing is printed to the terminal. `/g` makes the substitution global — it replaces every occurrence on the line, not just the first.

**Assessment:** ✅ Pass. `/g` = global per-line replacement, correct. `-i` understood as in-place rewrite of the file on disk (recovery from the 08-11 fail where `-i` was "edit from within the shell prompt"). Minor precision: sed always does the substitution — without `-i` the transformed stream goes to stdout; with `-i` it goes back into the file.

**Next Review:** 2026-08-22 (7d)
