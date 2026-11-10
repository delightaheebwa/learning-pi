# Vendored agent-skills pack

- **Upstream:** <https://github.com/addyosmani/agent-skills>
- **Tag:** `0.6.15` (tag commit `8bfcc1f9`)
- **Commit:** `301b02b12bff98e4688e6984af6556802322bbde` (two commits after the tag: `353ae84` + merge `#736`)
- **Vendored:** 2026-11-10
- **License:** MIT, Copyright (c) 2025 Addy Osmani (see `skills/LICENSE`)

## What is vendored

| Path | Source | Notes |
| --- | --- | --- |
| `.opencode/skills/` | upstream `skills/` | 25 skills, `LICENSE` preserved |
| `.opencode/references/` | upstream `references/` | 7 shared checklists |
| `.opencode/docs/agents.md` | upstream `docs/agents.md` | persona orchestration rules |
| `.opencode/docs/opencode-setup.md` | upstream `docs/opencode-setup.md` | OpenCode setup reference |

## Local modifications (reapplied by the sync)

These are the only edits to vendored files. `patches/apply.py` applies them and
fails loudly if upstream has moved the target text.

1. `skills/spec-driven-development/SKILL.md` — sibling skill paths translated
   from `skills/<name>/SKILL.md` (repo-root relative) to `../<name>/SKILL.md`.
2. `docs/opencode-setup.md` — removed a link to upstream's `CONTRIBUTING.md`,
   which is not vendored.
3. `docs/agents.md` — prepended a note that its lifecycle slash commands were
   not adopted here and that personas are composed by the parent agent.

## Project-owned (never overwritten by a sync)

- `.opencode/agents/*.md` — four adapted personas (OpenCode frontmatter,
  permission scopes, parent-orchestration composition).
- `scripts/check-skills`, `scripts/floor-guard.mjs`, `.constraintsignore`.
- `CONSTRAINTS.md`, `AGENTS.md`, `docs/README.md`.

## Updating

```sh
scripts/skills-sync.sh
```

The script fetches the pinned commit by SHA (git verifies the objects), replaces
`skills/`, `references/`, and the two docs, reapplies `patches/`, and runs
`scripts/check-skills`. `TAG` is display-only; `SHA` is authoritative. To move to
a new upstream release, update `TAG`/`SHA` in `scripts/skills-sync.sh` *and* this
file in the same commit, then reconcile any patch that no longer applies.
