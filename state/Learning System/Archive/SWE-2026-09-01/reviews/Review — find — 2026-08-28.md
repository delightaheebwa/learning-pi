# REVIEW: find — 2026-08-28

## Review Info
- **Date:** 2026-08-28
- **Concept:** find
- **Last Reviewed:** 2026-08-25
- **Review Interval:** 3d (due, via Attempts.json next_review 2026-08-28)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative (alternation from last definitional): `find . -name "*.zip"` works but `find . -name *.zip` (no quotes) errors. What does the unquoted version do wrong, and why?

## Your Answer
- **Confidence:** confident
- **Answer:** Unquoted `*.zip` is glob-expanded by the shell against the cwd BEFORE find runs, so find receives literal filenames as extra args and has no pattern left; quoting keeps `*.zip` intact so find does the recursive name matching itself.

## Assistant's Evaluation
- **Result:** Pass
- **Feedback:** Core insight correct — quoting controls what bash does before the program sees it; unquoted globs expand to real cwd matches (→ "paths must precede expression"). First clean recall after three inverted fails. Mistake row advances to review (1 correct recall).
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-28
- **next_review:** 2026-09-04 (advanced 3d → 7d)
- **Last Q Type:** discriminative
- **notes:** Pass — unquoted `*.zip` glob-expands pre-find; quoting preserves the pattern for find.

## Queue / Deferred Note
- **Queue position:** active (review)

## Key Takeaway
> Quoting controls what bash does before the program sees it: unquoted `*.zip` is glob-expanded against cwd; quoted `*.zip` reaches find as a pattern.
