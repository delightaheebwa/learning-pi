# REVIEW: grep — 2026-08-28

## Review Info
- **Date:** 2026-08-28
- **Concept:** grep
- **Last Reviewed:** 2026-08-20
- **Review Interval:** 3d (due; next_review 2026-08-27 drifted to today)
- **Status Before Review:** developing

## Assistant's Prompt
> Definitional (alternation from last discriminative): What does `*` mean inside a grep regex, and how is that different from `*` in a shell glob like `*.zip`?

## Your Answer
- **Confidence:** confident-but-wrong
- **Answer:** Said in grep regex `*` means "one or more characters" and glob `*` means "any character".

## Assistant's Evaluation
- **Result:** Fail
- **Feedback:** Slip: regex `*` repeats the PREVIOUS char zero-or-more times (not "any"; not "one or more" — that is `+`; "any char" is `.`). Shell glob `*` = any chars. So `grep 'a*'` matches every line (zero `a`s allowed). Mnemonic: shell `*` = match anything; regex `*` = repeat what is before it.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-28
- **next_review:** 2026-08-31 (held 3d)
- **Last Q Type:** definitional
- **notes:** Fail — regex `*` repeats previous char, not glob's "any"; new mistake row.

## Queue / Deferred Note
- **Queue position:** active (new mistake, retry 2026-08-31)

## Key Takeaway
> Shell `*` = any characters; regex `*` = repeat the previous character (zero or more). `grep 'a*'` matches every line.
