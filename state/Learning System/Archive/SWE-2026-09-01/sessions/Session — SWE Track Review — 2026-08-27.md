# Session — SWE Track Review — 2026-08-27

- **Track:** SWE (Stage 0 — Fluency & Tools)
- **Date:** 2026-08-27
- **Type:** Spaced-repetition review (5 slots)
- **Interleaving:** 5 concepts shuffled, 2 discriminative / 3 definitional; source-adjacency guard applied (Env Variables moved before curl to break the course-shell run; Make cluster excluded per 2026-08-25 backlog note).

## Queue
- **Priority-1 mistakes due:** NONE. All `active` mistakes (find, Shell Built-ins, Process Substitution, Shebang, fd) retry 2026-08-28; `review` rows are all September. So all 5 slots = due reviews.
- **Due reviews taken (5 of 8 due, Make cluster excluded):** xargs · Environment Variables (Shell) · curl (Web Fetching) · Parameter Expansion · less (Pager).

## Results (3 pass / 2 fail)
- **Environment Variables (Shell) PASS** (discriminative) — export reaches children; refined: `VAR=val cmd` reaches one child but isn't saved. Advanced 3d → 7d (next 2026-09-03).
- **curl (Web Fetching) PASS** (definitional) — curl|sh = unaudited code; download→inspect→run. Advanced 7d → 14d (next 2026-09-10).
- **less (Pager) PASS** (discriminative) — lazy reading, no full in-memory load. First review (row seeded into Attempts.json this session); advanced 7d → 14d (next 2026-09-03).
- **xargs FAIL** (discriminative) — reached for `-0` but placed it on find; missed NUL as the guarantee. New attempt; retry 2026-08-30.
- **Parameter Expansion FAIL** (definitional) — guessed `##!.txt` "adds" extension; correction: expansion only removes, `${FILE##*/}`=basename. New attempt; retry 2026-08-30.

## Housekeeping / flags
- **less (Pager) Attempts.json seed:** the row was ingested 2026-08-24 but never seeded into Attempts.json (ingest's attempt-record step missed). Seeded memory-type row (interval_idx 2, next 2026-08-27) before recording the pass this session.
- **5 active mistakes due TOMORROW 2026-08-28:** find (glob-quoting, 3rd retry), Shell Built-ins & Process Isolation, Process Substitution, Shebang & Script Execution, fd. Strong candidates for the 2026-08-28 session.
- **Feynman explain-back debt:** all concept items still lack a Feynman pass (advisory). `Shell Redirections & Streams` is the only Feynman:pass so far.
- **Gate (review):** not run — terminal API key 401 blocker still open (see 2026-08-24 log). Verify the 5 review notes manually.

## Writes
- Active Concepts 5 rows synced (last_reviewed/next_review/Last Q Type).
- Reviews/ — 5 per-concept notes.
- Attempts.json — 5 records (less seeded then recorded).
- Consistency check passed (touched rows re-grepped).
