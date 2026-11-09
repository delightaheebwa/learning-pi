# Curriculum — SWE Primary Colors & Roadmap

> Authoritative "what's next" map, aligned to the **SWE Primary Colors & Roadmap**
> (canonical copy: `Knowledge Wiki/wiki/SWE Primary Colors & Roadmap.md`).
> One mission per roadmap stage. Lessons within a mission are **sequential** —
> one at a time, no strand rotation, no interleaving (interleaving lives in the
> review flow only). One curriculum lesson = one tangible-win unit. Lessons are
> resumable via `continue`. Status legend: `not-started` → `in-progress` → `done`.
> A lesson is `done` only after demonstrating its skill (retrieval check +
> Feynman explain-back + practice complete).

## Mission 1 — Stage 0: Fluency & Tools *(Color 6 · Process · in progress)*

Goal: tooling becomes reflex, not friction.

- **Resource:** MIT Missing Semester (https://missing.csail.mit.edu/2026/) — shell, git, debugging, editors.
- **Note:** the roadmap's Stage-0 Python CLI-tool projects are skipped by decision (2026-08-24); tooling fluency is built directly through the MIT material and daily use.

| # | Lesson | Est. time | Prereqs | Status | Notes |
|---|--------|-----------|---------|--------|-------|
| 1 | Course Overview + Shell | ~1h | none | done | Shell fluencies in Active Concepts (What is the Shell, Navigation, PATH…) |
| 2 | Command-line Environment | ~1–2h | 1 | done | job control, signals, tmux, aliases, dotfiles |
| 3 | Development Environment & Tools | ~1–2h | 2 | done | editors, Vim, customizing, shell scripting |
| 4 | Debugging and Profiling | ~1–2h | 3 | not-started | gdb, strace, perf; syscall-level debugging |
| 5 | Version Control and Git | ~1–2h | 4 | not-started | git internals; deepens Git commit conventions concept |
| 6 | Data Wrangling | ~1–2h | 5 | not-started | regex, sed, awk deeper; joints to xargs/awk/pipes |
| 7 | Security and Cryptography | ~1–2h | 6 | not-started | |

**Exit:** shell, vim, git, and debugging hold no magic; you can profile a misbehaving program and read its syscalls.

## Mission 2 — Stage 1: Computation *(Color 1 · queued)*

Starts when Mission 1 completes.

- **Resource:** Berkeley CS61B (https://sp21.datastructur.es/, project-heavy) or _Grokking Algorithms_ for a gentler start.
- **Flagship project:** Write Yourself a Git! (https://wyag.thb.lt/) or ugit (https://www.leshenko.net/p/ugit/) — hashing, trees, graphs, compression.
- **Exit:** you can implement a nontrivial data structure cold.

Lesson table to be drafted when this mission activates.

## Future missions (not started)

Per the roadmap, in order:

- **Stage 2 — Systems:** nand2tetris + Build Your Own Text Editor (kilo)
- **Stage 3 — Abstraction:** Crafting Interpreters (+ _A Philosophy of Software Design_)
- **Stage 4 — State:** SQLBolt → Use The Index, Luke → Let's Build a Simple Database (or Redis from scratch)
- **Stage 5 — Interaction:** Beej's Guide to Network Programming (TCP → HTTP → chat → mini-Redis protocol)
- **Stage 6 — White Light:** containers-in-500-loc, Browser Engineering, MIT 6.824 distributed KV, real-codebase reading

## Rules

1. Lessons are strictly sequential within a mission; missions run in stage order.
2. New concepts enter `Core/📚 Active Concepts.md` on first introduction (status `developing`, `last_reviewed` today, `next_review` +3d), exactly like ingest.
3. A lesson marked `done` from prior learning is retrieval-checked, never re-taught; a failed check demotes it to `in-progress`.
4. Advancement requires: practice complete + retrieval check pass + Feynman explain-back (captured in a Learning Record, Bloom level noted).
5. Interleaving happens only in the review flow (SRS shuffle + adjacency + question-type alternation) — never inside lessons or quizzes.
