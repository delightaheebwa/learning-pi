# Review — Make Variables (CC, CFLAGS) — 2026-08-05

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d (full)

**Question:** You could hardcode `gcc -Wall -O2` in every recipe — why do the course notes bother with `$(CC)` and `$(CFLAGS)` instead?

**Answer:** Cleaner to store values in variables used elsewhere — changing a value needs just one line change.

**Assessment:** Correct. Single point of change instead of editing every recipe line. (Bonus not mentioned: variables also let callers override from the command line, e.g. `make CC=clang`.)

**Next Review:** 2026-08-12 (7d)
