<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# tmux — Sessions, Windows & Panes

> Source: Saturday 2026-08-22 lecture notes (website). Starter page — deepen during the Command-line Environment lesson.

## The three-level hierarchy

- **Session** — an independent workspace holding one or more windows. Detaching leaves everything running server-side; reattach anytime (`tmux new`, `tmux attach`). Sessions survive disconnects.
- **Window** — fills the terminal viewport; equivalent to tabs in an editor or browser. Usually the separate parts of one session.
- **Pane** — a split screen *within* a single window; several panes visible at once.

## Why it matters

tmux keeps long-running work alive across SSH drops, laptop sleep, or accidental window closes — the durable cousin of shell background jobs ([[MIT Missing Semester — Shell]] § Background Jobs). Panes let you watch a build in one split while editing in another, without alt-tabbing.

Related: [[Exit Codes & Short-Circuit Control Flow]] · [[SSH — Public-Key Auth & Remote Commands]]

## Sources

- tmux man page: https://man.openbsd.org/tmux.8
- tmux wiki: https://github.com/tmux/tmux/wiki
