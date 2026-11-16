# State tree: agent conventions

Read the root [`AGENTS.md`](../AGENTS.md) first. It governs this repo.

This file came from the pre-merge standalone `learning-system` checkout. Its
former body described a retired two-repo setup: Open WebUI as the live runtime,
a `learning-system` GitHub remote, an Open Terminal container checkout, and a
WSL maintenance checkout. None of that is current. Do not follow those paths,
remotes, or commands. The old text stays in git history.

## What is current

- This repo is [`learning-pi`](https://github.com/delightaheebwa/learning-pi).
  The learner state lives in `state/`, and there is no separate state repo.
- Canonical teaching behavior is in `.pi/skills/`, `.pi/agents/`,
  `.pi/prompts/`, `.pi/APPEND_SYSTEM.md`, and the gate in
  `.pi/extensions/learning-gate/`.
- `state/Skills/`, `state/OPENWEBUI.md`, `state/infra/`, and
  `state/scripts/setup_openwebui.py` are a frozen legacy Open WebUI snapshot.
  Do not add teaching-behavior changes there.
- Run `pi` from `state/` after `install.sh` links `.pi/` here. See the root
  [`README.md`](../README.md) and [`FIELD-GUIDE.md`](../FIELD-GUIDE.md).

## Conventions for editing state data

- [`Learning System/AGENTS.md`](Learning%20System/AGENTS.md) holds the
  consistency checks for notebook edits.
  [`Knowledge Wiki/AGENTS.md`](Knowledge%20Wiki/AGENTS.md) holds the wiki-file
  rules.
- The Clerk commits state at ingest and review close. Those files also carry the
  current single-repo git rules.
- Verify a change with `scripts/learn-check --no-load` and
  `python3 scripts/check-docs`.

## SRS state semantics

- `Core/📚 Active Concepts.md` columns: Concept | Type | Status | Prerequisites |
  Last Reviewed | Next Review | Source | Last Q Type | Notes. `Type` is one of
  `memory`, `concept`, `procedure`, or `design`, and it drives the intervals in
  `scripts/ops.py` (`memory [0,1,3,7,14,30,60]d`, `concept [3,7,14,30]`,
  `procedure [3,7,14]`, `design [14,28]`).
- `Attempts.json` is an advisory mastery sidecar, updated through
  `scripts/ops.py`. Its `interval_index` gains 1 on a pass, gains 2 on two
  consecutive passes, and loses 1 on a fail.
- `🧯 Mistakes.md` is the priority queue. Each item moves from `active` to
  `review` to `graduated`.
- Review queues default to 5 slots. The first 2 slots take due mistakes, then
  due reviews fill the rest. A same-Source adjacency guard and question-type
  alternation apply.
- New concepts start `developing`, with `last_reviewed` today and `next_review`
  at +3d.

There is no separate remote, WSL checkout, or Open Terminal container to sync.
