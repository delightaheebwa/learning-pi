> **ARCHIVED 2026-08-24** — superseded by `Learning System/CURRICULUM.md` (roadmap-aligned,
> sequential missions). The C-project strand (Terminal System Monitor) left the curriculum;
> its concepts moved to `Core/📦 Concept Archive.md`. Kept for history/revival.
>
# Curriculum: SWE Foundations — Stage 0 (Fluency & Tools)

> Integrated Stage-0 map. Two strands interleave deterministically strand-by-strand:
> **MIT Missing Semester** (Color 6 / Process) and the **Terminal System Monitor course** (mixed colors, C).
> Rotation rule: alternate strands positionally (MIT → Monitor → MIT → …). Colors are labels for seeing the mix, not a mechanical carousel.
> One curriculum lesson = one tangible-win unit (one monitor lesson, one MIT lecture). Lessons are resumable via `continue`.
> Status legend: `not-started` → `in-progress` → `done`. A lesson is `done` only after demonstrating its skill (retrieval check + Feynman explain-back + practice complete).

## Strand A — Terminal System Monitor (C) — source: `Curriculum/sources/terminal-system-monitor/`

| # | Lesson | Colors | Est. time | Prereqs | Status | Notes |
|---|--------|--------|-----------|---------|--------|-------|
| A1 | First compile (make) | Process + C [9] | 30–45m | shell + gcc | done | Mirrors Active Concepts: Makefile targets/prereqs/recipes |
| A2 | First tests (hand-rolled runner) | Process [8] | 45–60m | A1 | done | Mirrors: AAA, Testable Seam |
| A3 | Acutest + parser seam | Tests + Abstraction [7] | 60–90m | A2 | done | Mirrors: Acutest, fixtures, Static Fixtures & Boundary Cases |
| A4 | Read real memory (/proc/meminfo) | Systems + State [6] | 60–90m | A3 | done | Mirrors: meminfo smoke test, Sentinel Values vs Presence Flags |
| A5 | CPU from two samples (/proc/stat) | Computation + Systems [5] | 75–120m | A4 | not-started | Retrieval-verify prior concepts before teaching |
| A6 | List processes (/proc, PIDs) | Interaction + Systems [4] | 60–90m | A5 | not-started | |
| A7 | Live dashboard (termios, signals) | Interaction [3] | 90–150m | A6 | not-started | Capstone: Create level |
| A8 | CLI tool #2 (file organizer) | Color 6 | TBD | A7 | not-started | TBD — pick with user; git + tests |
| A9 | CLI tool #3 (TBD) | Color 6 | TBD | A8 | not-started | TBD — pick with user; git + tests |

## Strand B — MIT Missing Semester (2026) — source: https://missing.csail.mit.edu/2026/

| # | Lesson | Colors | Est. time | Prereqs | Status | Notes |
|---|--------|--------|-----------|---------|--------|-------|
| B1 | Course Overview + Shell | Process | ~1h | none | done | Shell fluencies already in Active Concepts (What is the Shell, Navigation, PATH…) |
| B2 | Command-line Environment | Process | ~1–2h | B1 | done | job control, signals, tmux, aliases, dotfiles |
| B3 | Development Environment & Tools | Process | ~1–2h | B2 | not-started | editors, Vim, customizing, shell scripting |
| B4 | Debugging and Profiling | Process | ~1–2h | B3 | not-started | gdb, strace, perf; syscall-level debugging |
| B5 | Version Control and Git | Process | ~1–2h | B4 | not-started | git internals; deepens Git commit conventions concept |
| B6 | Data Wrangling | Process | ~1–2h | B5 | not-started | regex, sed, awk deeper; joints to xargs/awk/pipes |
| B7 | Security and Cryptography | Process | ~1–2h | B6 | not-started | |

## Interleaving (automatic)

1. **Curriculum level (strand rotation):** alternate A ↔ B deterministically by position (e.g. A5 → B2 → A6 → B3 → …). The `lesson`/`continue` trigger returns the next lesson in the rotated order.
2. **Retrieval level:** every lesson's end quiz pulls 1–2 prior related concepts from the *other* strand (mixing practice).
3. **Review level:** unchanged — the existing SRS shuffle + adjacency + alternating types.

Rule of thumb: within a single lesson, introduction stays sequential (one reasoning step at a time); interleaving applies to practice and retrieval.

## How the map keeps honest

- New concepts from teaching enter `Core/📚 Active Concepts.md` on first introduction (status `developing`, `last_reviewed` today, `next_review` +3d), exactly like ingest.
- Lessons A1–A4 are marked `done` because their concepts already live in Active Concepts. When the curriculum reaches a `done` lesson, the teacher runs a **retrieval check** (verify, don't re-teach); a failed check demotes the lesson back to `in-progress` and corrects the concept status.
- Advancement requires: practice complete + retrieval check pass + Feynman explain-back (captured in a Learning Record, Bloom level noted).