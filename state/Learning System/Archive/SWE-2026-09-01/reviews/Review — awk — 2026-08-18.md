# Review — awk — 2026-08-18

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 14d (advanced)

**Question:** awk isn't just a column-picker — what makes it a mini programming language, and how does the pattern/action structure of `awk -F, '$3 > 100 {print $1}'` break down? What do `$0`, `$1`, and `NF` mean?

**Answer:** awk is a mini language because it filters AND transforms (fields, conditionals, arithmetic, loops). `-F,` splits on commas; `$3 > 100` is the pattern (rows where field 3 > 100); `{print $1}` is the action (print field 1). `$0` = whole line, `$1` = first field.

**Assessment:** ⚠️ Mostly correct on the language nature and pattern/action breakdown. But **NF was wrong** — user said "end"; NF = Number of Fields (count of fields on the line). `$NF` = the last field. Recall: `awk -F. '{print $NF}'` gets the extension after the final dot.

**Next Review:** 2026-09-01 (14d)
