# Stage REVIEW — per-checkpoint review, aggregate, and fix

You are the **review orchestrator** (default model). The cascade (P1 → P2 → P3) is done. Your job:
run one Muse-Spark reviewer per checkpoint, collect their findings, aggregate them, **implement the
fixes**, then spawn the final E2E stage.

Read first:
- `docs/AUDIT-2026-10-08.md` (the full audit — the standard you review against)
- `AUDIT-ROADMAP.md` (what each checkpoint claims)
- `docs/roadmap/reviews/README.md` (review format + rules)
- `docs/roadmap/{P1,P2,P3}.md` (what each stage was asked to do)

## Steps

### 1. Spawn one reviewer per checkpoint
Clear any stale outputs, then spawn the four reviewers (Muse Spark):
```bash
rm -f ~/learning-pi/docs/roadmap/reviews/P0.md ~/learning-pi/docs/roadmap/reviews/P1.md \
      ~/learning-pi/docs/roadmap/reviews/P2.md ~/learning-pi/docs/roadmap/reviews/P3.md
bash ~/learning-pi/docs/roadmap/spawn-reviewer.sh P0
bash ~/learning-pi/docs/roadmap/spawn-reviewer.sh P1
bash ~/learning-pi/docs/roadmap/spawn-reviewer.sh P2
bash ~/learning-pi/docs/roadmap/spawn-reviewer.sh P3
```

### 2. Wait for all four
```bash
bash ~/learning-pi/docs/roadmap/wait-for-reviews.sh 300
```
If it prints a timeout (or your shell tool times out first), run it again until it prints
`all reviews present`. Do not proceed until all four `docs/roadmap/reviews/P{0,1,2,3}.md` exist and
are non-empty.

### 3. Aggregate
Read all four review files and write `docs/roadmap/reviews/AGGREGATED.md`:
- a deduplicated, severity-ranked master list of findings (merge duplicates across checkpoints);
- for each: where, evidence, impact, recommended fix;
- mark each as **accept / reject / defer**, with a one-line reason (reject only if the finding is
  factually wrong — say why).
Do not drop findings silently.

### 4. Implement the fixes
Implement every **accepted** finding you can do safely, following the same ground rules as the cascade
(revise door for gate/contract changes; additive; small commits; tests). Then:
```bash
cd ~/learning-pi && scripts/learn-check --no-load --with-sidecars
cd ~/learning-system && python3 -m unittest scripts.ops_test
```
If a fix cannot be made safely, leave it clearly recorded in `AGGREGATED.md` and `AUDIT-ROADMAP.md`
with the reason — do not fake a fix or claim a check passed. Record what you changed in
`AUDIT-ROADMAP.md` (a "Review phase" note) and commit/push each repo.

### 5. Spawn the final E2E stage
```bash
bash ~/learning-pi/docs/roadmap/spawn-stage.sh E2E
```
Then finish your turn with a short report: reviewers run, findings (counts by severity), fixes applied
(shas), deferrals, and the `learn-check` result.
