# Development Environment & Tools (B3)

**Mission:** SWE Foundations — Stage 0 · **Prereqs:** B2 (Command-line Environment) · **Status:** done
**Colors:** Process
**Source:** https://missing.csail.mit.edu/2020/editors/ + https://missing.csail.mit.edu/2020/shell-tools/ (2026 URLs 404; stable 2020 mirrors)
**Date:** 2026-08-28

## Core

Probe result: the learner already held shell quoting (`'…'` vs `"…"`) and brace
expansion (correctly explained the `{foo,bar}/{a..h}` cross-product). The gaps
were (a) Vim keystrokes were genuinely new, and (b) a **misconception** in the
built-in/function/script taxonomy: they believed a script's `cd` changes the
parent shell's directory. This lesson taught the Vim philosophy fresh and
rebuilt the taxonomy around the one principle that collapses the whole table.

### Step 1 — Vim is a modal editor

**Unconditional truth:** Vim separates text *insertion* from text
*navigation/editing* into distinct modes, because programmers spend most time
reading/editing, not writing long streams. The same keystroke means different
things in different modes (`x` inserts a literal 'x' in Insert mode, deletes the
char under the cursor in Normal mode, deletes the selection in Visual).

**Modes:** Normal (default — navigate/edit), Insert (`i`), Replace (`R`),
Visual (`v`/`V`/`Ctrl-v`), Command-line (`:`). `Esc` returns to Normal from
anywhere.

### Step 2 — Vim's UI is a programming language

**Unconditional truth:** editing commands are **verbs** (`d`, `c`, `y`),
movements are **nouns** (`w`, `b`, `$`, `0`), and they compose as
verb+noun+count+modifier. `dw` = delete word; `cw` = change word (delete then
Insert); `3w` = move 3 words; `7dw` = delete 7 words.

**Modifiers** (`i`=inside vs `a`=around): `ci(` change inside the parens
(delimiters stay) → `fizzbuzz(10)` becomes `fizzbuzz()`. `da'` deletes a quoted
string AND its quotes. **Motions** (`f`=find onto, `t`=until/up-to): `ct)`
deletes from cursor to just before the next `)`.

### Step 3 — Buffers vs windows

**Unconditional truth:** a **buffer** is an open file in memory; a **window** is
a *view* onto a buffer; a **tab** is a collection of windows. No 1:1
buffer↔window mapping — one buffer can show in multiple windows at once
(`:sp`/`:vsp`). Closing a window (`:q`) does not close the buffer.

### Step 4 — The taxonomy: built-in vs function vs script

**Unconditional truth (the one principle that explains the whole table):**
a child process gets a **copy** of the parent's state but can never **write
back** to the parent's memory. Therefore:

| Kind | Runs in… | Can change your `cwd`? |
|---|---|---|
| built-in | the shell's own process | ✅ yes |
| function | the shell's own process | ✅ yes |
| script | a new child process | ❌ no |
| external command | a new child process | ❌ no |

**`cd` must be a built-in** because a child process can't propagate a cwd change
back; an external `cd` would change its own directory then exit (a no-op).

**Disk vs memory:** a child process *can* persist changes to **shared** channels
(disk files like `mkdir`, printed output) but can never rewrite the caller's
**private** memory (cwd, variables). `mkdir /tmp/x` survives; `cd /tmp/x` in a
script does not.

### Step 5 — Wiring editors into everything

- `export EDITOR=vim` sets the editor that programs launch (e.g. `git commit`).
- `#!/usr/bin/env python` resolves the interpreter via `$PATH`, making scripts
  portable (vs hardcoding `/usr/local/bin/python`).
- Vim emulation everywhere: `set -o vi` (bash), `set editing-mode vi`
  (`~/.inputrc`), browser extensions (Vimium/Tridactyl).

## Capstone (Create)

Ran `vimtutor`, then created `notes.txt` in Vim using `i`, `Esc`, `w`/`b`, and
`dw`. Learner self-diagnosed both beginner traps (deliberate Insert-mode entry;
hjkl one-char movement) and felt `w`/`b` word-hopping beat the mouse. Evidence
of Apply/Create.

## Quiz (first pass 3/6 — did NOT pass; re-probed to 5/6-equivalent)

Tier 1 retrieval: `c` = change (missed → said Visual); `ci)` vs `ct)` (inverted
twice → fixed with the inside/until 2×2 grid); buffers=files/windows=views ✅.
Tier 2 higher-order: script `cd` non-propagation ✅; `mkdir && cd` survival (missed
`sure` → said both persist — the disk-vs-memory split wobbled with both effects
present); `env` shebang ✅.

**Feynman explain-back: PASS** — "a function runs in the parent's process so it
can mutate shell state; a script runs in its own child and that change can't
propagate back up." Analogy: function = a child of the home; script = an errand
boy (sharpened: it's not permission, it's that he's in a different building).

**Re-probe (isomorphic):** R1 (core, both-effects) ✅ `sure`; R2 (`cw`) ✅
`hunch`; R3 (`di(` vs `dt)`) ❌ inverted → then F1/F2 ✅✅ `sure` — inversion
fixed.

## Glossary additions

→ proposed (pending user approval): **Modal editor**, **Buffer (Vim)**.

## Learning record

→ `Learning Records/0002-vim-modal-editing-and-process-isolation.md` (Feynman
explain-back passed; Bloom: Evaluate).

## Next steps

B4 — Debugging and Profiling (gdb, strace, perf; syscall-level debugging), per
CURRICULUM.md. Wiki pages for the 3 Vim concepts are a pending Clerk ingest
handoff (not written inline — see routing).
