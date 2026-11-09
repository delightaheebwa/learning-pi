# Session — SWE Track Review — 2026-08-28

- **Track:** SWE (Stage 0 — Fluency & Tools)
- **Date:** 2026-08-28
- **Type:** Spaced-repetition review (5 slots)
- **Interleaving:** 5 concepts shuffled, 2 discriminative / 3 definitional; source-adjacency guard applied (Signals sits between find and Shebang to break the course-shell run; Process Substitution from shell-tools, grep from course-shell; Make cluster excluded per 2026-08-25 backlog note).

## Queue
- **Priority-1 mistakes due:** NONE. Earliest active mistake retry is fd (2026-08-29); find / Built-ins / Process Substitution / Shebang / Vim rows all retry 2026-08-31 per 🧯 Mistakes.md. So all 5 slots = due reviews (Attempts.json next_review ≤ 2026-08-28).
- **Due reviews taken (5 of 9 due; Make cluster + fd / tmux / Vim excluded):** find · Signals (Software Interrupts) · Shebang & Script Execution · Process Substitution · grep.

## Results (2 pass / 3 fail)
- **find PASS** (discriminative) — unquoted `*.zip` glob-expands to cwd matches before find runs; quoting keeps the pattern for find. First clean recall after three inverted fails. Advanced 3d → 7d (next 2026-09-04). Mistake row → review (1 correct recall; graduates on next).
- **Signals (Software Interrupts) PASS** (definitional) — SIGTERM catchable/graceful vs SIGKILL uncatchable/skips cleanup; kill -9 last resort. Advanced 7d → 30d (next 2026-09-27).
- **Shebang & Script Execution FAIL** (discriminative) — route split still missing: `./run.sh` = kernel executes file (needs x; #! = interpreter path) vs `bash run.sh` = bash reads file (needs r; #! just a comment). Mistake row stays active (retry 2026-08-31).
- **Process Substitution FAIL** (discriminative) — `$( )` substitutes TEXT (then word-splits, listings melt) vs `<( )` substitutes a PIPE PATH (/dev/fd/N). Mistake row stays active (retry 2026-08-31).
- **grep FAIL** (definitional) — regex `*` repeats the PREVIOUS char (zero-or-more), not glob's "any characters" (that is `.`; "one-or-more" is `+`). New mistake row (retry 2026-08-31).

## Housekeeping / flags
- **find mistake row** → review (1 correct recall); Next Retry 2026-08-31 → 2026-09-08.
- **grep:** new 🧯 Mistakes.md row (error_type application — knew glob, misapplied regex `*`).
- **Feynman explain-back debt:** concept items (Signals, Process Substitution, Pipes, Bash Quoting, etc.) still lack a Feynman pass (advisory). Only Shell Redirections & Streams + Shell Built-ins have Feynman:pass.
- **Gate (review):** not run — terminal API key 401 blocker still open (see 2026-08-24 + 08-27 logs). Verify the 5 review notes manually.
- **Note discrepancy:** the 2026-08-27 session note listed find / Built-ins / Process Substitution / Shebang / fd as "due 2026-08-28", but 🧯 Mistakes.md lists them at 2026-08-31 (fd at 08-29). File is source of truth; none were actually priority-1-due today.

## Writes
- Active Concepts 5 rows synced (last_reviewed / next_review / Last Q Type).
- Reviews/ — 5 per-concept notes.
- Attempts.json — 5 records (find → interval 1; Signals → interval 3; Shebang / Process Substitution / grep held at interval 0).
- 🧯 Mistakes.md — find → review (1), +grep row.
- Consistency check pending.
