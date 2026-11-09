# Session — Lesson B3 Dev Env & Tools Ingest — 2026-08-28

**Topic:** Lesson B3 — Development Environment & Tools (Vim + shell scripting process isolation)
**Date:** 2026-08-28
**Type:** standalone `/ingest` of transcribed handwritten class notes (5 images, Lesson 3, 2026-08-25 → 2026-08-28)

## Concepts touched

1. **Vim Modal Editing** (concept) — mode philosophy; Normal/Insert/Replace/Visual; `Esc` returns to Normal. (row preexisted, wiki page was the missing artifact)
2. **Vim Composable Commands** (concept) — verb+noun+count+modifier language; `dw`/`cw`/`ci(`/`da'`/`f`/`t`. (row preexisted)
3. **Vim Buffers & Windows** (concept) — buffer = open file, window = view, tab = collection; `:sp`/`:vsp`. (row preexisted)
4. **Shell Built-ins & Process Isolation** (concept) — enriched: built-in vs function vs script vs external; child gets copy of parent state but cannot write back; `set -u` nounset; side-effects on shared disk/terminal. (row preexisted, deepened)
5. **Environment Variables (Shell)** (concept) — enriched: `EDITOR`/`VISUAL` var; readline `set -o vi` affordance. (row preexisted)
6. **Shell Redirections & Streams** (concept) — enriched: portable `env` shebang; `cut`/`wc`/history; `wc -l < file` hides filename because shell opens the file. (row preexisted)

## Status / next review

- 3 Vim rows: prereq set to `Shell Built-ins & Process Isolation`; wiki link de-"pending"; `last_reviewed` 2026-08-28; `next_review` 2026-08-31 (unchanged).
- Curriculum B3 already `done` (CURRICULUM.md:23).

## Interleaving

Enrichment-focused ingest (no new concept seeds): 3 Vim pages + 2 enriched pages, all on the MIT Missing Semester editors/shell source. Source-adjacency unavoidable (all share course-shell/editors source).

## Open questions

- None new. (Note: the notes' claim that "a function runs in your shell so an `ed` state" is garbled; the load-bearing point — functions behave like built-ins and run in the shell's own process — is captured under Shell Built-ins & Process Isolation.)

## Review gate

Ran as a foreground `GATE:review` envelope (delegate_task) on model `ox-alpha-free` (the bootstrap/default review model). The legacy `review_gate` Open WebUI *Tool* (also `ox-alpha-free`) is retired (OPENWEBUI.md:9) and was unreachable from this sandbox even when active (separate container; no `:8080` listener) — surfaced rather than faked. Verdict: [[Learning System/Reviews/Quality Gates/Editors-Vim+Shell-Enrichments-pass1-2026-08-28.json]].
