<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# MIT Missing Semester — Editors (Vim)

> Source: handwritten class notes, Lesson 3 "Development Environment & Tools" (MIT Missing Semester editors lecture, https://missing.csail.mit.edu/2020/editors/) transcribed 2026-08-25 → 2026-08-28, cross-referenced with the live lecture. Ingested 2026-08-28 (Clerk). This page fills the gap left by the 2026-08-28 concept seeding: the three Vim rows (Modal Editing, Composable Commands, Buffers & Windows) existed but their wiki page was marked "pending Clerk ingest".

## Why a modal editor

Most of your time coding is **reading, navigating, and making small edits** to existing text — not typing long new streams. A word processor is built for the long-stream case; code isn't a long stream, so we use an *editor* optimized for the common case.

Vim is a **modal editor**: the same keystroke means different things in different modes, because "typing" is the rare case and "navigating & editing" is constant. It applies the same command-based (not cursor-based) philosophy as `ed` and `grep`.

## Modes

- **Normal** (default) — navigate and edit. Your whole keyboard is commands; no modifier keys held down. *Live here.*
- **Insert** — type new text. Enter with `i`; return with `Esc`.
- **Replace** — type over existing text. Enter with `R`; return with `Esc`.
- **Visual** — select text, then act on the selection (delete / change / yank). Enter with `v` (character), `V` (line), `Ctrl-V` (block); return with `Esc`.
- **Command-line** (`:`) — ex commands.

`Esc` returns to Normal from any mode. Why a separate Visual mode? So you can *see and fine-tune* the selection before committing, and because some selections aren't expressible as a single linear motion.

## Normal-mode keystroke categories

Per the notes, Normal-mode bindings fall into: **Movement · Selection · Edits · Counts · Modifiers**. Vim's interface is a **programming language** — editing commands are verbs, movements are nouns, and they compose.

- Verbs (edits): `d` delete, `c` change, `y` yank/copy, `p` paste, `u` undo, `Ctrl-r` redo.
- Nouns (movements): `w` next word, `b` back word, `e` end of word, `$` end of line, `0` beginning of line, `)` next sentence, `f` find (onto a char), `t` un**t**il (up to, not including a char).
- Counts multiply a motion: `3w` moves 3 words; `7dw` deletes 7 words.
- Modifiers `i`=**in**side / `a`=**a**round: `ci(` change inside parens (delimiters kept); `da'` delete a quoted string *and* its quotes.

Compositions: `dw` delete word, `cw` change word (delete then drop into Insert), `c$` change to end of line, `y$` yank to end of line, `ct)` delete to just before the next `)`.

## Buffers, Windows & Tabs

- **Buffer** = an open file loaded in memory.
- **Window** = a *view* onto a buffer.
- **Tab** = a *collection* of windows.

No 1:1 buffer↔window mapping: one buffer can be shown in two windows at once (`:sp` / `:vsp` to view two parts of the same file). Closing a window (`:q`) does **not** close the buffer. Analogy: `tab > window > buffer` is like browser tabs > views > open pages; for tmux it's `session > window > pane`.

Buffer commands: `:e file` open, `:ls` list buffers, `:b N` switch, `:w` write, `:wq` save+quit.

## Vim everywhere (readline)

You don't have to leave Normal mode at the shell. Two affordances bring Vim keys to the rest of your command line:

- `set -o vi` (bash) — switches the interactive line editor to vi mode (also `set editing-mode vi` in `~/.inputrc` for *all* readline apps).
- readline (the library behind the bash prompt, Python REPL, MySQL REPL, etc.) supports Vim emulation, so the keystrokes you learn once in Vim work in those tools too.

## Why learn an editor at all

"Winning editors into everything": a modal editor is the highest-leverage tool you can learn — the notes' challenge was to take the software you use that is modal and force yourself to use it for a month. The investment compounds because the muscle memory transfers to every readline-based prompt.

Related: [[MIT Missing Semester — Shell]] · [[Shell Built-ins & Process Isolation]] · [[tmux — Sessions, Windows & Panes]] · [[Environment Variables (Shell)]]
