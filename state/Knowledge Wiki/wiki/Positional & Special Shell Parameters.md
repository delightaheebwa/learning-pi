<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Positional & Special Shell Parameters

When you run a program or script, **arguments arrive as plain strings**. Inside the script you reach them through special shell syntax — not named parameters.

## Positional parameters

| Syntax | Meaning |
|--------|---------|
| `$0` | Name of the program / script being run |
| `$1`, `$2`, … `$9` | The 1st through 9th argument, in order |
| `${10}`, `${11}`, … | 10th+ argument — **must use braces** (`$10` is read as `$1` followed by a literal `0`) |
| `$#` | Total number of arguments passed |
| `$@` | All arguments as a list (one per original argument) |

Example:
```bash
# ./greet.sh Alice Bob
echo "Program: $0"      # ./greet.sh
echo "First:  $1"       # Alice
echo "Count:  $#"       # 2
echo "All:    $@"       # Alice Bob
```

## Why this matters

- **The shell is stringly typed.** Every argument is a string; arithmetic/text logic happens later. This is why quoting (`"$@"`) matters — unquoted `$@` word-splits each argument on whitespace, which breaks arguments containing spaces.
- `$0` tells you *which* program is executing — useful in error messages (`echo "$0: cannot open $1" >&2`) and in scripts that behave differently based on the name they were invoked as.
- Beyond `$9`, always brace: `$10` ≠ the 10th argument.

## Related

- [[Shell Arguments & the Untyped-Variable Model]] — arguments are strings; shell variables have no types
- [[Command Substitution & Arithmetic Expansion]] — turning command output / math into values
- [[Process Substitution]] — feeding command output to a command that expects a *file path*
- [[Parameter Expansion]] — `${var%suffix}` style string surgery on variables

## Sources

- https://www.gnu.org/software/bash/manual/html_node/Special-Parameters.html
