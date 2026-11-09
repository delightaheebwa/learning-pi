# Session — SSH & Pipeline Parallelism Ingest — 2026-08-18

- **Date:** 2026-08-18
- **Topic:** SSH public-key auth + running commands on remote machines; pipeline-stage parallelism; only-a-few-signals-in-practice; `VAR=val cmd` env prefix & `bash -c` check
- **Type:** Ingest (1 new concept + 2 enrichments) — from MIT Missing Semester YouTube (Shell/Command-line Environment lecture)
- **Source:** https://missing.csail.mit.edu/2026/command-line-environment/
- **Concepts added (1 new, SWE track, `developing`):**
  - **SSH: Public-Key Auth & Remote Commands** — public key = shareable (server uses it to *verify* you), private key = your secret, equivalent to a password, never share it. `ssh host cmd` runs a command on the remote machine with stdout streaming back over the connection. Quoting decides where a pipe runs: `ssh host ls | wc -l` runs `ls` remotely and counts locally; `ssh host 'ls | wc -l'` sends the *whole* pipeline to run remotely (only the result crosses the wire — run the expensive stages on the side where the data is). `last_reviewed` 2026-08-18, `next_review` 2026-08-21 (+3d), `Last Q Type` definitional
- **Concepts enriched (2, SWE track):**
  - **Pipes (`|`) & Pipeline Composition** — pipeline stages run in **parallel**, not sequentially: all commands start at once and stream line-by-line (as one writes, the next consumes instantly; `grep | head` stops early once `head` has enough). `last_reviewed` 2026-08-18, `next_review` 2026-09-01 (7d→14d)
  - **Signals (Software Interrupts)** — in practice you use only a handful of the ~30 signals (SIGINT/Ctrl-C, SIGTERM, SIGKILL, SIGTSTP, SIGHUP, SIGPIPE); know the common set, not the whole list. `last_reviewed` 2026-08-18
- **Wiki pages (1 created, 2 enriched):** [[SSH — Public-Key Auth & Remote Commands]] (new); enriched [[MIT Missing Semester — Shell]] (pipe parallelism + local-vs-remote pipe placement) and [[MIT Missing Semester — Command-line Environment]] (per-command `VAR=val cmd` prefix, `bash -c` to inspect a variable, few-signals-in-practice note, SSH section links the dedicated page). index.md + log.md updated.
- **Key insights ingested:**
  - The public key is for *others to verify you*; the private key is the secret — the server never needs it.
  - Quoting is the switch that decides on which machine a pipeline's stages run — a one-token change (add/remove quotes) moves the computation.
  - Pipes are parallel, not sequential: streaming is why they're fast and why `head` can cut off upstream work.
  - `VAR=val cmd` sets a variable for a single command without exporting it; `bash -c 'echo $VAR'` spawns an isolated shell to inspect it.
  - Of ~30 signals, everyday work touches maybe six.
- **Verification:** learning-review gate **PASS** (verdict JSON saved to `Reviews/Quality Gates/`; model `minimax-m3`). **Factual gate passed** — public/private key semantics, `ssh host 'ls | wc -l'` quote behavior, and pipeline parallelism are standard, well-established systems facts.
- **Open questions:** none new
