<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Shell Arguments & the Untyped-Variable Model

Two foundational facts about how the shell handles data:

## 1. Arguments are plain strings

Every argument you pass on the command line arrives inside the script as a **plain string**. There is no type attached — `"42"` and `42` are the same kind of thing to the shell until you explicitly do arithmetic (via `$(( … ))`) or a test.

## 2. Shell variables have no types — they are all strings (by default)

The shell does not track integer / float / boolean types *by default*. A plain variable holds a string; "type" is implied by *how you use it* (e.g. `(( x + 1 ))` treats the string as a number; `[[ -n $x ]]` treats it as text).

> Nuance: bash *can* optionally tag a variable as integer with `declare -i x`, after which assignments do arithmetic. But you almost never need it — `$(( … ))` does the math inline — and unadorned assignments are always strings. The lecture's "all strings" framing is the right mental model for everyday scripting.

```bash
x=42          # x is the string "42"
y=x+1         # y is the string "x+1"  (no math happened!)
z=$(( x + 1 ))# z is the string "43"  (arithmetic expansion forced the math)
```

## Consequences

- **Word-splitting & quoting:** because values are untyped strings, unquoted expansion (`$var`, `$@`) is split on whitespace and globs are expanded — so you quote (`"$var"`, `"$@"`) to preserve a value as a single unit.
- **Command vs process substitution interplay:** you capture command output into a variable with command substitution (`$(cmd)`), and you feed output to a file-path-hungry command with process substitution (`<(cmd)`). Both treat output as text; the difference is *variable vs file path*.
- **Environment variables are the same strings, just exported** into the block child processes inherit (see [[MIT Missing Semester — Command-line Environment]]).

## Related

- [[Positional & Special Shell Parameters]] — how arguments reach a script (`$1`, `$@`, `$#`, `$0`)
- [[Command Substitution & Arithmetic Expansion]] — forcing math / capturing output
- [[Parameter Expansion]] — string manipulation without spawning tools
- [[MIT Missing Semester — Command-line Environment]] — environment variables, `$?`, `export`

## Sources

- Bash manual: https://www.gnu.org/software/bash/manual/bash.html
- MIT Missing Semester 2026 — Command-line Environment: https://missing.csail.mit.edu/2026/command-line-environment/
