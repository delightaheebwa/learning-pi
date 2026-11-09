# Session — SWE Track Review — 2026-08-29

- Date: 2026-08-29
- Track: SWE (Shell & Terminal / Command-line Environment)
- Flow: Review (5-slot cap)
- Interleaving: 5 concepts shuffled, 2 discriminative / 3 definitional; adjacency guard relaxed for slots 1–2 (priority-1 mistakes share course-shell source).

## Queue
1. fd (mistake retry, due 08-29) — FAIL
2. Shebang & Script Execution (mistake, technically due 08-31 — pulled 2d early) — FAIL
3. tmux — Sessions, Windows & Panes (due 08-29) — PASS
4. Job Control (Ctrl-Z, fg/bg, nohup/disown) (due 08-28) — PASS
5. PATH & Program Discovery (due 08-27) — FAIL

## Results: 3 pass / 2 fail
- PASS: tmux (memory, idx→4, 2026-09-12) · Job Control (procedure, idx→2, 2026-09-12)
- FAIL: fd (memory, idx→1, retry 2026-08-30) · Shebang (procedure, stays active, retry 2026-09-01) · PATH & Program Discovery (concept, new mistake, retry 2026-09-01)

## Mistakes ledger
- fd: existing row updated — retry pushed 2026-08-29 → 2026-08-30; self-attribution deepened.
- PATH & Program Discovery: NEW row (structural; cwd not on PATH).
- Shebang: stays `active`, retries 0 (kernel-vs-shell route still tangled).

## Observations
- Structural-debt cluster: Shebang, Process Substitution, Shell Built-ins, PATH all hinge on the kernel-vs-shell / child-vs-parent execution model. Recommended deep-dive.
- Feynman explain-back debt remains on all concept/memory items (advisory mode; not blocking).
- Tooling note: `ops.py attempt` and `ops.py mastery` are NOT registered in this repo's ops.py (only state/bundle/apply). Interval_index advanced manually per type-aware tables; Attempts.json interval_index not auto-bumped — flag for tooling fix.

## Open questions surfaced
- None new; existing open questions unchanged.