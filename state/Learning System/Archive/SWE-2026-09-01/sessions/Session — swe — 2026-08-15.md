# Session — swe — 2026-08-15

**Date:** 2026-08-15
**Topic:** swe Review — sed (Stream Editor), C String Buffer Boundaries, ls & File Listing, Acutest Unit Testing, xargs
**Track:** swe

## Concepts Reviewed

| Concept | Status | Interval | Next Review |
|---|---|---|---|
| sed (Stream Editor) | developing | 3d → 7d (advanced) | 2026-08-22 |
| C String Buffer Boundaries | developing | 3d → 7d (advanced) | 2026-08-22 |
| ls & File Listing | developing | 7d → 14d (advanced) | 2026-08-29 |
| Acutest Unit Testing | developing | 3d (kept — safety mechanism reversed) | 2026-08-18 |
| xargs | developing | 3d (kept — mechanism + spaces fix missed again) | 2026-08-18 |

## Notes
- 34 concepts were due (backlog from missed days); shuffled, capped at 5.
- sed: clean recovery — `-i` = in-place rewrite on disk (not "edit from the shell prompt"), `/g` = per-line global replacement. Passed.
- C String Buffer Boundaries: `+1` for the `'\0'` terminator; named both sscanf failure modes (partial consumption + boundary overrun). Precision note: sscanf overruns are *writes* past the buffer; strtok+strlen validate length *before* copying. Passed.
- ls & File Listing: full recovery from 08-05 — `-l` = long format (permissions/size/mtime), `-a` = hidden files, combined `ls -la`. Passed.
- Acutest: surface contrast right (TEST_CHECK continues / TEST_ASSERT aborts) but the safety mechanism was reversed — it's not "prevents corrupting later tests", it's **each test runs in its own child process**, so the OS reclaims everything on abort. Kept at 3d.
- xargs: same two gaps as 08-11 — `xargs wc -l` counts lines *inside* files (not the file count), and the spaces fix is `-print0 | xargs -0` (NUL can't appear in filenames), not awk/regex. Kept at 3d.
- Interleaving: 5 concepts shuffled, 3 discriminative / 2 definitional.
- No open questions surfaced during review.
