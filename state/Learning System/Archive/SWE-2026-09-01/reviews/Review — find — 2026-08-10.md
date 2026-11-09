# Review — find — 2026-08-10

**Concept:** find
**Source:** MIT Missing Semester — Shell
**Q Type:** Definitional
**Confidence:** 1/5

**Q:** Write the one-liner that finds every regular file under a directory whose name ends in `.zip` — and why is piping it to `xargs rm` dangerous without `-print0`?

**A (user):** `find -f "*.zip"` — "dangerous because you may delete all zip files."

**Evaluation:** Miss. Correct syntax: `find <dir> -type f -name "*.zip"` (no `-f` flag; `-type f` = regular files, `-name` takes the pattern). Real danger: xargs splits on whitespace/newlines, so `annual report.zip` becomes two args → `rm` deletes unintended files (`annual`, `report.zip`), not just "all zips". Fix: `find ... -print0 | xargs -0 rm`.

**Next Review:** 2026-08-13 (3d — reset)
