# Review — Bash Quoting — 2026-08-03

**Concept:** Bash Quoting
**Source:** MIT Missing Semester — Shell
**Q Type:** Discriminative
**Confidence:** 4/5

**Q:** What happens when you run `echo '$(whoami)'` vs `echo "$(whoami)"`?

**A:** Single quotes: prints `$(whoami)` literally — no expansion at all. Double quotes: command substitution expands, prints the output of `whoami` (e.g. `delight`). Use single quotes when you want the literal characters.

**Note:** User said "variable" instead of "command substitution" — minor terminology slip, core understanding correct.

**Next Review:** 2026-08-10 (7d)
