# Session — CLI Environment Batch 2 Ingest — 2026-08-24

**Track:** SWE · **Type:** Ingest (batch 2 of Lecture 2 website notes; batch 1 was 2026-08-23)
**Source:** Furnished transcription of handwritten Lecture 2 notes — Fri 2026-08-21 (shell args recap, process substitution & env vars, exit codes & SSH auth, file transfer tools & ssh config) + Sat 2026-08-22 (tmux, dotfiles, startup modes, curl|bash security, aliases).

## Actions

| Concept | Action | Status | last_reviewed | next_review |
|---|---|---|---|---|
| Environment Variables (Shell) | NEW page + row | developing | 2026-08-24 | 2026-08-27 |
| Exit Codes & Short-Circuit Control Flow | NEW page + row | developing | 2026-08-24 | 2026-08-28 |
| tmux — Sessions, Windows & Panes | NEW page + row | developing | 2026-08-24 | 2026-08-29 |
| File Transfers over SSH — scp, rsync & ssh_config | NEW page + row | developing | 2026-08-24 | 2026-08-30 |
| SSH: Public-Key Auth & Remote Commands | ENRICHED (row + page: ~/.ssh/config; noted recurring encrypt-challenge error) | developing | 2026-08-24 | 2026-08-27 (held 3d) |
| curl (Web Fetching) | ENRICHED (row + Shell page: `curl \| bash` hazard) | developing | 2026-08-24 | 2026-08-31 (was overdue 08-15; held 7d, ladder not advanced — no live recall) |
| Shell Config & Dotfiles | ENRICHED (row + page: login × interactive startup-mode table) | developing | 2026-08-24 | 2026-08-31 (was overdue 08-22; held 7d) |

## Skipped as duplicates (already ingested 2026-08-23)
Positional/special params (`$0/$1–$9/$@/$#`), process substitution `<(CMD)` (incl. the notes' recurring false "captures into a variable" claim), untyped-variable model, SSH key-based handshake (wiki already carries the corrected sign/verify model; notes repeat the encrypt-with-public-key framing).

## Corrections applied to source claims
- "rsync builds on scp" → rsync independently improves on scp (MIT wording).
- Non-login shells "load the profile flow" → inverted for bash; corrected table in dotfiles page.
- Aliases can't take mid-command arguments → kept (standard bash behavior; functions required for parameterized logic).

## Verification
`fact_check` (muse-spark-1.2-contributor) returned HTTP 500 throughout; load-bearing claims verified directly against live MIT pages (2020/command-line, 2020/security) instead.

## Review gate
Blocked at pass 1: review_gate.py ran from the terminal against http://host.docker.internal:3000 (reachable), but the stored Open WebUI API key was rejected (HTTP 401, expired/invalid token). No independent minimax/mimo verdict for this batch — re-run once the key is regenerated.

## Open questions
- None new. Standing: deepen tmux (starter page) during Command-line Environment lessons.

Interleaving: n/a (ingest, not review) — 4 new definitional seeds staggered 2026-08-27 → 2026-08-30.
