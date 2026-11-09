# 📚 Learning System (canonical: pi · Open WebUI frozen)

A local-first, spaced-repetition learning system that turns your assistant into a rigorous tutor. It forces retrieval instead of passive reading, checks prerequisites, and preserves memory across sessions. Originally built with Zo + Obsidian; Open WebUI path frozen — canonical runtime is **pi** (`learning-pi`).

## How it works

Say `/review`, `/ingest`, `/teach`, `/lesson`, `/continue`, or `/pause` — the assistant runs the pi **`learning-system`** skill (legacy Open WebUI copy: `Skills/learning-system`), which handles reviews, ingestion, and the writes below. The review gate is a review-gate subagent task (runs after standalone ingests AND at lesson end when a lesson wrote wiki content); teaching verification uses batched fact-check subagent tasks; question batches (probe and end-of-lesson quiz) are audited by quiz-audit subagent tasks before the learner sees them. Verifiers run on the **calling preset's own base model** (Open WebUI has no separate verifier-model setting — see `OPENWEBUI.md`) — enforcement rests on the deterministic Pipe checks.

Agent behavioral conventions (consistency checks, git sync) live in `AGENTS.md`.

## Layout

- `Core/` — live state: `💡 Learning Profile.md`, `📚 Active Concepts.md` (the review schedule), `Attempts.json` (mastery sidecar), `🧯 Mistakes.md`, `Learner History.md` (generated), `📦 Concept Archive.md`, session/review templates (`📖 Scripture Memory.md` archived 2026-09-08 to `Archive/frozen/`)
- `Sessions/` — session notes
- `Reviews/` — review notes (incl. `Quality Gates/`, `Session Audits/`)
- `Lessons/` — lesson files (5 live)
- `Learning Records/` — numbered records (ADR-style)
- `Concept Notes/` — archived stub (frozen 2026-09-08, do not add)
- `build-artifacts/` — built lesson artifacts (e.g. optimizers)
- `.tmp/` — ephemeral Scout digests (gitignored, 7-day TTL)
- `Archive/` — reference-only historical material
- `Knowledge Wiki/` (sibling folder) — curated wiki pages, `index.md`, `log.md`
- `Skills/` (repo root) — FROZEN Open WebUI snapshot: `learning-system`, `learning-teach`, `learning-review` (quality gate), `llm-wiki` (+ `learning-review/openwebui/` gate files)

## Principles

- Clarity is not comprehension
- Prerequisites come first
- Retrieval beats recognition
- Open questions stay open until resolved
- Active Concepts is the persistent memory
