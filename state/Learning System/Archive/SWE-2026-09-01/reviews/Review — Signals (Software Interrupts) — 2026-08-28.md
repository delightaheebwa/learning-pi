# REVIEW: Signals (Software Interrupts) — 2026-08-28

## Review Info
- **Date:** 2026-08-28
- **Concept:** Signals (Software Interrupts)
- **Last Reviewed:** 2026-08-21
- **Review Interval:** 7d (due)
- **Status Before Review:** developing

## Assistant's Prompt
> Definitional (alternation from last discriminative): What is the difference between SIGTERM and SIGKILL, and why is `kill -9` always the last resort?

## Your Answer
- **Confidence:** confident
- **Answer:** SIGTERM is catchable and lets the process clean up gracefully; SIGKILL is uncatchable and kills immediately, skipping cleanup (may orphan children / leave temp junk). Hence -9 is last resort.

## Assistant's Evaluation
- **Result:** Pass
- **Feedback:** Correct kill ladder: SIGINT → SIGTERM (catchable, graceful) → SIGKILL (uncatchable, immediate). Explains why Ctrl-C sometimes fails and why -9 is final.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-28
- **next_review:** 2026-09-27 (advanced 7d → 30d)
- **Last Q Type:** definitional
- **notes:** Pass — SIGTERM catchable/graceful vs SIGKILL uncatchable/skips cleanup.

## Queue / Deferred Note
- **Queue position:** active

## Key Takeaway
> SIGTERM lets a process clean up; SIGKILL cannot be caught and skips cleanup — that is why `kill -9` is last resort.
