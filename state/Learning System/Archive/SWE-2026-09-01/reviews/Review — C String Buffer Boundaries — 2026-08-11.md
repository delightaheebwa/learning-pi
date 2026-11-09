# Review — C String Buffer Boundaries — 2026-08-11

**Track:** SWE (C / Testing)
**Question Type:** discriminative
**Interval:** 3d → 3d (keep)

**Question:** Why does `char username[COLUMN_USERNAME_SIZE + 1]` need the `+1`, and why was `sscanf` replaced with `strtok` + `strlen` bounds checks?

**Answer:** +1 stores an extra slot for the C language; sscanf was replaced to ensure the full line was consumed.

**Assessment:** ⚠️ Close but fuzzy. +1 right in spirit — it's for the `'\0'` null terminator. The sscanf reason was off: half is partial consumption (`%lu` stops at non-digits), the bigger half is overflow safety — sscanf writes past the buffer on long input; `strtok` + `strlen` check length *before* copying.

**Next Review:** 2026-08-14 (3d)
