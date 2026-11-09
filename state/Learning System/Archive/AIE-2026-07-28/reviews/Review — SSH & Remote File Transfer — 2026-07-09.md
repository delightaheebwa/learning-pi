# Review — SSH & Remote File Transfer

**Date:** 2026-07-09
**Concept:** SSH & Remote File Transfer
**Track:** AI Engineering (aie)

## Question
For syncing an existing model directory to a remote GPU box — scp or rsync, and why?

## Response
rsync. Because after the first upload, it only tracks and uploads what changed hence in this scenario the process is much faster than using scp.

## Evaluation
**Correct.** Clear distinction: rsync = delta-only sync for updates; scp = full transfer better for initial upload. Solid understanding.

## Outcome
- **Status:** developing → developing
- **Interval:** 7d → 14d
- **Next Review:** 2026-07-23
