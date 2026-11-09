# Review — ls & File Listing — 2026-08-15

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 14d (advance)

**Question:** `ls` alone shows just names. What does `ls -l` add that bare `ls` hides — and if you wanted to see hidden files too, what flag would you combine?

**Answer:** `ls -l` shows more details per file, like permissions. To also see hidden files: `ls -la`.

**Assessment:** ✅ Pass. Correctly separated `-l` (long format: permissions, owner, size, mtime) from `-a` (hidden/dotfiles), and combined them as `ls -la`. Full recovery from the 08-05 miss (`-l` mischaracterized as showing hidden files).

**Next Review:** 2026-08-29 (14d)
