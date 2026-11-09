# REVIEW: xargs — 2026-08-27

## Review Info
- **Date:** 2026-08-27
- **Concept:** xargs
- **Last Reviewed:** 2026-08-18
- **Review Interval:** 3d (interval_index 0, due)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative (alternation from last definitional): `find . -name "*.sh" | xargs wc -l` splits filenames with spaces into two args and breaks. What's the one-line fix, and *why* does it work — what character can never appear in a filename?

## Your Answer
- **Confidence:** partial
- **Answer:** Reached for `-0` but placed it on the find side too (`-0`); did not name NUL as the guarantee.

## Assistant's Evaluation
- **Result:** Fail
- **Feedback:** The fix pairs `find . -name "*.sh" -print0` (NUL-delimited output) with `xargs -0` (split only on NUL). Filenames may contain spaces/tabs/newlines but NEVER a NUL byte (the C string terminator), so NUL-delimited splitting is unambiguous. The `-0` flag belongs on BOTH ends, not just xargs.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing
- **last_reviewed:** 2026-08-27
- **next_review:** 2026-08-30 (interval 0 → 0, 3d)
- **Last Q Type:** definitional

## Key Takeaway
> `find -print0 | xargs -0` is unambiguous because NUL can't appear in a filename; default xargs whitespace-splitting breaks on spaces.
