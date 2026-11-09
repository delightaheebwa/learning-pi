# Review — sed — 2026-08-11

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 3d (reset)

**Question:** Write the command that replaces *every* occurrence of `foo` with `bar` directly inside `notes.txt`, and state what `-i` and the trailing `/g` each do.

**Answer:** `sed -i foo bar notes.txt /g` — `-i` means inline, edit from within the shell prompt; `/g` opens the edited file.

**Assessment:** ❌ Reset. Dropped the `s/pattern/replacement/` substitution syntax; `-i` = in-place (rewrites the file on disk), not "in the shell"; `/g` = global (replace every occurrence per line), not "open the file". Same `-i` slip as the 08-02 review.

**Next Review:** 2026-08-14 (3d)
