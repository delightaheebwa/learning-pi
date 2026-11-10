# ADR-0002 — Adopt agent-skills as a pinned vendored layer with two explicit quality bars

- **Status:** Accepted
- **Date:** 2026-11-10
- **Deciders:** repo owner

## Context

`addyosmani/agent-skills` was vendored into `.opencode/skills/` as a partial copy:
6 of 7 shared `references/` were missing, `docs/agents.md` was absent, every
persona invoked slash commands that do not exist in OpenCode, and nothing
pinned the upstream version. `.opencode/skills` sat outside `check-docs`, so the
broken links survived.

The repo already had a written, mechanically enforced bar: `CONTRACT.md` plus
`contracts/learning-core.json`, with each invariant bound to a passing test and
a revise door guarding `CONTRACT.md`, `contracts/`, and `test/`. Root
`AGENTS.md` claimed that `constraint-driven-development` "maps onto" that bar
and forbade a `CONSTRAINTS.md`.

That mapping was wrong. The contract governs learning-system runtime behavior
and has no content about suppressions, skipped tests, stubs, coverage,
accessibility, performance budgets, lint, dependency audit, or `.opencode/`.
The skill's detect step never reads `CONTRACT.md`; its only skip condition is an
existing `CONSTRAINTS.md`. Following the skill literally would have produced the
forbidden file; following `AGENTS.md` would have silently dropped the skill.

## Decision

Adopt the pack as a pinned, vendored layer with **two explicitly scoped bars**:

1. `CONTRACT.md` + `contracts/learning-core.json` — product/domain invariants.
   Frozen, revise door, `scripts/learn-check`.
2. `CONSTRAINTS.md` — engineering quality for any change, including
   `.opencode/`, `state/`, and docs. Living, ratchetable,
   `scripts/floor-guard.mjs`.

`CONSTRAINTS.md` points at the JSON instead of restating its version, count, or
test names, so `docs/README.md`'s single-source rule holds. `docs/README.md`
names both files in its sources-of-truth table.

Supporting decisions:

- **One router.** OpenCode discovers skills natively; `AGENTS.md` no longer
  duplicates the lifecycle as a second router, and `using-agent-skills` is on
  demand only.
- **Pinned vendoring.** `.opencode/UPSTREAM.md` records tag `0.6.15` / commit
  `301b02b`; `scripts/skills-sync.sh` re-vendors and reapplies the two
  documented patches. No `npx` install and no submodule.
- **Parent orchestration.** Personas do not invoke each other or nonexistent
  slash commands; the parent composes them with `Task` calls.
- **Gates.** `scripts/check-skills` pins the pack inventory and links;
  `scripts/floor-guard.mjs` blocks diff-level weakening; CI warns on
  `check-skills` until 2026-11-24 and blocks the floor and the revise door
  immediately.
- **Floor-only first run.** No coverage, vulnerability, performance, or
  accessibility tool is installed, so those dimensions are deferred; the
  "at least one external constraint" gap is exception `E1` with an owner and
  expiry.

## Consequences

- A root `CONSTRAINTS.md` exists and is the engineering bar; `AGENTS.md` points
  at it.
- The pack is complete, pinned, and reproducible; broken links cannot return
  unnoticed once `check-skills` is promoted to blocking.
- `CONTRACT.md` and `contracts/` are untouched, so no invariant or revise-door
  behavior changed.
- `scripts/learn-check` was not modified; the new gates are separate commands.
- The floor guard is regex-shallow by design and exempts vendored docs and
  `CONSTRAINTS.md`; a determined author can still evade it.
- Until 2026-11-24 `check-skills` is advisory, so a broken pack warns rather
  than fails CI.

## Revisit when

- `check-skills` is promoted to blocking on 2026-11-24.
- An external scanner (`osv-scanner`, `gitleaks`, `semgrep`) is added; retire
  exception `E1`.
- Upstream moves the patch targets, or a new release changes the skill
  inventory.
- A coverage or performance metric becomes meaningful enough to record as a
  ratchet.
