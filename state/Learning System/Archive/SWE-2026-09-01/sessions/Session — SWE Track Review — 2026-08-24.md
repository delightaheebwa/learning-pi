# Session — SWE Track Review — 2026-08-24

**Track:** SWE (Shell & Terminal, MIT Missing Semester) · **Type:** spaced-repetition review, cap 5 · **Date:** 2026-08-24

## Queue & Results

| Slot | Concept | Kind | Result | Interval → Next |
| --- | --- | --- | --- | --- |
| 1 | man & Documentation | mistake retry | ✅ PASS | 7d → **14d**, next 2026-09-07 |
| 2 | find | mistake retry | ❌ FAIL (re-inverted) | held, retry **2026-08-27** |
| 3 | File Permissions (ls -l) | overdue (since 08-10) | ✅ PASS | → **14d**, next 2026-09-07 |
| 4 | PATH & Program Discovery | overdue (since 08-11) | ❌ FAIL (partial recall) | → **3d**, retry 2026-08-27 |
| 5 | Command Substitution & Arithmetic | overdue (since 08-11) | ✅ PASS | 7d → **14d**, next 2026-09-07 |

**Interleaving: 5 concepts shuffled — 2 mistake retries (priority-1) + 3 overdue reviews; 3 definitional / 2 discriminative.** Adjacency guard moot (all one Source); shuffled for type/topic spread.

## Themes

- **Quoting model re-inverted on `find`:** claimed quotes *enable* glob expansion and unquoted searches for a literal `*.zip`. Fixed with a live demo: unquoted glob expands to real filenames before find runs (`paths must precede expression: 'b.zip'`). Unifying frame given: quoting controls what bash does to your text *before* the program sees it (same coin as word-splitting).
- **Retrieval gap on PATH:** explained why `./a.out` works (explicit location) but couldn't spontaneously produce where bare-name lookup searches ($PATH directory walk, cwd deliberately absent). Name→search vs path→direct-execution distinction supplied.
- **Framing slips, sound substance:** permissions decoded correctly but chunked as "first four = owner" (char 1 is the type; 2–4/5–7/8–10 = owner/group/others); "guests" → formal term *others*.
- **Substitution vs arithmetic:** labels right immediately; subshell-runs-program vs bash-internal-math landed on the scaffolded second round.

## Advisory mastery after session

- man & Documentation 0.51 (x,v) · File Permissions 0.50 (v) · Command Substitution & Arithmetic 0.50 (v) · find 0.00 (x,x) · PATH & Program Discovery 0.00 (x)

## Surfaced

- **Feynman explain-back debt:** every concept-type item still lacks one (advisory qualitative gate) — Background Jobs, Signals, SSH, Shell Config & Dotfiles, Pipes, etc.
- **Scheduler drift (stale next_review from the 08-24 backfill):** xargs (08-18), curl (08-15), jq (08-20), Parameter Expansion (08-21), plus the whole 08-10/08-11 cohort — fold gradually into upcoming queues rather than mass-bumping.
- Deep dive offered at close; learner may pick any of today's five.
