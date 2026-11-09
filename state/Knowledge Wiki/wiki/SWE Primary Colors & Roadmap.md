<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# SWE Primary Colors & Roadmap — ARCHIVED 2026-09-01

> **Archived 2026-09-01 — superseded by AI Engineering from Scratch (Rohit).** See active map: [[AI Engineering from Scratch — Roadmap]] · `Learning System/CURRICULUM.md` (Rohit 20 phases) · archive copies: `Learning System/Archive/CURRICULUM — SWE Primary Colors — archived 2026-09-01.md` and `Learning System/Core/📦 Concept Archive.md` section `Paused Concepts — SWE (Archived 2026-09-01)` (visibility strictly out of scope — Scout/Tutor do not grep). This page kept for reference only.

> Source: `Learning System/Curriculum/` (attached by user, 2026-08-16) — the project-based roadmap for Software Engineering, primary colors taxonomy, and Stage 0 mission spine.

## Part 1 — The Six Primary Colors

| Color | Core Question | What It Contains |
|---|---|---|
| **1. Computation** | How do we transform data? | Algorithms, data structures, logic, state machines, complexity |
| **2. State** | How do we remember things? | Memory, files, databases, caches, transactions, consistency |
| **3. Interaction** | How do things talk? | I/O, protocols, networks, APIs, events, UIs |
| **4. Abstraction** | How do we tame complexity? | Functions, modules, types, interfaces, naming, decomposition |
| **5. Systems** | What does the machine actually do? | Hardware, OS, processes, memory layout, compilers, runtimes |
| **6. Process** | How do humans build reliably? | Testing, debugging, git, reading code, design, collaboration |

### The mixing test

Every technology is a blend: React = Abstraction + State + Interaction · Redis = State + Systems + Interaction · A compiler = Computation + Abstraction + Systems · Docker = Systems + Interaction + Process · Distributed systems = all six (the "white light").

## Part 2 — Project-Based Roadmap (5–10 hrs/week · ~18–24 months)

**Meta-resources:** [Build Your Own X](https://github.com/codecrafters-io/build-your-own-x) · [CodeCrafters](https://codecrafters.io).

- **Stage 0 — Fluency & Tools (Color 6 · ~1 month):** MIT Missing Semester (shell, git, debugging, editors) + 2–3 small CLI tools in Python (file organizer, notes CLI, weather fetcher), git + tests on every one. Goal: tooling becomes reflex, not friction.
- **Stage 1 — Computation (Color 1 · ~2–3 months):** Berkeley CS61B or _Grokking Algorithms_; flagship [Write Yourself a Git!](https://wyag.thb.lt/)/[ugit](https://www.leshenko.net/p/ugit/).
- **Stage 2 — Systems (Color 5 · ~3–4 months):** [nand2tetris](https://www.nand2tetris.org); second project [kilo (text editor)](https://viewsourcecode.org/snaptoken/kilo/).
- **Stage 3 — Abstraction (Color 4 · ~2–3 months):** [Crafting Interpreters](https://craftinginterpreters.com); side quest Rust or a Lisp; reading _A Philosophy of Software Design_.
- **Stage 4 — State (Color 2 · ~2–3 months):** SQLBolt → Use The Index, Luke → [Let's Build a Simple Database](https://cstack.github.io/db_tutorial/) (SQLite clone in C) or [Build Your Own Redis](https://build-your-own.org/redis).
- **Stage 5 — Interaction (Color 3 · ~2–3 months):** [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/); web server raw TCP → HTTP/1.1 → chat → mini-Redis protocol.
- **Stage 6 — White Light (ongoing):** [Docker ~500 LOC C](https://blog.lizzie.io/linux-containers-in-500-loc.html), [Browser Engineering](https://browser.engineering), MIT 6.824 labs, read Redis/SQLite codebases.

### Rules That Make Project-Based Learning Work

1. **Rebuild, don't copy.** Type every line; close the tutorial and re-derive.
2. **Finish small, not big.** A completed tiny interpreter beats an abandoned compiler.
3. **One color at a time.** Mixing happens in capstones.
4. **Tests + README on everything.** Color 6 compounds.
5. **Time math:** each stage ~60–100 hours ≈ 2–3 months at 5–10 hrs/week.

## Status

- **Stage 0 archived 2026-09-01** (switch to AIEFS). Previously: Monitor course implemented in C (decision 2026-08-16: user chose C over the roadmap's Python for the CLI strand). Now: 43 SWE concepts paused, no active SWE rows in `📚 Active Concepts.md`.
- **Active roadmap:** [[AI Engineering from Scratch — Roadmap]] — Mission 0 Catch-Up (P0+P1.01–06, 80/20, in-progress) → Phase 1 L07 Bayes' Theorem.

Related: [[AI Engineering from Scratch — Roadmap]] (active) · [[AI Engineering Roadmap v2]] (paused) · [[MIT Missing Semester — Shell]]

## Sources

- Build Your Own X: https://github.com/codecrafters-io/build-your-own-x
- CodeCrafters: https://codecrafters.io
- MIT Missing Semester: https://missing.csail.mit.edu/
- nand2tetris: https://www.nand2tetris.org
- Crafting Interpreters: https://craftinginterpreters.com