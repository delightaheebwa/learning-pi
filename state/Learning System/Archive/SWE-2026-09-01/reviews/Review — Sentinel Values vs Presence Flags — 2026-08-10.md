# Review — Sentinel Values vs Presence Flags — 2026-08-10

**Concept:** Sentinel Values vs Presence Flags
**Source:** Gemini tutoring
**Q Type:** Discriminative
**Confidence:** 3/5

**Q:** Is `0` a safe sentinel for "failed" in a function returning "bytes read"? Why or why not — and what condition makes a sentinel value safe at all?

**A (user):** A sentinel is safe only if there isn't also a case where you determine presence rather than right/wrong.

**Evaluation:** Close but fuzzy. The crisp rule: a sentinel is safe only when that value can never be a legitimate payload result. `-1` for "index not found" is safe (indices are never negative). `0` for "bytes read" is NOT safe — an empty input legitimately returns 0, so "0 = failed" is ambiguous → need an explicit presence flag. (Interval kept.)

**Next Review:** 2026-08-13 (3d — kept)
