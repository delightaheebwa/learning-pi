# Learning System

This is a local-first spaced-repetition learning system that turns your
assistant into a rigorous tutor. It forces retrieval instead of passive reading,
checks prerequisites, and preserves memory across sessions. It was originally
built with Zo and Obsidian. The Open WebUI path is frozen, and the canonical
runtime is pi in `learning-pi`.

## How it works

Say `/review`, `/solo`, `/ingest`, `/teach`, `/lesson`, `/continue`, `/pause`, or
`/audit`. The assistant then runs the pi `learning-system` skill. The copy under
`Skills/` is a frozen legacy snapshot. That skill handles reviews, ingestion, and
the writes listed below.

The review gate is a `review-gate` subagent task. It runs after standalone
ingests, and at lesson end when a lesson wrote wiki content. Teaching
verification uses batched `fact-check` subagent tasks. `quiz-audit` audits the
question batches, both probe and end-of-lesson quiz, before the learner sees
them.

Verifier models are configured in `.pi/settings.json`. The gate requires a
matching passing receipt, and it does not depend on model separation. See the
root `README.md` and `FIELD-GUIDE.md`.

Agent behavioral conventions, including the consistency checks and git sync,
live in `AGENTS.md`.

## Layout

- `Core/` holds live state: `💡 Learning Profile.md`, `📚 Active Concepts.md`
  for the review schedule, `Attempts.json` as the mastery sidecar,
  `🧯 Mistakes.md`, the generated `Learner History.md`, `📦 Concept Archive.md`,
  and the session and review templates. `📖 Scripture Memory.md` was archived on
  2026-09-08 to `Archive/frozen/`.
- `Sessions/` holds session notes.
- `Reviews/` holds review notes, including `Quality Gates/` and
  `Session Audits/`.
- `Lessons/` holds lesson files, with 5 live.
- `Learning Records/` holds numbered records in ADR style.
- `Concept Notes/` is an archived stub, frozen on 2026-09-08. Do not add to it.
- `build-artifacts/` holds built lesson artifacts, for example optimizers.
- `.tmp/` holds ephemeral Scout digests. It is gitignored and has a 7-day TTL.
- `Archive/` holds reference-only historical material.
- `Knowledge Wiki/` is the sibling folder with curated wiki pages, `index.md`,
  and `log.md`.
- `state/Skills/` is the frozen Open WebUI snapshot: `learning-system`,
  `learning-teach`, `learning-review` as the quality gate, and `llm-wiki`, plus
  the `learning-review/openwebui/` gate files.

## Principles

The system follows these principles:

- Clarity is not comprehension.
- Prerequisites come first.
- Retrieval beats recognition.
- Open questions stay open until resolved.
- Active Concepts is the persistent memory.
