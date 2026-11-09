<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Shell Built-ins & Process Isolation

## Core Insight

Some commands **must** be built into the shell because they modify the shell's own internal state (working directory, variables, environment). The OS enforces **memory isolation** between parent and child processes — a child process physically cannot write to its parent's memory. So any command that needs to change the shell itself must run inside the shell process, not as a separate program.

## Why `cd` Is a Built-in

If `cd` were an external program:
1. Shell forks a child process
2. Child process changes **its own** working directory
3. Child exits
4. Shell's `$PWD` is unchanged — you're right back where you started

The child process's directory change **dies with it**. The parent shell's memory is untouched.

## What Counts as Internal Shell State

| State | Example | Modified by |
|---|---|---|
| Current working directory | `$PWD`, `$OLDPWD` | `cd` (built-in) |
| Shell/environment variables | `PATH`, `USER`, custom vars | `export`, `unset`, `alias`, `VAR=val` |
| Background jobs | Job list, PIDs, status | `bg`, `fg`, `jobs`, `kill` |
| Shell options | Strict mode, history settings | `set`, `shopt` |
| Command history | Previous commands | `history` (built-in) |

All of this lives in the **shell process's own RAM**. The OS's memory isolation guarantees no child process can touch it.

## Built-ins vs External Programs

### Must be built-in (modify shell state):
- `cd` — changes working directory
- `export` — sets environment variables
- `source` (`. script.sh`) — runs script in current shell context
- `set` — modifies shell options
- `alias` — creates command aliases
- Variable assignment (`VAR=value`) — writes to shell memory

### Can be external (filesystem side-effects only):
- `ls` — reads directory, prints to stdout
- `mkdir` — creates folder on disk
- `grep` — reads files, prints to stdout
- `cp`, `mv`, `rm` — filesystem operations
- `curl` — network I/O

The pattern: if the command's **result persists on disk or stdout** (outside the shell process), it can be external. If it must **change something in the shell's memory**, it must be built-in.

## How to Check

```bash
type cd        # "cd is a shell builtin"
type ls        # "ls is /usr/bin/ls"
type echo      # "echo is a shell builtin"
type grep      # "grep is /usr/bin/grep"
```

## Why This Matters

- **Performance** — built-ins skip the fork/exec overhead
- **Correctness** — built-ins actually modify shell state; external copies can't
- **Debugging** — understanding why `cd script.sh` doesn't change your directory (child process isolation)
- **Security** — understanding that `export` in a script doesn't affect the calling shell

## Related

- [[Shell Navigation & Paths]] — practical `cd` usage
- [[Shell Redirections & Streams]] — stdout/stderr, pipes
- [[Shebang & Script Execution]] — script execution context
- [[MIT Missing Semester — Shell]] — source course

## Sources

- Source: Gemini conversation — Socratic tutoring on shell built-ins, child process isolation, internal state (2026-08-04)
- Reference: https://missing.csail.mit.edu/2026/course-shell/
- Bash built-in commands (manual): https://www.gnu.org/software/bash/manual/html_node/Shell-Builtin-Commands.html
- fork/exec & process isolation (Wikipedia): https://en.wikipedia.org/wiki/Fork_(system_call)
