# Review — Wildcards & Globs — 2026-08-03

**Concept:** Wildcards & Globs
**Source:** MIT Missing Semester — Shell
**Q Type:** Discriminative
**Confidence:** 4/5

**Q:** You run `echo *.txt` and it prints `file1.txt file2.txt`. You run `echo "*.txt"` and it prints `*.txt`. What's actually happening at the shell level in each case — and when would you *want* the second behavior?

**A:** Unquoted `*` triggers glob expansion — shell matches files in cwd. Quoted `"*"` prevents glob expansion, prints literally. Want the second when you just need to print text with `*` in it.

**Follow-up:** Double quotes do prevent glob expansion, but they still allow `$USER`, `$(cmd)`, and arithmetic. Single quotes kill everything. `echo "$HOME/*.txt"` expands `$HOME` but keeps `*.txt` literal; `echo '$HOME/*.txt'` prints the whole thing as-is.

**Next Review:** 2026-08-10 (7d)
