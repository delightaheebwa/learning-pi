<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Environment Variables (Shell)

> Source: Lecture 2 written notes (website, Fri 2026-08-21) + MIT Missing Semester. Ingested 2026-08-24.

## What they are

Every process receives a bag of `KEY=value` **strings** from its parent. Whenever a program calls another program, it passes along its environment variables — that is how settings flow down a process tree. List them with `env`; print one with `echo $HOME`. Like shell variables generally, they have no types — everything is a string.

## Setting them — three scopes

1. **Per-command:** `TZ=Asia/Tokyo date` prepends an assignment to a single command — only *that* child sees `TZ`. Afterwards `echo $TZ` prints nothing: the variable never entered your shell. (The notes demonstrate this with `T2=Asia/Tokyo date` → `echo $T2` empty.)
2. **Shell-local:** `FOO=1` creates a variable owned by the shell process itself. Children do **not** inherit it.
3. **Exported:** `export DEBUG=1` (or `export DEBUG` for an existing var) marks the variable part of the environment, so every child inherits it. Check: `bash -c 'echo $DEBUG'` → `1`.

## Deleting: `unset`

`unset DEBUG` removes the variable from the environment/shell.

## Why export/unset must be built-ins

They mutate the **shell's own memory** (its environment). A child program cannot modify its parent's environment — OS process isolation forbids it (see [[MIT Missing Semester — Shell]] § Shell Built-ins vs External Programs).

## Common uses & gotchas

- `$PATH` is just another environment variable — extend with `export PATH=$PATH:/new/dir`.
- Per-command assignment is idiomatic for one-off config: `DEBUG=1 ./server`.
- Forgetting `export` is the classic bug: the script you call sees an empty variable while `echo $VAR` in the shell looks fine.

- `EDITOR` / `VISUAL` — programs read this env var when they need to launch an editor (e.g. `git commit`, `crontab -e`, `less` + `v`). Set `EDITOR=vim` once and you never fight a program's default editor again.
- **Vim keys everywhere:** `set -o vi` (bash) or `set editing-mode vi` in `~/.inputrc` switches the readline line editor to vi mode, so the Normal-mode keystrokes you learn work at the bash prompt and in any readline REPL (Python, MySQL, …).

Related: [[Positional & Special Shell Parameters]] · [[Exit Codes & Short-Circuit Control Flow]] · [[MIT Missing Semester — Editors (Vim)]]

## Sources

- MIT Missing Semester — Shell Tools and Scripting: https://missing.csail.mit.edu/2020/shell-tools/
- GNU Bash manual — Environment: https://www.gnu.org/software/bash/manual/html_node/Environment.html
