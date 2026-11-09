<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# MIT Missing Semester — Command-line Environment

**Source:** [Command-line Environment](https://missing.csail.mit.edu/2026/command-line-environment/)
**Track:** SWE (Software Engineering Fundamentals)
**Taught:** 2026-08-18 (lesson B2)

## Signals (software interrupts)

A **signal** is a short asynchronous message the kernel (or another process) delivers to a process — a "software interrupt" — that makes it stop and react. The receiving process can **catch, ignore, or take the default action** (often terminate). That's why Ctrl-C "sometimes fails" — the target gets a vote.

### The graceful-to-hard kill ladder

| Signal | Sent by | Catchable? | Purpose |
|---|---|---|---|
| SIGINT | `Ctrl-C` | Yes | polite interrupt |
| SIGTERM | `kill <pid>` | Yes | "exit gracefully, clean up first" |
| SIGKILL | `kill -9 <pid>` | **No** | nuclear option — always works, skips cleanup |

Rule of thumb: try Ctrl-C → `kill` (SIGTERM) → only if it still won't die, `kill -9`. SIGKILL's cost is no cleanup: orphaned child processes, unsaved state.

**You only use a few in practice:** there are many signals, but everyday work touches only a small set — `SIGINT` (interrupt, Ctrl-C — the one you reach for most), `SIGQUIT` (Ctrl-\, quit + core dump), `SIGTERM` (graceful kill), `SIGKILL` (force kill), `SIGTSTP` (suspend, Ctrl-Z), `SIGHUP` (hangup on terminal close). Don't memorize the whole list — know the small common set and that the rest exist.

## Job Control

- `Ctrl-Z` sends **SIGTSTP** (terminal stop) — *suspends*, doesn't kill.
- `jobs` — list unfinished jobs with job numbers (`[1]`, `[2]`, …).
- `fg %1` — resume job 1 in the foreground; `bg %1` — resume in the background.
- `cmd &` — start in the background directly; `$!` — PID of the last background job.

**SIGHUP trap:** a backgrounded process is still a *child of the terminal*; closing the terminal sends SIGHUP (hangup) and kills it. Survive with `nohup cmd &` (before) or `disown %1` (after).

## Environment Variables

- `FOO=bar` — local to the current shell only.
- `export FOO=bar` — puts `FOO` in the environment block every child process inherits.
- `printenv` lists current env vars; `unset FOO` removes one.
- Convention: env vars are ALL_CAPS (`HOME`, `PATH`, `DEBUG`); local shell vars are lowercase.
- **Per-command prefix (no `export` needed):** `DEBUG=1 command` — putting an assignment *before* a command sets that variable in that single command's environment only, without touching the current shell. `DEBUG=1 DEBUG_LOG=on ./prog` launches the program with both vars set just for that run.
- **Spawn-a-shell to inspect a var:** `bash -c 'echo $DEBUG'` starts a fresh shell, prints `$DEBUG`, and exits — a quick way to confirm what value a variable has in a subprocess's environment. Prefix `DEBUG=1` when you launch it and the spawned shell sees that value: `DEBUG=1 bash -c 'echo $DEBUG'` → `1`.
- These two ideas meet in debugging: `bash -c` gives you an isolated shell to check a variable, and the `VAR=val cmd` prefix lets you inject a value for one invocation instead of exporting it globally.

## Return Codes & Boolean Operators

- Exit code `0` = success; nonzero = failure. `$?` holds the last command's code.
- A successful command exits `0`; to **force a specific exit** yourself, use the `exit N` built-in (`N` is the status code to return; if omitted, the shell exits with the status of the last command executed). This is how scripts abort on failure:
  ```bash
  mkdir /root/secret || exit 1   # if mkdir fails, the script exits with code 1 and the lines after it never run
  ```
  To *read back* `$?` after a command, check it on its own line **before** any other command runs — a later command overwrites it:
  ```bash
  grep -q "needle" file.txt
  echo "grep exited with code $?"   # 0 if found, 1 if not
  ```
- `&&` / `||` are **short-circuiting** operators on return codes, not values:
  - `grep -q pat file && echo found` — runs only if grep succeeded (0).
  - `grep -q pat file || echo "not found"` — runs only if grep failed.
- `if`/`while` also test return codes. See also [[Shell Positional & Special Shell Parameters]] for the special parameters a script receives.

## Aliases

`alias ll='ls -lh'` — the shell expands `ll` to `ls -lh` *before* running it. No space around `=`. Aliases can't take arguments mid-command (use functions for that); `\ll` bypasses, `unalias ll` removes.

## Dotfiles

Plain-text config files whose names start with `.` (e.g. `~/.bashrc`, `~/.gitconfig`, `~/.vimrc`, `~/.tmux.conf`, `~/.ssh/config`) — hidden from the default `ls` by convention. Organize them in a version-controlled folder and symlink into place for portability and quick re-install.

## Terminal Multiplexers (tmux)

tmux runs several shell sessions in one terminal via **sessions → windows → panes**, and lets you **detach** (`<C-b> d`) and **reattach** (`tmux a`) later — invaluable on remote machines (replaces `nohup` tricks).

## SSH

`ssh alice@server` opens a remote shell; key-based auth (public-key crypto) is preferred over passwords. SSH runs commands on remote machines and can be piped like any command — quoting decides whether a pipe runs locally or remotely. See the dedicated page: [[SSH — Public-Key Auth & Remote Commands]]. `scp`/`rsync` copy files; `~/.ssh/config` stores per-host defaults.

## Key Takeaways

1. A signal is a *message* a process may react to — not a forced kill (except SIGKILL).
2. Job control = signals + the shell's bookkeeping (`jobs`, `fg`, `bg`).
3. Background jobs die with the terminal (SIGHUP) unless `nohup`/`disown` protect them.
4. `export` makes a variable heritable; `alias` is pre-run shorthand; dotfiles are the config convention.
