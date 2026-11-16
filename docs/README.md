# Documentation index

This file maps the docs in this repo. Read it before any other doc.

## Sources of truth

| Question | File |
| --- | --- |
| What behavior is guaranteed, and which tests prove it | `CONTRACT.md` and `contracts/learning-core.json` |
| What "good enough to ship" means, and what must not be weakened in a diff | `CONSTRAINTS.md` |
| How to verify a change | `scripts/learn-check`, `scripts/check-docs`, `scripts/check-skills`, and `scripts/floor-guard.mjs` |
| How to work in this repo | `AGENTS.md` |
| What the system is and how to set it up | `README.md` |
| Current teaching method | `docs/teaching-methodology.md` |

`contracts/learning-core.json` is the authoritative invariant set. The file's
version, its invariant count, and the test name for each invariant change over
time. No other doc repeats those numbers, so point at the JSON instead.

Root CI (`.github/workflows/learn-check.yml`) runs `scripts/learn-check --no-load`,
which also runs the `harness/` suite. CI also runs `scripts/check-docs`,
`scripts/check-skills`, `scripts/floor-guard.mjs`, the state unit tests,
`gitleaks`, and the `revise(contract):` commit-subject check.

## Current docs

| File | What it covers |
| --- | --- |
| `README.md` | System overview, setup, tutor flows, repo layout. |
| `FIELD-GUIDE.md` | Day-to-day operator reference and failure diagnosis. |
| `CONTRACT.md` | Prose statement of the behavior contract and the two-door change rule. |
| `docs/README.md` | This index. |
| `docs/teaching-methodology.md` | Current LearnHarness-hybrid teaching method. |
| `docs/adr/ADR-0001-transcript-parsing.md` | Decision to keep the two transcript readers separate. |
| `docs/adr/ADR-0002-agent-skills-adoption.md` | Why the agent-skills pack is vendored under `.opencode/`. |
| `bridge/README.md` | `B-*` bridge invariants. |
| `deploy/README.md` and `deploy/SECURITY.md` | Docker Open WebUI deployment and its security notes. |
| `harness/README.md`, `bin/README.md`, `omarchy/README.md` | Per-component guides. |
| `state/README.md` | Layout of the learner state tree. |

## Skill and prompt map

The pi runtime loads these files. `test/contract/check_learning_layer.py`
asserts on their content, so edit them with care.

| Tree | Files | Role |
| --- | --- | --- |
| `.pi/skills/` | 5 | Canonical teaching flows for pi. |
| `.pi/prompts/` | 8 | Slash-command entry points. Seven of the eight carry a `[[FLOW:...]]` marker, and `audit.md` is not a gated flow. |
| `.pi/agents/` | 15 | Verifiers and workers dispatched by the gate. |
| `.pi/APPEND_SYSTEM.md` | 1 | Tutor stance loaded every turn. |
| `state/Skills/` | 4 | Frozen Open WebUI snapshot. `state/scripts/setup_openwebui.py` still ships these skill bodies live, and `state/scripts/` reads its `gate_pipe.py`. |

The invariants in `contracts/learning-core.json` bind to these resource checks.
A prose edit that removes an asserted phrase turns `scripts/learn-check` red.

## Historical docs

Completed work is archived under [`docs/archive/`](archive/README.md). These
files record work already done, not current process. Do not follow their
instructions. Their internal paths are frozen snapshots that may no longer
resolve.

- `docs/archive/AUDIT-ROADMAP.md` is the 2026 staged audit. Its stage status and
  contract counts predate the current contract.
- `docs/archive/roadmap/` is a completed Herdr cascade. Its briefs describe a
  push-to-main workflow that no longer applies. The helper scripts and the
  unused R-P3 brief were removed.
- `docs/archive/roadmap/E2E-REPORT.md` and
  `docs/archive/roadmap/STAGE-LOG.md` are snapshots from that cascade.
- `docs/archive/plans/intelligent-ui/` is a completed spike. It names modules
  that do not exist in this tree and pins an older Open WebUI version.
  `PHASE0-FINDINGS.md` records the rationale for the live
  `@openuidev/browser-bundle` pin.
- `docs/archive/AUDIT-2026-10-08.md` is the original deep audit and is
  explicitly historical.

### Inherited state-tree records

Several files under `state/` came from the pre-merge standalone
`learning-system` checkout. They historically escaped `scripts/check-docs`,
which now guards them. These files are frozen historical records, not current
process. Do not follow their remotes, paths, or commands:

- `state/AGENTS.md`, `state/OPENWEBUI.md`
- `state/infra/ACCESS.md`, `state/infra/VERSIONS.md`

Current references are the root [`README.md`](../README.md) and
[`FIELD-GUIDE.md`](../FIELD-GUIDE.md), plus the conventions in
`state/Learning System/AGENTS.md` and `state/Knowledge Wiki/AGENTS.md`.

## Open work

These are known gaps. All of them land as ordinary commits. Last verified:
2026-11-16.

### Ordinary commits

- `state/Skills/` is described as frozen, but the legacy installer
  `state/scripts/setup_openwebui.py` still ships those skill bodies to an Open
  WebUI instance when you run it. The docs now say so. Reconciling the two
  stacks is a separate redesign.

### Deliberate duplication, guarded

`.pi/APPEND_SYSTEM.md` owns the normative stress-test protocol. The teaching
skill is its operational step-index. Both load paths are bound by contract
resource checks, so `harness/protocol_sync_test.py` pins their shared markers
instead of merging them. A physical dedupe still needs the revise door.

## Reading order

1. `README.md` for what the system is.
2. `AGENTS.md` before you change anything.
3. `CONTRACT.md` before you change behavior.
4. `docs/teaching-methodology.md` before you change teaching prompts.
