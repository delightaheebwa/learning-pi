# Session — C Parsing & Makefile Ingest

- **Date:** 2026-08-07
- **Type:** Ingest (not review)
- **Source:** Gemini Socratic tutoring — parsing `/proc/meminfo` in C + Makefile dependencies (notebook: https://gemini.google.com/app/8870dcd71e2919f5)
- **Concepts added (2, SWE track, `developing`, `last_reviewed` 2026-08-07, `Last Q Type` definitional):**
  - Sentinel Values vs Presence Flags — next_review 2026-08-10
  - sscanf %n & Line Advancement — next_review 2026-08-11 (staggered +1 day)
- **Enriched:** Make: Timestamp Evaluation (last_reviewed → 2026-08-07, next_review → 2026-08-14) — Makefile-as-own-prerequisite; make compares timestamps only, never content; comment-only save still triggers rebuild
- **Wiki pages created (2):** Sentinel Values vs Presence Flags, sscanf %n & Line Advancement; `MIT Missing Semester — Shell` page extended with Makefile self-update section
- **Key insights ingested:**
  - Sentinel values: reusing a payload value (`0`) to mean "missing" is ambiguous when `0` is a valid quantity. `(total_kb != 0 && available_kb != 0)` rejects a legitimate zero read (false negative) and only "catches" absent fields by coincidence (`{0}` init → accidental true negative). Fix: explicit presence flags (`has_total`, `has_available`), set on key match, return `(has_total && has_available) ? 0 : -1`; alternatives: bitmask or field counter. Decouple structural presence from numeric payload.
  - `strchr` is not line-aware: a missing `\n` in the MIDDLE of a buffer makes it jump to the next newline, silently skipping valid lines; missing `\n` on the last line → `NULL` → clean break (line already parsed).
  - `%n` reports characters consumed in the format match, not where the line ends — and `%lu` stops at the first non-digit, so `line += consumed` leaves `" kB"` behind. The shifted line does NOT make sscanf fail: `%[^:]` swallows newlines, so it succeeds with a garbage key (`"kB\nMemAvailable"`) and the value is silently lost. Fix: match the full line pattern (`"%31[^:]: %lu kB%n"`) or advance by whole lines (`strchr`/`fgets`/`strtok_r`).
  - Makefile: adding `Makefile` to a target's prerequisites makes the build recompile when the Makefile changes — make compares mtimes only, never content.
- **Learning-review gate:**
  - Factual gate: PASS — `%n` semantics verified against cppreference; GNU make timestamp-only comparison verified against the GNU make manual
  - Quality gate: PASS after 2 cycles — cycle 1: renamed "Robust pattern" → "Working Pattern (Common Case)" + caveat cross-ref to presence flags; corrected "false positive" → "accidental true negative"; `%n` wording fix. Cycle 2: corrected the sscanf failure mechanism (`%[^:]` swallows newlines → garbage key, not parse failure); moved caveat out of the code block; no third reviewer pass per 2-cycle cap
- **Concurrency note:** a parallel session was processing the same ingest; its wiki-page writes collided with this session's index/Active Concepts edits (concatenated lines), all repaired during the consistency check.
- **Open questions:** none new
