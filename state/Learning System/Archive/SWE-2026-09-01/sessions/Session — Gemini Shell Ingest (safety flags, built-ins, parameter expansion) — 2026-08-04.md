# Session — Gemini Shell Ingest (safety flags, built-ins, parameter expansion) — 2026-08-04

**Date:** 2026-08-04
**Topic:** Shell scripting — safety flags deep dive, shell built-ins vs external programs, parameter expansion
**Track:** swe

## Source
Two Gemini conversation notebooks (Socratic tutoring sessions on shell scripting):
- https://gemini.google.com/app/effe61964e68778c — Shell safety flags (`set -euo pipefail`), `cp` vs `>`, command substitution in filenames, for loops with glob patterns, parameter expansion
- https://gemini.google.com/app/921fdcb9207f4b05 — Shell built-ins vs external programs, child process memory isolation, internal shell state, `chmod +x`, `if [ -f "$FILE" ]` syntax, variable assignment

## New Concepts (2)
1. **Parameter Expansion** — `${var%pattern}` strips suffix, `${var#pattern}` strips prefix. Used with loops and command substitution for file manipulation (e.g., backup scripts).
2. **Shell Built-ins & Process Isolation** — Why `cd`, `export`, variable assignment must be built-ins: child processes inherit parent's memory but OS prevents them from modifying it. Internal shell state = `$PWD`, env vars, background jobs, shell options.

## Enrichments (6)
1. **Shebang & Script Execution** — Added `|| true` pattern for expected failures, set -x security risk (exposes secrets in trace), deeper `set -euo pipefail` failure mode explanations
2. **Shell Conditionals** — Added that variables should be quoted in test conditions: `[ -f "$FILE" ]`
3. **Shell Loops** — Added backup loop pattern with `${FILE%.txt}` and `$(date +%Y-%m-%d)`
4. **Shell Redirections & Streams** — Added `cp` vs `>` distinction (copy vs stdout redirect)
5. **File Permissions** — Cross-referenced `chmod +x` detail
6. **Shell Navigation & Paths** — Cross-referenced built-ins concept

## Open Questions
- None — all concepts cleanly extracted

## Interleaving
N/A — ingest session, no review questions
