# Review — Shell Redirections & Streams — 2026-08-18

**Date:** 2026-08-18
**Next Review:** 2026-08-25 (7d)
**Q Type asked:** discriminative

## Result: Mostly correct

- Streams 0/1/2 = stdin/stdout/stderr — ✅ correct.
- `cp notes.txt backup.txt` copies the file's *contents* (photocopy; original untouched), overwriting destination — ✅ correct.
- `notes.txt > notes.txt` bug — ⚠️ direction right, mechanism tangled.
  - Correction: `>` redirects the *stdout of the command on the left* to a file; `notes.txt` as a command produces no stdout, so it writes empty output.
  - The real failure: the shell **opens/truncates the redirect target before the command runs**, so `notes.txt` is wiped to 0 bytes first. Not "no stdin" — the file is clobbered regardless.
  - Key insight: a file cannot serve as both content source and redirect target.

## Interval
3d → 7d (advanced).
