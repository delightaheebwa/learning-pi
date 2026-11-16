# ADR-0002: Adopt agent-skills as a pinned vendored layer with two explicit quality bars

- Status: Accepted
- Date: 2026-11-10
- Deciders: repo owner

## Context

`addyosmani/agent-skills` was vendored into `.opencode/skills/` as a partial copy. The copy was
missing 6 of 7 shared `references/`, and `docs/agents.md` was absent. Every persona invoked slash
commands that do not exist in OpenCode, and nothing pinned the upstream version.

`.opencode/skills` sat outside `check-docs`, so the broken links survived.

The repo already had a written bar with mechanical enforcement: `CONTRACT.md` plus
`contracts/learning-core.json`. Each invariant was bound to a passing test, and a revise door guarded
`CONTRACT.md`, `contracts/`, and `test/`. Root `AGENTS.md` claimed that
`constraint-driven-development` "maps onto" that bar and forbade a `CONSTRAINTS.md`.

That mapping was wrong. The contract governs learning-system runtime behavior. It has no content
about suppressions, skipped tests, stubs, coverage, accessibility, performance budgets, lint,
dependency audit, or `.opencode/`. The skill's detect step never reads `CONTRACT.md`. Its only skip
condition is an existing `CONSTRAINTS.md`. Following the skill literally would have produced the
forbidden file. Following `AGENTS.md` would have silently dropped the skill.

## Decision

Adopt the pack as a pinned, vendored layer with two explicitly scoped bars.

- `CONTRACT.md` and `contracts/learning-core.json` cover product and domain invariants. The files are
  frozen, the revise door applies, and `scripts/learn-check` enforces them.
- `CONSTRAINTS.md` covers engineering quality for any change, including changes to `.opencode/`,
  `state/`, and docs. It is living and ratchetable, and `scripts/floor-guard.mjs` enforces it.

`CONSTRAINTS.md` points at the JSON instead of restating its version, count, or test names. That
keeps the single-source rule in `docs/README.md` intact. `docs/README.md` names both files in its
sources-of-truth table.

Supporting decisions:

- The pack has one router. OpenCode discovers skills natively. `AGENTS.md` no longer duplicates the
  lifecycle as a second router, and `using-agent-skills` is on demand only.
- Vendoring is pinned. `.opencode/UPSTREAM.md` records tag `0.6.15` and commit `301b02b`.
  `scripts/skills-sync.sh` re-vendors the pack and reapplies the two documented patches. There is no
  `npx` install and no submodule.
- The parent orchestrates. Personas do not invoke each other or nonexistent slash commands. The
  parent composes them with `Task` calls.
- The following gates apply. `scripts/check-skills` pins the pack inventory and links.
  `scripts/floor-guard.mjs` blocks diff-level weakening. CI warns on `check-skills` until 2026-11-24.
  CI blocks the floor and the revise door immediately.
- The first pass is floor-only. No coverage, vulnerability, performance, or accessibility tool is
  installed, so those dimensions are deferred. The "at least one external constraint" gap is
  exception `E1` with an owner and expiry.

## Consequences

- A root `CONSTRAINTS.md` exists and is the engineering bar. `AGENTS.md` points at it.
- The pack is complete, pinned, and reproducible. Broken links cannot return unnoticed once
  `check-skills` is promoted to blocking.
- `CONTRACT.md` and `contracts/` are untouched, so no invariant or revise-door behavior changed.
- `scripts/learn-check` was not modified. The new gates are separate commands.
- The floor guard is regex-shallow by design and exempts vendored docs and `CONSTRAINTS.md`. A
  determined author can still evade it.
- Until 2026-11-24, `check-skills` is advisory, so a broken pack warns rather than fails CI.

## Revisit when

- `check-skills` is promoted to blocking on 2026-11-24.
- An external scanner (`osv-scanner`, `gitleaks`, `semgrep`) is added. Retire exception `E1`.
- Upstream moves the patch targets, or a new release changes the skill inventory.
- A coverage or performance metric becomes meaningful enough to record as a ratchet.

## Amendment (2026-11-10)

`E1` is retired. `gitleaks`, pinned to `8.30.1`, now runs in CI against tracked content and blocks on
findings. That gives the bar an external constraint. It runs CI-only to keep laptops clean.
`.gitleaks.toml` extends the default ruleset and allowlists one frozen raw source whose
`generic-api-key` match is a quoted model name, not a credential.

The `ovm` VM rule is waived for this repository. Every change is repo-local and reversible with git,
and `opencode.json` denies the `ovm` skill for this project.
