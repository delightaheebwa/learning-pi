# REVIEW: grep — 2026-08-20

## Review Info
- **Date:** 2026-08-20
- **Concept:** grep
- **Last Reviewed:** 2026-08-17
- **Review Interval:** 3d (due)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative (alternation from last definitional): Compare `grep 'report'` vs `grep 'rep*rt'`. What does `*` mean inside a regex (vs a Bash glob), and what's the trap if someone expects it to match like a glob?

## Your Answer
- **Confidence:** confident
- **Answer:** Command A looks for literal `report`; Command B uses `rep*rt` as a regex pattern matching e.g. `rep1rt`, `repart`, `repxrt`.

## Assistant's Evaluation
- **Result:** Pass
- **Feedback:** Core insight correct — `*` in regex repeats the PREVIOUS char, not glob's match-anything. Refinement: `rep*rt` only allows repeated `p` (`rt`, `rpt`, `rppt`...), NOT arbitrary middle chars like `rep1rt` — those need `re.rt`/`re[apx1]rt`. Direction was right; just over-applied what `*` covers.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-20
- **next_review:** 2026-08-27 (advanced 3d → 7d)
- **Last Q Type:** discriminative
- **notes:** Pass — regex `*` repeats prev char, not glob match-anything.

## Queue / Deferred Note
- **Queue position:** active

## Key Takeaway
> Inside grep's regex, `*` repeats the preceding character — not glob's wildcard for "any characters."
