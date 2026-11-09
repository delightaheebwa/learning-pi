# Command-line Environment (B2)

**Mission:** SWE Foundations — Stage 0 · **Prereqs:** B1 (Shell) · **Status:** done
**Colors:** Process
**Source:** https://missing.csail.mit.edu/2026/command-line-environment/
**Date:** 2026-08-18

## Core

Probe result: the learner already held env vars, return codes, tmux's purpose, aliases, and dotfiles; the single gap was **signals → job control**. This lesson taught that gap fresh and *verified* the rest.

### Step 1 — A signal is a software interrupt

**Unconditional truth:** A signal is a short asynchronous message the kernel (or another process) delivers to a process — a "software interrupt" — that makes the process stop what it's doing and react.

**Motivated discovery:** A hardware interrupt pokes the CPU mid-execution ("device has data"); a signal is the same idea one level up — the *kernel pokes a running process*. The key consequence: the receiving process gets to *decide* how to respond (run a handler, ignore it, or take the default action, often terminate). That is why Ctrl-C "sometimes fails to stop a program" — the target gets a vote.

### Step 2 — The graceful-to-hard kill ladder

| Signal | Sent by | Catchable? | Purpose |
|---|---|---|---|
| SIGINT | `Ctrl-C` | Yes | polite interrupt |
| SIGTERM | `kill <pid>` | Yes | "exit gracefully, clean up first" |
| SIGKILL | `kill -9 <pid>` | **No** | nuclear option — always works, skips cleanup |

**Rule:** try SIGINT/Ctrl-C → `kill` (SIGTERM) → only if it still won't die, `kill -9`. SIGKILL's downside is orphaned child processes / unsaved state, because the process gets no chance to clean up.

### Step 3 — Suspend & resume: Ctrl-Z, fg, bg, jobs

- `Ctrl-Z` sends **SIGTSTP** (terminal stop) — *suspends*, doesn't kill.
- `jobs` lists unfinished jobs; `fg %1` resumes in foreground, `bg %1` resumes in background.
- `cmd &` starts in the background directly; `$!` holds the last background PID.

**SIGHUP trap:** a backgrounded process is still a *child of the terminal*; closing the terminal sends SIGHUP and kills it. Survive with `nohup cmd &` (before) or `disown %1` (after).

### Verified (prior knowledge, connected not re-taught)

- `export FOO=bar` → variable goes into the environment block every child inherits; plain `FOO=bar` stays local to the shell.
- Dotfiles are hidden (leading `.`) by convention so config stays out of the default `ls` listing.

## Quiz (5/5)

Tier 1 retrieval — SIGKILL uncatchable; Ctrl-Z→`bg` = suspend-then-background; interleaved Make timestamp-rebuild.
Tier 2 higher-order — SIGKILL accepts uncleaned junk (predict); background job is a child → SIGHUP → `nohup`/`disown` (explain why).

## Glossary additions

→ proposed (pending user approval): **Signal**, **Job control**.

## Learning record

→ `Learning Records/0001-signals-and-job-control.md` (Feynman explain-back passed; Bloom: Evaluate).

## Next steps

B3 — Development Environment & Tools (editors, Vim, shell scripting), per CURRICULUM.md rotation (A5 next, then B3).
