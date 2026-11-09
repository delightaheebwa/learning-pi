# REVIEW: Job Control (Ctrl-Z, fg/bg, nohup/disown) — 2026-08-21

## Review Info
- **Date:** 2026-08-21
- **Concept:** Job Control (Ctrl-Z, fg/bg, nohup/disown)
- **Last Reviewed:** 2026-08-18
- **Review Interval:** 3d (due)
- **Status Before Review:** developing

## Assistant's Prompt
> Definitional (alternation from last discriminative): When a backgrounded job's parent terminal closes, the job dies from SIGHUP — what are the two different ways to prevent that, and which one is used *before* vs. *after* the job starts? Give the exact pattern for each. Follow-up: why does `disown` need the `%job-number` reference syntax when `nohup` does not?

## Your Answer
- **Confidence:** confident
- **Answer:** nohup (before) and disown (after). Pattern: nohup runs *up front* (before the job exists) — you give it the command and background it yourself (`nohup myjob &`), so nohup is a wrapper that detaches the job from HUP from the start. disown is used *after* the job is already running in the background; the job already has a slot in the shell's job table, so you reference that existing slot by number — `disown %1` — rather than rewriting the command. `%1`/`%2` are the shell's job references.

## Assistant's Evaluation
- **Result:** Pass
- **Feedback:** Core insight correct — the mechanism, not just the memorized pattern: nohup is a wrapper used *before* the job exists (command + background `&`), disown references an *already-existing* job-table slot by `%<job-number>` afterward. `disown <cmd>` as a pattern is misleading — you write `disown %<job-number>` because the command no longer identifies the job; the job-table number does.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-21
- **next_review:** 2026-08-28 (advanced 3d → 7d)
- **Last Q Type:** definitional
- **notes:** Pass — nailed why disown uses %job-number vs nohup takes the command.

## Key Takeaway
> `nohup cmd &` is a wrapper used **before** the job exists; `disown %n` references an **already-running** job's slot in the job table.
