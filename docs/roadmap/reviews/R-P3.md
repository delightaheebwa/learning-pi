> **NOT USED — P3 is deferred.** This brief is kept for when P3 is resumed. Do not spawn it now.

# Reviewer R-P3 — review the P3 changes

You are the **P3 reviewer** on `opencode-go/muse-spark-1.3-contributor`. Follow
`docs/roadmap/reviews/README.md` for the rules and the exact findings-file format. **Review only — do
not edit code, commit, or spawn agents.** Write your findings to `docs/roadmap/reviews/P3.md`.

Read `docs/AUDIT-2026-10-08.md`, `AUDIT-ROADMAP.md` (P3 section), `docs/roadmap/P3.md`, `CONTRACT.md`,
and `contracts/learning-core.json` first.

## Scope (P3 changes only)

P3 delivered (per its brief): judge repurposed for disputes only, `viz` ROI instrumentation or
demotion, `ops.py analytics`, and the learner challenge/dispute workflow.

Find P3's changes:
```bash
git -C ~/learning-pi log --oneline --grep '(P3' ; git -C ~/learning-system log --oneline --grep '(P3'
```
If tagging is incomplete, review the current state of the files named in `docs/roadmap/P3.md` and diff
against the P2 boundary. Inspect the actual diff.

## What to check (adversarially)

- **Judge scope:** is the judge genuinely limited to disputes/tie-breaks, or does it still run on
  ordinary passes? Do the existing judge tests still pass?
- **`viz`:** if instrumented, is the attribution signal real and not a no-op? If demoted, is the
  behavior actually opt-in-only and documented?
- **`ops.py analytics`:** is the math correct (independence trend, hint debt, calibration, dimension
  mix, regressions)? Read-only? Tested?
- **Learner challenge workflow:** is it a concrete procedure with evidence, or vague prose? Does a
  corrected claim mark dependents `unverified` per the P0.6 convention?
- **General:** false claims in `AUDIT-ROADMAP.md`, missing tests, contract/implementation drift.

Run `cd ~/learning-pi && scripts/learn-check --no-load --with-sidecars` and
`cd ~/learning-system && python3 -m unittest scripts.ops_test`.

Write `docs/roadmap/reviews/P3.md` in the required format, then stop.
