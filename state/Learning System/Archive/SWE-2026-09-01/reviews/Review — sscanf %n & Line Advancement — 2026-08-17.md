# Review — sscanf %n & Line Advancement — 2026-08-17

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 3d → 3d (keep)

**Question:** What does sscanf's `%n` conversion do, and why does `line += consumed` (advancing by the bytes `%n` reported) leave a parser *stuck* when parsing a line like `MemAvailable: 8123456 kB`? How do you fix it?

**Answer:** `%n` is for getting the bytes to consume. The parser gets stuck because it has to deal with a mix of digits and non-digits.

**Assessment:** ⚠️ Partial. `%n` = reports how many bytes sscanf consumed up to that point ✓. The stuck mechanism is fuzzy: `%lu` stops at the **first non-digit** — on `MemAvailable: 8123456 kB` the value parses, `line += consumed` leaves `" kB"` behind (not the newline), the next sscanf starts at `'k'` and *silently succeeds* on shifted junk (`kB\nMemAvailable` — the `%[^:]` key swallows the newline), so the next value is lost and the loop dies a line later. It's not just "a mix of digits and non-digits" — the `kB` unit suffix and newline stay unconsumed. ❌ Fix missing: match the **full line pattern** (`"%31[^:]: %lu kB%n"`) or advance by whole lines (strchr/fgets/strtok_r). sscanf reads tokens, not lines.

**Next Review:** 2026-08-20 (3d)