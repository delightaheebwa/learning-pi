<!-- provenance: status=verified | source=https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html ; https://missing.csail.mit.edu/2020/shell/ | verified-by=fact-check-agent | date=2026-10-26 -->

# Exit Codes & Short-Circuit Control Flow

> Source: Lecture 2 written notes (website, Fri 2026-08-21) + MIT Missing Semester (Command-line Environment). Ingested 2026-08-24.

## Every command returns a number

Convention: **0 = success**, **any non-zero = failure**. Read the last command's code with `$?`:

```bash
mkdir /root/secret || exit 1   # guard: bail out of the script if mkdir fails
echo $?                        # -> the code mkdir exited with
```

Gotcha: `echo $?` itself succeeds, so asking twice yields `0` the second time — capture or branch on it immediately.

## Choosing your own code: the `exit` built-in

`exit NUM` terminates the script (or shell) with code NUM. Fatal paths in scripts should `exit 1` so callers — cron, CI, other scripts — can detect the failure.

## Boolean operators act on return codes, not values

Unlike `&&` and `||` in ordinary programming languages (which combine true/false *expressions*), the shell versions dispatch on the previous command's **exit status**:

```bash
false || echo "runs — || executes the right side on failure"
true  && echo "runs — && executes the right side on success"
cmd1 && cmd2 || cmd3     # evaluated left-to-right, short-circuiting
```

Both are **short-circuiting**: the right side runs only when the outcome demands it. The same mechanism drives control flow — in `if cmd; then …` and `while cmd; do …`, the condition *is* a command judged by its exit status (see [[MIT Missing Semester — Shell]] § Conditionals; contrast with expression-level [[Short-circuit evaluation]]).

## Fail-fast pattern

Combine with strict mode: `set -e` stops the script on any unexpected failure; explicit guards like `critical_step || { echo "failed"; exit 1; }` document the intended response.

Related: [[Environment Variables (Shell)]] · [[Shell Loops]]

## Sources

- https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html
- https://missing.csail.mit.edu/2020/shell/
