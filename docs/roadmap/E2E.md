# Stage E2E — Final end-to-end verification

You are the **final E2E agent**. The cascade has built P0 (done) through P3. Your job is to verify the
**whole integrated system** end to end, find anything that does not actually work, fix what you safely
can, and produce a report. Read:
- `docs/AUDIT-2026-10-08.md` (the full audit and its evaluation plan §17–§18)
- `AUDIT-ROADMAP.md` (everything claimed as done — your job is to test those claims)
- `docs/roadmap/README.md`

If a stage agent left deferrals or claimed something it did not do, record it as a finding.

## 1. Static / offline suites (must pass)
```bash
cd ~/learning-pi && scripts/learn-check --no-load --with-sidecars
cd ~/learning-system && python3 -m unittest scripts.ops_test
python3 scripts/wiki_provenance.py --check
python3 ~/learning-pi/pi/audit_state.py --root ~/learning-system
```
Record exact exit codes and output tails.

## 2. Targeted feature verification (the P0/P1/P2/P3 claims)
Exercise each and record PASS/FAIL with the command or test name:
- Gate hard-fact completeness (`CLAIMS_INCOMPLETE`) and tail bound (`G-draft-tail-bound`).
- Always-on claim-level ledger (`~/.pi/agent/learning-gate/receipts.ndjson` has `claims[]` + `envelopeHash`).
- `/solo`: `[[FLOW:solo]]` withholds claims/viz (`SOLO_NO_TEACHING`/`SOLO_NO_AIDS`) and allows the quiz batch.
- Mastery dimensions + independence gate: `python3 scripts/ops.py mastery --json`; a failed `mode=solo` blocks `solid`.
- `q_type` enum + deterministic MCQ grading (P1.2) if present.
- Prerequisite refusal over a `fuzzy` prereq (P1.3) if present.
- Confidence calibration report (P1.4) if present.
- Wiki provenance: every page carries a marker; trust order documented.
- Any seeded-error red-team harness (P1.8).
Run the actual test suites that cover each; do not just re-read the code.

## 3. Live journey (if the environment supports it)
If a judge/model is configured and real-model e2e is acceptable, run the sandboxed journeys:
```bash
cd ~/learning-pi && scripts/learn-check --e2e --e2e-tier smoke
```
If keys/models are unavailable, **do not fake it** — run the offline load probe instead
(`scripts/learn-check --no-load` plus the load probe if a sandbox can be built) and say clearly in the
report that the live journey was skipped and why. Do not claim a live test you did not run.

## 4. Integration / drift checks
- `git -C ~/learning-pi status --short` and `git -C ~/learning-system status --short` are clean.
- Both repos are pushed (`git log --oneline -1` in each).
- `contracts/learning-core.json` invariants all have passing tests (learn-check covers this).
- The `learning-pi` copy and `learning-system` copies of shared skills have no *unintended* drift
  beyond the documented canonicalization (P2.4).

## 5. Report
Write `docs/roadmap/E2E-REPORT.md` with:
- Environment (date, repos, commit shas, whether a live model path ran).
- A results table: check → command → result → evidence/notes.
- Findings: every failure or false claim, with severity.
- Fixes you made (with shas) and anything left unfixed with a recommended next step.
- A one-paragraph honest verdict: does the integrated system do what the audit roadmap claims?

Then commit and push the report (and any fixes). There is **no next stage** — you are the end of the
cascade. If you found serious failures, say so plainly; do not paper over them.
