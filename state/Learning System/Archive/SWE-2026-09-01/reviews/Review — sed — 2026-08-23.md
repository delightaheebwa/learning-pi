# Review — sed — 2026-08-23

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional (alternated from discriminative)
**Interval:** held 7d

**Question:** What is `sed`, and what do the `-i` and `/g` flags do in `sed -i 's/pattern/replacement/g' file`?

**Answer:** "sed is a stream editor. it edits files from the terminal. -i tells sed to edit the file inline and '/g' tells sed to do nothing else."

**Assessment:** ⚠️ Hold. Stream editor + `-i` (in-place edit) correct. `/g` wrong: it does NOT mean "do nothing else" — `/g` = **global**, replacing EVERY occurrence of the pattern on each line; without it only the FIRST match per line is replaced. Contrast with the 08-15 pass, where /g was answered correctly — this flip suggests the flag was memorized as a pair, not understood. Held 7d.

**Next Review:** 2026-08-30 (held 7d)
