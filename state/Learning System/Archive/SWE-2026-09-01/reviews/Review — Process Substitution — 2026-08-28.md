# REVIEW: Process Substitution — 2026-08-28

## Review Info
- **Date:** 2026-08-28
- **Concept:** Process Substitution
- **Last Reviewed:** 2026-08-25
- **Review Interval:** 3d (due)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative (alternation from last definitional): `diff <(ls a) <(ls b)` — how is `<(cmd)` different from `$(cmd)`, and why can you not write `diff $(ls a) $(ls b)`?

## Your Answer
- **Confidence:** partial
- **Answer:** Intuited `<()` helps diff tell the two args apart; claimed `$(...)` "just expands" confusingly. Missed the mechanism.

## Assistant's Evaluation
- **Result:** Fail
- **Feedback:** Both forms hand diff two args. Difference is WHAT they contain: `$(cmd)` splices output TEXT then word-splits (listings melt into one bag of names, resolved against cwd); `<(cmd)` substitutes a PIPE PATH (/dev/fd/N) so diff opens two real files and compares them. Anchor: `$( )` = TEXT (then splits); `<( )` = PATH.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-28
- **next_review:** 2026-08-31 (held 3d)
- **Last Q Type:** discriminative
- **notes:** Fail — `$( )` text-split vs `<( )` path distinction; mistake row stays active.

## Queue / Deferred Note
- **Queue position:** active (mistake, retry 2026-08-31)

## Key Takeaway
> `$()` substitutes TEXT (then word-splits); `<()` substitutes a PATH (/dev/fd/N). That is why `diff <(a) <(b)` works and `diff $(ls a) $(ls b)` does not.
