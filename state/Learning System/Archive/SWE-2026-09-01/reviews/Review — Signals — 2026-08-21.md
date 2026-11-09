# REVIEW: Signals (Software Interrupts) — 2026-08-21

## Review Info
- **Date:** 2026-08-21
- **Concept:** Signals (Software Interrupts)
- **Last Reviewed:** 2026-08-18
- **Review Interval:** 3d (due)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative (alternation from last definitional): Someone says "just `kill -9` it, that always works." Why should SIGKILL be a *last resort*, not the default? Name the three-signal escalation ladder, what each does, and the specific danger of skipping straight to `kill -9` — what does it do to a process that SIGTERM wouldn't?

## Your Answer
- **Confidence:** confident
- **Answer:** kill -9 terminates the process immediately without time to clean up, leaving anything it was handling hanging. Ladder: (1) SIGINT — polite ask, the process can choose to react, ignore it, or continue. (2) SIGTERM — tells the process it's time to end but gives it time to clean up. (3) SIGKILL — terminates immediately, no grace.

## Assistant's Evaluation
- **Result:** Pass
- **Feedback:** Full ladder + the *why* correct — SIGKILL skips cleanup: no chance to save state, flush buffers, release locks/close files; can orphan children and corrupt shared state. Refinement to sharpen: the key contrast is **catchability** — SIGINT and SIGTERM are both *catchable* (the process can intercept and run a cleanup handler), whereas SIGKILL is *uncatchable* — the kernel enforces it, no handler, no `try/finally`.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-21
- **next_review:** 2026-08-28 (advanced 3d → 7d)
- **Last Q Type:** discriminative
- **notes:** Pass — full ladder + why kill -9 skips cleanup; refined: SIGINT/SIGTERM catchable, SIGKILL UNcatchable.

## Key Takeaway
> SIGINT & SIGTERM are **catchable** (graceful cleanup possible); SIGKILL is **uncatchable** — immediate termination, no cleanup. That's why `kill -9` is a last resort.
