# AGENTS.md — working in this repo

`learning-pi` is the pi control layer plus learner state for a spaced-repetition
learning system: a tutor and verification gate, an OpenWebUI bridge, deploy
assets, and a notebook under `state/`. Read `docs/README.md` for the
source-of-truth map.

## Commands

- Verify a change: `scripts/learn-check --no-load` (offline) or
  `scripts/learn-check` (full).
- Doc drift: `python3 scripts/check-docs`.
- Skill-pack integrity: `scripts/check-skills`.
- Diff floor: `node scripts/floor-guard.mjs` (against `origin/main`).
- Secrets (CI-only): `gitleaks dir . --config .gitleaks.toml --redact --no-banner`.
- Launcher update: `lpi check` / `lpi update` (pinned in `versions.lock.json`).

## Layout and landmines

- `.pi/` — canonical teaching behavior: 5 skills, 15 subagents, 8 prompts.
- `.opencode/` — the vendored agent-skills pack (25 skills, 4 personas). It is
  pinned; update it with `scripts/skills-sync.sh`, not by hand-editing vendored
  files. Its guard scripts live in `scripts/`.
- `contracts/` + `CONTRACT.md` — product behavior invariants, **frozen**. They
  change only through the revise door. Never edit `CONTRACT.md`, `contracts/`,
  or `test/` to make a change pass, and never restate the JSON's version,
  invariant count, or test names — point at it.
- `state/` — the learner notebook (merged). The retired Antigravity layer was
  removed in the 2026-11 cleanup and no longer exists.
- `bridge/`, `deploy/`, `harness/`, `omarchy/` — runtime, packaging, and the
  update conductor. No lint or coverage tool is configured; verify with the
  commands above.
- System-level changes (packages, `/etc`, systemd, boot) are out of scope for
  this repository. `ovm` VM testing is not used here: every change is
  repository-local and reversible with git, and `opencode.json` denies the
  `ovm` skill for this project.

## Agent skills

Skills live in `.opencode/skills/` and OpenCode advertises them natively from
their descriptions; that is the only router. Load the skill that matches the
task; do not preload the whole pack. Start with `using-agent-skills` only when
the task is ambiguous. Typical chains:

- Feature: `spec-driven-development` → `planning-and-task-breakdown` →
  `incremental-implementation` + `test-driven-development` →
  `code-review-and-quality`.
- Bug: `debugging-and-error-recovery` → `test-driven-development` →
  `code-review-and-quality`.

Read `CONSTRAINTS.md` before writing code. Do not weaken it to make a change
pass. It is the engineering bar; `CONTRACT.md` is the product bar. They are
different documents and neither replaces the other.

## Personas (subagents)

Four personas live in `.opencode/agents/`. They do not call each other; the
parent agent or the user composes them with `Task` calls.

| Subagent | Model | Edits |
| --- | --- | --- |
| `code-reviewer` | `opencode-go/glm-5.3-flash#high` | denied |
| `security-auditor` | `opencode-go/glm-5.3-flash#high` | denied |
| `test-engineer` | `opencode-go/glm-5.3-flash#high` | allowed (it writes tests) |
| `web-performance-auditor` | `opencode-go/deepseek-v4.1-flash#high` | denied |

The pack is MIT-licensed (`.opencode/skills/LICENSE`). The `chrome-devtools`
MCP server is configured in `opencode.json` and pinned to `1.12.0`; do not add a
`.mcp.json` or change the pin.
