# Session — SWE Track Review — 2026-08-25

- **Track:** swe · **Format:** spaced repetition, 5 slots (2 priority-1 mistake retries + 3 due reviews)
- **Pre-session anomaly:** repo had uncommitted edits from an interrupted earlier session today (Attempts.json: Bash Quoting + Wildcards & Globs passes; Mistakes.md: new Shell Built-ins row) — no Active-Concepts sync, no note, no commit. Folded into this session's persistence pass. Built-ins retry (08-28) and Wildcards (passed) were not re-queued.

## Results

| # | Concept | Q Type | Result | New schedule |
| --- | --- | --- | --- | --- |
| 1 | find (glob-quoting mistake) | definitional | ❌ FAIL (3rd) | retry 2026-08-28 |
| 2 | Bash Quoting (mistake) | discriminative | ✅ PASS | 2026-09-24 (30d) |
| 3 | Shell Redirections & Streams | definitional | ✅ PASS · Feynman ✓ | 2026-09-08 (14d) |
| 4 | SSH: Public-Key Auth & Remote Commands | discriminative | ✅ PASS (4th straight, mastery 1.00) | 2026-09-08 (14d) |
| 5 | Process Substitution | discriminative | ❌ FAIL | retry 2026-08-28 |

Interleaving: 5 concepts shuffled, 3 discriminative / 2 definitional (single source MIT Missing Semester — adjacency guard unsatisfiable).

## Coaching notes

- **find:** third inversion of the glob-quoting model even after a slow trace. Fact is memorized; the execution movie (who rewrites what, and when) still runs backwards under pressure. Plan for 08-28: learner traces an example aloud step-by-step instead of recalling the rule.
- **Bash Quoting:** discriminative format unlocked it — ANSI-C "escapes-only" stuck. Mistake → review (1 correct recall; graduates on the next).
- **SSH:** quote-decides-where-the-pipe-runs is automatic. Bonus refined: push computation to where the data lives — quoted pipeline ships a few bytes (the count); unquoted ships the whole listing, and a dropped connection makes local `wc` silently undercount.
- **Process Substitution:** conflated $() text-splice (then word-split) with <() path-substitution; wrapped both commands in one <() → bash tried to execute filenames → empty pipes → false "no differences". Anchor taught: "$() substitutes text, <() substitutes a path."

## Surfaced

- Scheduler-drift cohort still pending (fd, jq, curl, Parameter Expansion, Shebang, Git-commit conventions, Make cluster) — fold into upcoming queues.
- Data bug: Attempts.json `xargs.last_reviewed` holds corrupted value "`) & Pipeline Composition" (string spill from the Pipes key) — needs repair.
- Feynman explain-back: Redirections ✓ cleared today; remaining concept-type items still owe explain-backs.

## Gap-fill round (same day, learner-requested continuation)

Hypothetical: had the morning's 3 passes committed earlier, these 3 would have filled the queue — pulled from the scheduler-drift backlog.

| # | Concept | Q Type | Result | New schedule |
| --- | --- | --- | --- | --- |
| 6 | sed (Stream Editor) · mistake retry #1 | definitional | ✅ PASS — mistake → review | 2026-09-08 |
| 7 | Shebang & Script Execution | definitional | ❌ FAIL — two-route model missing | retry 2026-08-28 |
| 8 | Git commit message conventions | discriminative | ✅ PASS | 2026-09-08 |

Interleaving: 3 concepts, 2 definitional / 1 discriminative.

### Coaching notes (gap-fill)

- **sed:** /g semantics finally articulated correctly ('all occurrences IN THE LINE'). One more correct recall graduates the mistake.
- **Shebang:** structural gap — didn't separate kernel-executes-file (./script: x bit, shebang = interpreter path) from bash-reads-file (bash script: r suffices, shebang = comment). Correction logged; retry 08-28 alongside find + Process Substitution + Shell Built-ins (busy mistake day).
- **Git conventions:** recognition solid; nudged from specificity to machine-scannability + imperative mood. Still owes an applied check (writing his own subject line) at next review.

Backlog remaining after this round: jq, curl, fd, Parameter Expansion, xargs, Shell Built-ins & Process Isolation (+ Make cluster, deprioritized with C-project archive).
