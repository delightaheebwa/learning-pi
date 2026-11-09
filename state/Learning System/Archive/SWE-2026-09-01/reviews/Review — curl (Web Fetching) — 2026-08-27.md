# REVIEW: curl (Web Fetching) — 2026-08-27

## Review Info
- **Date:** 2026-08-27
- **Concept:** curl (Web Fetching)
- **Last Reviewed:** 2026-08-08
- **Review Interval:** 7d (interval_index 1, due)
- **Status Before Review:** developing

## Assistant's Prompt
> Definitional: Install docs often show `curl -fsSL URL | sh`. What's the #1 safety rule about piping curl straight into a shell interpreter, and what's the safe 3-step alternative?

## Your Answer
- **Confidence:** confident
- **Answer:** Piping into sh runs unaudited code with your privileges — a malicious script executes before you can review it. Safer: download, inspect, then run.

## Assistant's Evaluation
- **Result:** Pass
- **Feedback:** Correct model. The safe 3-step: `curl -fsSL URL -o install.sh` (download only) → `less install.sh` (inspect) → `bash install.sh` (run after reading). The `bash -c "$(curl ...)"` variant is still blind execution — inspection is the safety step regardless.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing
- **last_reviewed:** 2026-08-27
- **next_review:** 2026-09-10 (interval 1 → 2, 14d)
- **Last Q Type:** definitional

## Key Takeaway
> Never pipe curl straight into a shell — it runs unaudited code with your privileges. Download → inspect → run instead.
