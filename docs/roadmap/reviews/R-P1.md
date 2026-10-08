# Reviewer R-P1 — review the P1 changes

You are the **P1 reviewer** on `opencode-go/muse-spark-1.3-contributor`. Follow
`docs/roadmap/reviews/README.md` for the rules and the exact findings-file format. **Review only — do
not edit code, commit, or spawn agents.** Write your findings to `docs/roadmap/reviews/P1.md`.

Read `docs/AUDIT-2026-10-08.md`, `AUDIT-ROADMAP.md` (P1 section), `docs/roadmap/P1.md`, `CONTRACT.md`,
and `contracts/learning-core.json` first.

## Scope (P1 changes only)

P1 delivered (per its brief): mandatory Feynman/teach-back, deterministic MCQ grading + `q_type` enum,
prerequisite edges + refusal, confidence calibration, transfer dimension/far transfer, withholding
unverified hard-fact claims, learner-authored wiki sections, the seeded-error red-team harness, and
fading hint budgets.

Find P1's changes:
```bash
git -C ~/learning-pi log --oneline --grep '(P1' ; git -C ~/learning-system log --oneline --grep '(P1'
```
If tagging is incomplete, review the current state of the files named in `docs/roadmap/P1.md` and use
`git log -p` around the P0 baseline (`learning-pi e344abc`, `learning-system 64893fe`) to see what
changed. Inspect the actual diff, not just the summary.

## What to check (adversarially)

- **Feynman gate:** is explain-back actually required for `concept`/`design` in reviews, or only
  documented? Can a concept still reach `solid` without it?
- **Deterministic MCQ + `q_type` enum:** is the enum enforced (unknown rejected) without breaking
  existing stored attempts? Is the deterministic grader correct (mixed correct/incorrect letters,
  out-of-range, missing answers)?
- **Prerequisites:** does a `fuzzy` prereq actually block advancement, or only warn? Any false blocks
  when prereq data is missing?
- **Confidence calibration:** is `--confidence` actually recorded on graded attempts end to end? Is the
  calibration math correct?
- **Transfer / far transfer:** is a far-transfer item actually scheduled, and is the dimension fed by
  the right `q_type` values?
- **Withhold unverified hard facts:** does the retry cap now withhold hard-fact claims content (not
  render it)? Does it regress non-hard-fact turns? Contract invariant + tests present?
- **Red-team harness:** does it actually run in `learn-check`, and does it genuinely catch seeded
  errors (not a no-op)?
- **General:** false claims in `AUDIT-ROADMAP.md`, missing tests, contract/implementation drift,
  regressions to P0 behavior.

Run `cd ~/learning-pi && scripts/learn-check --no-load --with-sidecars` and
`cd ~/learning-system && python3 -m unittest scripts.ops_test`, plus any new tests P1 added.

Write `docs/roadmap/reviews/P1.md` in the required format, then stop.
