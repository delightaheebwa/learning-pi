# REVIEW: Environment Variables (Shell) — 2026-08-27

## Review Info
- **Date:** 2026-08-27
- **Concept:** Environment Variables (Shell)
- **Last Reviewed:** 2026-08-24
- **Review Interval:** 3d (interval_index 0, due)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative: `TZ=Asia/Tokyo date` prints Tokyo time but `echo $TZ` afterward is empty, while `export DEBUG=1` makes `bash -c 'echo $DEBUG'` print 1. What single rule explains both — what does a child process actually receive?

## Your Answer
- **Confidence:** confident
- **Answer:** `export` sends the value to the child; without it the child doesn't get it — so the first shows empty, the second shows something.

## Assistant's Evaluation
- **Result:** Pass
- **Feedback:** Correct on the load-bearing half. Refinement: `TZ=Asia/Tokyo date` DOES deliver TZ to that one child (that's why `date` prints Tokyo time) — it just isn't stored in the shell's persistent env bag, so `echo $TZ` after is empty. Rule: a child inherits only the exported environment; a `VAR=val cmd` prefix reaches that one command and isn't saved; `export VAR=val` writes into the shell's env so every future child gets it.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing
- **last_reviewed:** 2026-08-27
- **next_review:** 2026-09-03 (interval 0 → 1, 7d)
- **Last Q Type:** discriminative

## Key Takeaway
> A child inherits only the exported environment. `VAR=val cmd` reaches one command (not saved); `export VAR=val` persists into the shell's env for all future children.
