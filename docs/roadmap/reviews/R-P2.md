# Reviewer R-P2 — review the P2 changes

You are the **P2 reviewer** on `opencode-go/muse-spark-1.3-contributor`. Follow
`docs/roadmap/reviews/README.md` for the rules and the exact findings-file format. **Review only — do
not edit code, commit, or spawn agents.** Write your findings to `docs/roadmap/reviews/P2.md`.

Read `docs/AUDIT-2026-10-08.md`, `AUDIT-ROADMAP.md` (P2 section), `docs/roadmap/P2.md`, `CONTRACT.md`,
and `contracts/learning-core.json` first.

## Scope (P2 changes only)

P2 delivered (per its brief): blocking state audit on errors (content vs state gate), removal/whitelist
of the out-of-scope ISSUES demotion, Scout TTL enforcement, declaring pi canonical / freezing the
OpenWebUI path, `ops.py amend`, resolving prompt contradictions, light procedural interleaving, and
misconception→prereq links.

Find P2's changes:
```bash
git -C ~/learning-pi log --oneline --grep '(P2' ; git -C ~/learning-system log --oneline --grep '(P2'
```
If tagging is incomplete, review the current state of the files named in `docs/roadmap/P2.md` and diff
against the P1 boundary. Inspect the actual diff.

## What to check (adversarially)

- **State gate:** does a state-audit **error** actually block the ingest/review close, while warnings
  stay non-blocking? Could this create a dead-end (the exact failure mode the gate historically
  avoids)? Is the contract updated and tested?
- **Out-of-scope demotion:** is the demotion truly removed or strictly whitelisted? Try to construct a
  content finding that gets wrongly demoted.
- **Scout TTL:** is stale-digest teaching actually prevented, or only warned?
- **pi canonical / OpenWebUI freeze:** are the banners accurate? Is `audit_openwebui.py` drift
  explained rather than hidden?
- **`ops.py amend`:** does it validate input and persist correctly? Does it replace the `.tmp` surgery
  without corrupting `Attempts.json`?
- **Prompt contradictions:** are they actually resolved (grep), or did a new contradiction appear?
- **Interleaving / misconception links:** any regression to the one-idea mini-checkpoint rule?
- **General:** false claims in `AUDIT-ROADMAP.md`, missing tests, contract/implementation drift.

Run `cd ~/learning-pi && scripts/learn-check --no-load --with-sidecars` and
`cd ~/learning-system && python3 -m unittest scripts.ops_test`.

Write `docs/roadmap/reviews/P2.md` in the required format, then stop.
