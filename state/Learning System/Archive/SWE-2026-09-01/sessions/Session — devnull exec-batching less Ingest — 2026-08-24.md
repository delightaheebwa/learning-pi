# Session — Ingest: /dev/null, find -exec {} + batching, less — 2026-08-24

**Type:** Standalone ingest · **Track:** SWE (Stage 0 — Fluency & Tools, Mission 1: MIT Missing Semester)
**Source:** Handwritten lecture notes furnished by Delight (Mon 2026-08-24); spot-checked live against https://missing.csail.mit.edu/2020/shell-tools/ (confirms the `> /dev/null 2> /dev/null` discard idiom) and https://missing.csail.mit.edu/2026/course-shell/ (none of today's three items appear there).

## Concept changes

| Concept | Type | Status | Action | last_reviewed | next_review |
| --- | --- | --- | --- | --- | --- |
| less (Pager) | memory | developing | NEW — page + row | 2026-08-24 | 2026-08-27 |
| find | procedure | developing | ENRICHED — row + wiki (`-exec {} +`) | 2026-08-24 | 2026-08-27 (mistake retry stands) |
| Shell Redirections & Streams | concept | developing | ENRICHED — row + wiki (`/dev/null`) | 2026-08-24 | 2026-08-25 |

## What was added

- **New page** `Knowledge Wiki/wiki/less (Pager).md`: pager definition, why it doesn't load the whole file (lazy reading → fast + memory-efficient on huge logs), navigation basics, pipe-to-paginate, and the download-inspect-run tie-in.
- **[[MIT Missing Semester — Shell]] §find & fd:** added the `-exec CMD {} +` batch form — all matches substituted into ONE invocation — contrasted with `\;` (once per file).
- **[[MIT Missing Semester — Shell]] §Shell Redirections & Standard Streams:** added `/dev/null` (null device — discards everything written to it) and worked it into the example block: `find . -name "*.txt" -exec wc -l {} + 2>/dev/null`.
- **Duplicates skipped:** none — `less`, `/dev/null`, and `{} +` batching were all absent from Active Concepts.

## Open questions

- None raised this session. Standing debt: Feynman explain-backs pending on all concept-type items.

## Quality gate

- **BLOCKED:** review_gate pass 1 could not produce a verdict — stored API key rejected (HTTP 401, expired/invalid). Record with compensating checks: `Learning System/Reviews/Quality Gates/dev-null_find-exec-batching_less-pass1-2026-08-24.json`. Remedy: regenerate the key (Admin Panel → Settings → API Keys) → update `~/.config/learning-system/openwebui_key` → re-run.
