# Roadmap cascade — orchestration

This directory drives the staged implementation of the learning-system audit.
It is executed by a **cascade of Herdr agents**: each stage agent implements its stage, verifies it,
commits and pushes, then spawns the next stage agent in a new Herdr tab.

```
(this orchestrator) → P1 → P2 → P3* → REVIEW → E2E
                               (*P3 deferred: no-op forwarder)
                                        ├── R-P0  (Muse Spark) review P0 changes
                                        ├── R-P1  (Muse Spark) review P1 changes
                                        └── R-P2  (Muse Spark) review P2 changes
                                           → aggregate → fix (default model) → E2E
```

P0 is already complete (see `AUDIT-ROADMAP.md`). The cascade covers the remaining stages, then a
**review phase** (one Muse-Spark reviewer per checkpoint, an aggregate+fix step, then final E2E).
See `docs/roadmap/reviews/README.md`.

## What every stage agent must read first

1. `docs/AUDIT-2026-10-08.md` — the **full audit** (the user's canonical capture: audit + P0.1 plan +
   summary). This is the *why* behind every task.
2. `AUDIT-ROADMAP.md` — the living plan and status; P0's landed work and the P1/P2/P3 items.
3. `CONTRACT.md` and `contracts/learning-core.json` — the behavior contract.
4. This stage's brief: `docs/roadmap/<STAGE>.md`.

## Ground rules (carried over from P0)

- **Two repos.** `learning-pi` is the pi/control/runtime layer; `learning-system` is durable state,
  scripts, wiki, skills. Change each in its own repo and commit there.
- **Revise door.** Changing gate behavior means editing `contracts/learning-core.json` **first**, in
  the same commit as its tests and implementation. The update door never touches `contracts/`/`test/`.
- **Deterministic over LLM** where a task is mechanical; adaptive judgment stays with the model.
- **Additive and backward-compatible** unless the task says otherwise. Do not break existing state.
- **Verify before you advance:** `cd ~/learning-pi && scripts/learn-check --no-load --with-sidecars`
  must pass. Add tests for every behavior change and name them to match contract `tests` substrings.
- **Do not commit learning state from `learning-pi`.** State commits happen in `learning-system`.
- **Record progress** in `AUDIT-ROADMAP.md` (mark items done, note deviations) each stage.
- **Honesty.** If an item is deferred or only partly done, say so in the roadmap with the reason.
  Never claim a check passed if it did not.

## Cascade protocol

When your stage is complete, verified, committed, and pushed, spawn the next stage:

```bash
bash /home/delightaheebwa/learning-pi/docs/roadmap/spawn-stage.sh <NEXT_STAGE>
```

`<NEXT_STAGE>` is one of `P1`, `P2`, `P3`, `E2E` (each stage's brief names the next). The helper
creates a new Herdr tab, starts a fresh `opencode` agent named `roadmap-<stage>` with `--auto`, and
sends it that stage's brief. Then **finish your own turn** — do not wait for the child.

If you run out of practical capacity mid-stage, do **not** silently stop: commit what is complete and
verified, write precisely what remains into `AUDIT-ROADMAP.md`, then spawn the next stage anyway so
the cascade continues (the next agent or a human can pick up the remainder).

## Stage ownership

| Stage | Brief | Scope | Spawns |
| --- | --- | --- | --- |
| P1 | `P1.md` | High-impact: Feynman gate, deterministic MCQ+q_type, prerequisites, confidence calibration, transfer, withhold unverified, learner-authored wiki, red-team harness, fading hints | P2 |
| P2 | `P2.md` | Valuable: blocking state audit, remove out-of-scope demotion, Scout TTL, pi canonical, `ops.py amend`, prompt contradictions, interleaving, misconception links | P3 |
| P3 | `P3.md` | **Deferred** — no implementation; forwards to REVIEW | REVIEW |
| REVIEW | `REVIEW.md` | Spawn R-P0..R-P2 (Muse Spark), aggregate, fix, then spawn E2E | E2E |
| E2E | `E2E.md` | Full end-to-end verification of everything built | — (final) |

Reviewer briefs: `docs/roadmap/reviews/R-P{0,1,2}.md` (spawned by `spawn-reviewer.sh`; `R-P3` is kept
but unused while P3 is deferred).
