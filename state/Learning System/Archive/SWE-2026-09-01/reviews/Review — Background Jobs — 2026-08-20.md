# REVIEW: Background Jobs — 2026-08-20

## Review Info
- **Date:** 2026-08-20
- **Concept:** Background Jobs
- **Last Reviewed:** 2026-08-08
- **Review Interval:** Overdue (due 08-11)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative (alternation from last definitional): Run `sleep 300 &` then close the terminal window. What likely happens to the process and why? Then the two escape routes (one before, one after) and what makes each work.

## Your Answer
- **Confidence:** confident
- **Answer:** Backgrounded process is killed when terminal closes because it's still a child of the shell, which sends SIGHUP to all children. Escape routes: `nohup` from the start or `disown` after.

## Assistant's Evaluation
- **Result:** Pass
- **Feedback:** Clean pass — full mechanism correct: `&` backgrounds but the job stays a child of the terminal's shell; closing sends SIGHUP → kills children. `nohup` (before) makes the process ignore HUP; `disown` (after) detaches the job from the shell's job table. Nuance: two distinct mechanisms — nohup makes the process ignore the signal, disown removes ownership — both achieve survival.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-20
- **next_review:** 2026-08-27 (advanced to 7d)
- **Last Q Type:** discriminative
- **notes:** Pass — bg job still child of shell → SIGHUP on close; nohup before / disown after.

## Queue / Deferred Note
- **Queue position:** active

## Key Takeaway
> A backgrounded job is still a child of the terminal's shell — closing it SIGHUPs the job; escape with `nohup` (signal-ignore) or `disown` (detach).
