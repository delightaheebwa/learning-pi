# Review — C String Buffer Boundaries — 2026-08-15

**Track:** SWE (C / Testing)
**Question Type:** definitional
**Interval:** 3d → 7d (advance)

**Question:** Why does `char username[COLUMN_USERNAME_SIZE + 1]` need the `+1`, and why was `sscanf` replaced with `strtok` + `strlen` bounds checks?

**Answer:** The `+1` reserves space for the `'\0'` null terminator. `sscanf` could read past the line it should read or fail to read all of it; `strtok` + `strlen` ensure the full line is consumed.

**Assessment:** ✅ Pass (precision note). `+1` for the null terminator — correct. Named both sscanf failure modes: partial consumption (`%lu` stops at non-digits, leaving `" kB"`) and boundary overrun. Precision: sscanf's overrun is a *write* past the buffer, not a read; `strtok`+`strlen` work by checking length *before* copying (validate-then-copy). "Full line consumed" phrasing belongs more to the `sscanf %n & Line Advancement` bug; here the fix is bounds-checking before the write.

**Next Review:** 2026-08-22 (7d)
