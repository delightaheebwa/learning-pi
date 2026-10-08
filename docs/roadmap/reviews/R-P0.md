# Reviewer R-P0 — review the P0 changes

You are the **P0 reviewer** on `opencode-go/muse-spark-1.3-contributor`. Follow
`docs/roadmap/reviews/README.md` for the rules and the exact findings-file format. **Review only — do
not edit code, commit, or spawn agents.** Write your findings to `docs/roadmap/reviews/P0.md`.

Read `docs/AUDIT-2026-10-08.md`, `AUDIT-ROADMAP.md` (P0 section), `CONTRACT.md`, and
`contracts/learning-core.json` first.

## Scope (P0 changes only)

**learning-pi** commits: `d00acf3` (P0.1 consolidation), `5d7af31` (P0.2 hard-facts/tail-bound),
`e42a817` (P0.3 ledger), `d40f9de` (P0.4 skills), `baad482` (P0.5 `/solo`), `5ce4573` (P0.6 skills).
**learning-system** commits: `0882821` (P0.4 ops), `64893fe` (P0.6 wiki provenance).

Inspect with e.g. `git -C ~/learning-pi show <sha>` and
`git -C ~/learning-system show <sha>`. Key files:
- `.pi/skills/learning-teach/SKILL.md`, `.pi/APPEND_SYSTEM.md`, `.pi/prompts/{teach,lesson,continue,solo}.md`,
  `.pi/agents/{clerk,review-clerk,fact-check}.md`
- `.pi/extensions/learning-gate/gate-core/{primitives,engine}.ts`, `gate-core/judge/types.ts`,
  `pi-adapter/index.ts`, `contracts/learning-core.json`, `CONTRACT.md`, `test/gate_test.mjs`
- `learning-system/scripts/{ops.py,learner_history.py,ops_test.py,wiki_provenance.py}`,
  `Knowledge Wiki/AGENTS.md`, `AGENTS.md`, `Skills/llm-wiki/SKILL.md`, `Knowledge Wiki/wiki/*.md`

## What to check (adversarially)

- **P0.2 claim completeness / binding:** does `missingHardFacts` actually close the self-selected-claim
  hole? Any false positives/negatives in `extractHardFacts` (e.g. years, list markers, code)? Does the
  tail bound (`extraTokenCount <= 12`) break legitimate re-emissions? Is the `claimsText` binding
  sound? Are the contract invariants (`G-claims-complete`, `G-draft-tail-bound`) actually covered by
  passing tests?
- **P0.1 consolidation / dependency log:** is the State rung's `[[TURN:none]]` vs `[[TURN:claims]]`
  rule consistent with the gate's none-evasion guard? Can "just tell me" still bypass all generation?
- **P0.3 ledger:** is it truly always-on? Does it record claim-level verdicts for fact/quiz/grade?
  Any PII/secret leakage, unbounded growth, or write failures that silently drop records?
- **P0.4 mastery/independence:** are the dimension heuristics defensible? Can `independence_ok`
  wrongly demote or wrongly grandfather? Does `ops.py attempt` stay backward-compatible?
- **P0.5 `/solo`:** can teaching still reach the learner in a solo flow (e.g. via `[[TURN:none]]`,
  grade, or inferred tags)? Is `SOLO_NO_TEACHING` actually enforced on all paths?
- **P0.6 wiki provenance:** does the stamp actually cover all pages? Is the trust inversion consistent
  across `AGENTS.md` and the skills? Does the marker regex accept malformed markers?
- **General:** false claims in `AUDIT-ROADMAP.md`, missing tests, contract/implementation drift.

Run the checks you can: `cd ~/learning-pi && scripts/learn-check --no-load --with-sidecars`,
`cd ~/learning-system && python3 -m unittest scripts.ops_test`, `python3 scripts/wiki_provenance.py --check`.

Write `docs/roadmap/reviews/P0.md` in the required format, then stop.
