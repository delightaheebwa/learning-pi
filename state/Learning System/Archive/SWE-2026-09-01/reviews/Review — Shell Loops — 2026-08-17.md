# Review — Shell Loops — 2026-08-17

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 7d → 14d (advance)

**Question:** Explain exactly what this one-liner does, step by step — and name the three shell techniques it combines (bonus: what would break if the quotes were dropped)?

```bash
for FILE in *.txt; do cp "$FILE" "${FILE%.txt}_$(date +%Y-%m-%d).txt"; done
```

**Answer:** For every text file, it creates a duplicate file with the date and time appended to the filename. It combines the for loop, regex, and string operations. If the quotes were dropped, the argument would be `$FILE" "${FILE%.txt}_$(date +%Y-%m-%d).txt"` which would cause an error.

**Assessment:** ✅ Pass with two wording fixes. Purpose correct — a dated **backup copy** of every `.txt` (exact name: `${FILE%.txt}` strips the extension, appends `_2026-08-17`; it's the **date**, not date+time). Techniques named: the **for loop** ✓, plus **glob** (`*.txt` expansion — not regex), **parameter expansion** (`${FILE%.txt}`), and **command substitution** (`$(date ...)`). Quotes: dropping them doesn't necessarily error — it enables **word splitting**, so a file named `my notes.txt` becomes two arguments and the copy silently breaks; quoting protects against spaces.

**Next Review:** 2026-08-31 (14d)