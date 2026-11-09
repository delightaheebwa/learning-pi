<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Process Substitution (<(CMD))

**Process substitution** runs a command, sends its output to a temporary file (typically a `/dev/fd/N` pipe), and substitutes that file's path in place of `<(CMD)`. It lets you hand command output to another command that expects a **file path argument** rather than stdin.

## Syntax

```bash
diff <(ls dir1) <(ls dir2)     # compare the listings of two directories
```

The shell rewrites `<(ls dir1)` to a path like `/dev/fd/63` and `<(ls dir2)` to `/dev/fd/62`, then runs `diff /dev/fd/63 /dev/fd/62`. `diff` reads them as ordinary files; it never knows they are live command output.

## When to use it

- A command takes **file paths** as inputs (e.g. `diff`, `comm`, `cmp`) but you want to feed it filtered command output instead of writing temporary files.
- Compare or combine the output of two (or more) commands directly.

## Process substitution vs command substitution

| Feature | Command substitution `` `cmd` `` / `$(cmd)` | Process substitution `<(cmd)` |
|---------|---------------------------------------------|-------------------------------|
| Produces | The command's **output text** (a string) | A **file path** to the output |
| Use when | You want the output as a value / argument | The receiving command wants a **file path** |
| Example | `now=$(date)` | `diff <(ls a) <(ls b)` |

> **Common confusion (from lecture notes):** the lecture's second "process substitution" paragraph mistakenly says `<(CMD)` *captures output into a variable* — that is **command substitution** (`$(CMD)`), not process substitution. Process substitution yields a file path, not a variable assignment.

## Related

- [[Positional & Special Shell Parameters]] — `$0`, `$1`–`$9`, `$@`, `$#`
- [[Command Substitution & Arithmetic Expansion]] — `$(cmd)` captures output as a value
- [[Shell Redirections & Standard Streams]] — stdin/stdout/stderr and `<` / `>`
- [[Shell Arguments & the Untyped-Variable Model]] — everything is a string

## Sources

- https://www.gnu.org/software/bash/manual/html_node/Process-Substitution.html
