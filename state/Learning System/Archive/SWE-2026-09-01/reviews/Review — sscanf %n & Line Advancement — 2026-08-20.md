# REVIEW: sscanf %n & Line Advancement — 2026-08-20

## Review Info
- **Date:** 2026-08-20
- **Concept:** sscanf %n & Line Advancement
- **Last Reviewed:** 2026-08-17
- **Review Interval:** 3d (due)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative (alternation from last definitional): Two fixes — A) advance by `%n` bytes, B) advance by whole line (`strtok_r`/`fgets`). Which is fundamentally safer for line-based parsing, what does `%n` not guarantee, and what silent failure happens advancing by `%n`?

## Your Answer
- **Confidence:** confident
- **Answer:** Fix B (whole-line). Fix A stops at the first non-digit so part of the previous line leaks/ignored; Fix B guarantees consuming all characters in the line before advancing.

## Assistant's Evaluation
- **Result:** Pass
- **Feedback:** Correct 20% insight. `%n` reports bytes where the pattern matched; `%lu` stops at first non-digit, so `line += n` leaves `" kB"` behind and the whitespace-skip loop stalls at `'k'`; next sscanf "succeeds" on the shifted garbage, silently eating a line. Fix B (whole-line) never rescan mid-line debris. Nuance: `%n` works safely only if the format matches the ENTIRE line (incl. trailing `kB`); otherwise whole-line advancement is the robust choice.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-20
- **next_review:** 2026-08-27 (advanced 3d → 7d)
- **Last Q Type:** discriminative
- **notes:** Pass — whole-line advancement safest; `%n` partial-match drift.

## Queue / Deferred Note
- **Queue position:** active

## Key Takeaway
> For line-based parsing, advance by whole lines; `%n` only reflects where the (possibly partial) format matched.
