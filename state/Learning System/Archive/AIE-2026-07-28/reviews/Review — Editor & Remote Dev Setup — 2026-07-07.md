# Review — Editor & Remote Dev Setup — 2026-07-07

**Track:** AI Engineering (aie)
**Type:** Spaced Repetition Review (2nd review)
**Previous review:** 2026-07-04 (kept at 3d)

## Question
What's the system that makes VS Code extensions (linting, autocomplete, type checking) work without the editor doing the parsing itself?

## Answer
**LSP (Language Server Protocol)** — a standardized protocol for editors to communicate with language-specific tools. The editor sends text, the server returns errors, completions, and hints. The editor doesn't need to know the language — it just renders what the server says.

## Evaluation
✅ Fully correct. Explained LSP clearly and understood the editor-server separation.

## Outcome
- Status: developing
- Interval: advanced from 3d to 7d
- Next review: 2026-07-14
