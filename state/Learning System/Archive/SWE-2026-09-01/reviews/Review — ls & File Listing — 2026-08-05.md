# Review — ls & File Listing — 2026-08-05

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 7d → 7d (partial)

**Question:** Your teammate swears by `eza` where you use `ls`. What does `eza` give you that plain `ls` doesn't — and what does `ls -l` show that bare `ls` hides?

**Answer:** eza = human-friendly format (emojis, tree view, syntax coloring). `ls -l` = lists all files including hidden ones.

**Assessment:** Partial. eza part correct (human-friendly formatting, colors/icons/tree). `ls -l` mischaracterized — it does NOT show hidden files; that's `ls -a`. `-l` is the long format: permissions, owner, size, modification time. So `-l` = detail, `-a` = hidden.

**Next Review:** 2026-08-12 (7d)
