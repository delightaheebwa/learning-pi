# Review — Shell Redirections & Streams — 2026-08-10

**Concept:** Shell Redirections & Streams
**Source:** MIT Missing Semester — Shell
**Q Type:** Definitional
**Confidence:** 1/5

**Q:** What does `cmd 2>&1 > file` actually do — where does stdout go, where does stderr go, and why does the order matter?

**A (user):** Both stdout and stderr go to the file; the reverse order would result in an error.

**Evaluation:** Miss (classic gotcha). Redirections apply left-to-right at their moment: `2>&1` first points stderr at the current stdout (terminal), then `> file` moves stdout. Result: stdout → file, stderr → terminal. To merge both into the file you need `cmd > file 2>&1`. No error either way — order just changes the target.

**Next Review:** 2026-08-13 (3d — reset)
