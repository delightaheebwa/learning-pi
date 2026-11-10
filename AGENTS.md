# AGENTS.md — agent skills (this repo)

Skills from `addyosmani/agent-skills` live in this repo under
`.opencode/skills/`. Start with `using-agent-skills` when unsure which one
applies.

## Core rules

- If a task matches a skill, load it with the `skill` tool before acting.
- Follow the skill workflow strictly; never skip a required step such as spec,
  plan, or test when the skill demands it.
- A skill may reference its own `references/` and `scripts/` directories; use
  those paths rather than guessing.
- The skill packs are MIT-licensed; see `.opencode/skills/LICENSE`.
- `constraint-driven-development` maps onto this repo's existing bar:
  `CONTRACT.md` and `contracts/` already are the written contract. Do not create
  a parallel `CONSTRAINTS.md`, and do not edit guarded files to satisfy it.
- The `chrome-devtools` MCP server is already configured in `opencode.json`
  (`mcp.servers.chrome-devtools`, pinned to `1.12.0`). Do not add a `.mcp.json`
  or change the pin.

## Lifecycle mapping

- DEFINE → `spec-driven-development`, `interview-me`, `idea-refine`
- PLAN → `planning-and-task-breakdown`
- BUILD → `incremental-implementation`, `test-driven-development`
- VERIFY → `debugging-and-error-recovery`, `browser-testing-with-devtools`,
  `performance-optimization`
- REVIEW → `code-review-and-quality`, `code-simplification`,
  `security-and-hardening`
- SHIP → `shipping-and-launch`, `ci-cd-and-automation`,
  `documentation-and-adrs`
- Cross-cutting → `context-engineering`, `git-workflow-and-versioning`,
  `observability-and-instrumentation`, `deprecation-and-migration`,
  `api-and-interface-design`, `frontend-ui-engineering`,
  `constraint-driven-development`, `doubt-driven-development`,
  `source-driven-development`
