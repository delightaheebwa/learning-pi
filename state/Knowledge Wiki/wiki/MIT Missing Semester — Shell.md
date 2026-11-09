<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# MIT Missing Semester — Shell

**Source:** [Course Overview + The Shell](https://missing.csail.mit.edu/2026/course-shell/)
**Track:** SWE (Software Engineering Fundamentals)
**Ingested:** 2026-07-28

## What is the Shell

The shell is a **textual interface** to your computer. Instead of clicking buttons in a GUI, you type commands to run programs, give them input, and inspect their output.

- **Terminal** — the visual app that opens a window to the shell
- **Shell** — the actual program inside the terminal that interprets commands (bash, zsh, fish, etc.)
- **Prompt** — the line the shell prints to indicate it's ready: `hostname:~$` (the `~` is your home directory, `$` means normal user, `#` means root)

## Basic Commands

- `date` — prints the current date/time
- `echo [text]` — prints its arguments back to you
- `echo $PATH` — prints the PATH environment variable
- Commands are split by whitespace. Use quotes or backslash for spaces/special characters

## Shell Navigation

- `pwd` — print working directory (where am I?)
- `cd [path]` — change directory (built into the shell, not a program)
- Paths: absolute (`/home/workspace`) vs relative (`Documents/notes.md`)
- `.` = current directory, `..` = parent directory, `~` = home directory
- Tab completion works for paths and commands

## man & Documentation

- `man [program]` — open the manual page (q to quit, arrows to scroll, / to search)
- `[program] --help` — most programs accept this for a quick reference
- `tldr [program]` — practical examples (community-maintained, more readable)

## PATH & Program Discovery

The shell needs to find the program file when you type a name like `date`.

- `$PATH` — environment variable listing directories separated by `:`
- The shell searches each directory in `$PATH` in order
- `which [program]` — shows which file the shell will run
- `ls /bin` — list all programs in /bin (one of the PATH directories)
- Bypass PATH by giving the full path: `/usr/bin/date`

## ls & File Listing

- `ls [path]` — list directory contents
- `ls -l` — detailed listing (permissions, owner, size, modification date)
- `ls /bin` — list everything available on the system
- Consider [eza](https://eza.rocks/) for a more human-friendly `ls`

## Key Takeaways

1. The shell is your primary tool for controlling a computer programmatically
2. The prompt tells you who you are ($ vs #) and where you are (~)
3. Programs are just files that live in directories listed in $PATH
4. cd is built into the shell because it changes the shell's own state
5. man pages are the canonical documentation source — learn to read them

## Shell Tools

### Basic File Tools (cat, sort, uniq, head, tail)

- `cat file` — print the contents of `file` to stdout
- `sort file` — print lines of `file` in sorted order
- `uniq file` — eliminate **consecutive** duplicate lines from `file`
- `head file` — print the first few lines of `file`
- `tail file` — print the last few lines of `file`
- Install [`bat`](https://github.com/sharkdp/bat) over `cat` for syntax highlighting and scrolling

### grep & ripgrep

- `grep pattern file` — find lines matching `pattern` in `file`
- `pattern` is a **regular expression** — very expressive for complex patterns
- `grep -r` recursively searches a directory
- `grep -c pattern file` — count matching lines instead of printing them (same as `grep pattern file | wc -l`)
- grep works **line-by-line** — a pattern can't span multiple lines, so multiline HTML (`<h3>` on one line, `</h3>` on another) breaks `grep "<h3>.*</h3>"`
- In grep regex, `*` means "repeat the previous character 0+ times" — NOT glob's "match anything". Use `.*` for that
- Install [`ripgrep`](https://github.com/BurntSushi/ripgrep) for a faster, more human-friendly grep
- ripgrep recursively searches the current directory by default

### sed — Stream Editor

- `sed -i 's/pattern/replacement/g' file` — replace all instances of `pattern` with `replacement` in `file` (inline)
- `-i` = edit inline (modifies the file)
- `s/` = substitute command
- Trailing `/g` = replace all occurrences on each line (not just the first)
- `pattern` is a regular expression
- Replacement can refer back to matched groups with `\1`, `\2`, etc.

### find & fd

- `find <dir> -type f -name "*.zip"` — find files by type and name pattern
- `find <dir> -type f -size +100M` — find files larger than 100M
- `find . -name "*.py" -exec grep -l "TODO" {} \;` — find files and run a command on each
- `find . -type f -name "*.*"` — only files with a dot in the name (excludes extensionless files like `README` or `build`)
- `-print0` — print matches separated by NUL bytes instead of newlines; pairs with `xargs -0` for filenames containing spaces
- `-exec CMD {} +` — batch form: ALL matching paths are substituted into ONE command invocation (e.g. `find . -name "*.txt" -exec wc -l {} +` counts lines across every match in a single `wc` run). Contrast the `\;` terminator, which runs the command once PER file — slower on large result sets
- `-exec` runs a command on each matching file; `{}` is replaced by the file path
- Install [`fd`](https://github.com/sharkdp/fd) for a more human-friendly `find`
- fd is faster and has more intuitive defaults (but less portable)

## Shell Tools (continued)

### awk — Column-Oriented Data Processing

`awk` is a programming language for parsing structured text data (like CSVs and log files). Unlike `sed` which edits files, `awk` extracts and processes data by columns.

> **Source scope:** the lecture teaches only `{print $2}` and `-F,` (and points to the exercises for more). Everything below beyond those two — pattern/action pairs, built-in variables, FS/OFS, match operators, FPAT — is expansion from the lecture exercises and practice notes, not verbatim lecture content.

- `awk '{print $2}' file` — prints the second whitespace-separated column of every line
- `awk -F, '{print $1}' file` — comma-separated (CSV) parsing with `-F,`
- `awk '$3 ~ /pattern/ {$4=""; print}'` — filter lines where column 3 matches a pattern, omit column 4
- `awk '$2 > 100 {print $1, $3}'` — filter by numeric column value, reorder output

**Program structure — pattern/action pairs:** `awk '/pattern/ { action }'` — a condition (regex or expression) in front, an action block after. No condition → action runs on every line.

**Built-in variables:** `$0` = the entire line, `$1`, `$2`, … = individual fields, `NF` = number of fields in the current record (so `$NF` is the last field).

**Match operators:** `~` matches a regex (`$1 ~ /pattern/`), `!~` does not match.

**FS vs OFS:** `FS` (input field separator) defines how each line is split into fields — same as `-F,`. `OFS` (output field separator) defines the separator between printed fields — set it in a `BEGIN` block: `awk 'BEGIN { OFS="," } { print $1, $2 }'` prints the two fields joined by a comma.

**FPAT — fields containing the delimiter:** when fields themselves contain the delimiter (e.g. quoted CSV), `FS` breaks. `FPAT` defines what a *field looks like* instead of what splits it:
```bash
awk -v FPAT='[^,]+|"[^"]*"' '{ for(i=1;i<=NF;i++) print $i }'
```

**Classic examples:** `awk -F: '{ print $1 }' /etc/passwd` prints the first field of each `/etc/passwd` line (username); `awk 'BEGIN { OFS="," } { print $1, $2 }'` comma-separates the first two fields of every line.

`awk` can do filtering, aggregation, column reordering, and pattern matching in one pass.

**Extension counting (top-5 pattern):**
```bash
find . -type f | awk -F. '{print $NF}' | sort | uniq -c | sort -nr | head -n 5
```
- `-F.` sets the field separator to the dot; `$NF` (last field) is the extension (e.g. `py` from `main.py`)
- A file with **no dot** (e.g. `README`, `build`) has `NF = 1` — `$NF` prints the whole filename, which gets counted alongside real extensions
- Add `find ... -name "*.*"` to filter extensionless files out first

## Pipes & Pipeline Composition

`|` (pipe) connects the standard output of one program to the standard input of the next. This lets you compose programs like building blocks.

```bash
journalctl | grep "error" | tail -n 10
```

The program before `|` writes to stdout, which becomes the stdin of the program after `|`. Most CLI programs read from stdin when no file argument is given, which is what makes pipes work.

**Pipes run in parallel, not in sequence:** every command in a pipeline is started at once and they run *concurrently*. As one program writes a line, it's consumed immediately by the next command's stdin — you don't wait for the first program to finish before the next starts, so output streams through the pipeline as it's produced.

### Putting It Together

A full pipeline example (SSH log analysis):
```bash
ssh myserver 'journalctl -u sshd -b-1 | grep "Disconnected from"' \
  | sed -E 's/.*Disconnected from .* user (.*) [^ ]+ port.*/\1/' \
  | sort | uniq -c \
  | sort -nk1,1 | tail -n10 \
  | awk '{print $2}' | paste -sd,
```

This extracts the top 10 usernames disconnected from an SSH server, comma-separated — all in one line.

**Where the pipe runs (local vs remote):** with `ssh myserver 'journalctl ... | grep ...' \` followed by a local pipe, the part *inside* single quotes runs remotely, and the `| sed ... | sort ...` chain after the backslash runs **locally** on the streamed remote output. Quoting decides which stages execute on which machine — see [[SSH — Public-Key Auth & Remote Commands]].

**Top-counts pattern:** `sort | uniq -c | sort -nr | head -n 5` — `uniq -c` only counts *consecutive* duplicates, so you must `sort` first. Then `sort -nr` orders by count descending (numeric, reverse). Note `head -n 5` (or `head -5`); plain `head 5` looks for a file named `5`.

### xargs — stdin Lines to Command Arguments

`xargs` bridges the stream world and the argument world: it reads lines from stdin and appends them as positional arguments to a command.

```bash
find . -type f -name "*.sh" | xargs wc -l
```

- Without `xargs`, `find . -type f -name "*.sh" | wc -l` counts the *number of filenames* (lines in find's output), not the lines inside the files
- `xargs` bundles as many paths as possible into one execution: `wc -l ./a.sh ./b.sh`
- **Spaces trap:** default `xargs` splits on spaces/tabs/newlines, so `./my test script.sh` becomes three args (`./my`, `test`, `script.sh`) and `wc` fails
- **Fix:** `find ... -print0 | xargs -0 wc -l` — NUL is the only byte that can never appear in a filename, so `-print0`/`-0` make the split unambiguous

### curl — Websites as Streams

```bash
curl -s https://missing.csail.mit.edu/ | grep -c 'href="/2026/'
```

- `curl URL` fetches a webpage and prints the raw HTML to stdout; `-s` silences the progress meter
- The command line is a browser without a GUI — pipe fetched HTML into `grep` to scrape or count
- `grep -c pattern` counts matching lines directly (equivalent to `grep pattern | wc -l`)
- Standard `grep` is line-by-line, so multiline HTML tags break patterns like `<h3>.*</h3>` (and greedy matching collapses multiple matches on one line). Target a unique single-line attribute instead — e.g. each lecture link appears exactly once as `href="/2026/..."`


#### `curl URL | bash` — the risky convenience

Downloading a script and immediately executing it is convenient but dangerous: unaudited code runs with your user's privileges. Safer: download, review, then execute.

```bash
curl -fsSL https://example.com/install.sh -o install.sh
less install.sh   # inspect before trusting it
bash install.sh
```

Some installers use `bash -c "$(curl -fsSL https://URL)"` — marginally safer in that `bash` interprets the script rather than whatever shell you happen to run, so Bash-specific syntax ("bashisms") won't misfire — but it is still blind execution. Inspection is the actual safety step.

### jq — JSON Processing

`jq` is a dedicated JSON processor for the shell — line-based tools like grep/sed/awk struggle with JSON because objects span multiple lines and nest.

```bash
curl -s https://microsoftedge.github.io/dummy-data/64KB.json | jq -r '.[] | select(.version > 6) | .name'
```

- `jq .` pretty-prints JSON so you can inspect the structure first
- `.[]` unrolls a top-level array into a stream of individual objects
- `select(.version > 6)` keeps only items where the condition is true; `.name` extracts the field
- Keep all the jq steps **inside the single quotes** — pipes outside the quotes are shell pipes and bash will try to run `select`/`name` as commands
- `-r` (raw output) prints strings without JSON quotes, ready for further piping (e.g. into `sort`)


## Shell Redirections & Standard Streams

Every program has three standard streams:
- **stdin (0)** — input (keyboard by default)
- **stdout (1)** — output (terminal by default)
- **stderr (2)** — error output (terminal by default)

Key redirect operators:
- `> file` — redirect stdout to a file (overwrites)
- `>> file` — redirect stdout to a file (appends)
- `< file` — read stdin from a file
- `2> file` — redirect stderr to a file
- `2>&1` — redirect stderr to wherever stdout is going
- `&> file` — redirect both stdout and stderr to a file (shorthand)
- `> /dev/null` — send stdout to the **null device**: a special system file that discards everything written to it (reads return end-of-file). Silences output you don't care about; `2>/dev/null` drops just the error stream

Example:
```bash
ls /nonexistent /tmp > stdout.txt 2> stderr.txt
ls /nonexistent /tmp &> both.txt
find . -name "*.txt" -exec wc -l {} + 2>/dev/null   # batch line-count all matches, errors silenced
```

**Why redirection order matters:**

Redirections are evaluated left to right:
- `> "$LOGFILE" 2>&1` ✅ First stdout goes to the file. Then stderr is pointed at where stdout is going (already the file). Both end up in the file.
- `2>&1 > "$LOGFILE"` ❌ First stderr is pointed at where stdout is currently going (the terminal). Then stdout is redirected to the file. Stderr still prints to the terminal!

### tee

`tee` splits output: it writes stdin to both stdout and a file simultaneously.

```bash
verbose_cmd | tee verbose.log | grep CRITICAL
```

This saves the full log to `verbose.log` while keeping terminal output clean (only CRITICAL lines shown).


**`cp` vs `>` — Copy vs Redirection:**
- `>` **writes** the stdout of a command to a file (overwriting it). You can't do `notes.txt > notes_backup.txt` — Bash would treat `notes.txt` as a command generating output, not as a file to copy.
- `cp` **duplicates** a file on disk. Use `cp notes.txt notes_$(date +%Y-%m-%d).txt` for backups.

## Shell Scripting: Shebang & Execution

### Shebang

The first line of a script tells the system which interpreter to use:
```bash
#!/bin/bash      # Bash shell script
#!/usr/bin/python3  # Python script
```

When the file is executed (e.g. `./script.sh`), the OS reads the shebang and runs the specified interpreter with the script content as input.

### Portable shebang with `env`

Hardcoding `/usr/bin/python3` breaks on machines where Python lives elsewhere. `#!/usr/bin/env python3` lets `env` resolve the interpreter by searching `$PATH`, so the **same script runs unchanged** on any machine. (The notes framed this as: `env` finds the real location by walking `$PATH`.)

### Making a Script Executable

Scripts need the executable permission bit set:
```bash
chmod +x script.sh  # Add execute permission
./script.sh         # Now it runs
```

Without `chmod +x`, you'd need to explicitly invoke the interpreter: `bash script.sh`.

### set Flags (Strict Mode)

Add this at the top of every script to catch errors early:
```bash
set -euo pipefail
```

- `-e` (errexit) — exit immediately if any command fails. Without it, Bash ignores failures and keeps running subsequent lines — which can lead to catastrophic cascading errors (e.g., a failed `cd` followed by `rm -rf *` in the wrong directory).
- `-u` (nounset) — crash on undefined variable usage instead of silently treating it as an empty string. Without it, a typo like `$VAR_DIER` when you meant `$VAR_DIR` silently expands to nothing, which can turn `rm -rf "$VAR_DIER/*"` into `rm -rf /*`.
- `-o pipefail` — if any program in a pipeline fails, the whole pipeline fails. Without it, only the last command's exit status matters, so a failing `grep` in `grep pattern file | cut -d: -f1` goes unnoticed.

**The `|| true` pattern:** When using `set -e`, some commands are *expected* to fail (e.g., `grep` returning 1 when no match found). Append `|| true` to suppress the error:
```bash
grep "alice" users.txt | cut -d: -f1 || true
```

Add `-x` for debug mode (prints each command as it expands, before executing):
```bash
set -x
```

**Security note:** `set -x` expands variables before printing. If your script handles secrets (API tokens, passwords), they'll appear in the trace output. Disable tracing while handling sensitive data:
```bash
set +x   # turn off tracing
# ... work with secrets ...
set -x   # turn tracing back on
```

## Shell Scripting: Conditionals & Loops

### Conditionals

```bash
if command1; then
    command2
    command3
else
    command4
fi
```

`command1` is executed; if it exits with status 0 (success), the `then` branch runs. Status 1+ triggers `else`.

Common test commands:
- `test -f file` / `[ -f file ]` — check if file exists
- `test -d dir` / `[ -d dir ]` — check if directory exists
- `[ "$var" = "string" ]` — string equality check
- `[[ "$var" = "string" ]]` — safer built-in version with fewer quoting gotchas

### Loops

**For loop:**
```bash
for varname in a b c d; do
    echo "$varname"
done
```

**While loop:**
```bash
while command1; do
    command2
done
```

Runs the body repeatedly as long as `command1` succeeds (exit status 0).

**Common pattern — iterate over files with glob:**
```bash
for FILE in *.txt; do
    echo "$FILE"
done
```

**Combined with parameter expansion and command substitution (backup script):**
```bash
for FILE in *.txt; do
    cp "$FILE" "${FILE%.txt}_$(date +%Y-%m-%d).txt"
done
```

## Command Substitution & Arithmetic Expansion

### Command Substitution

Capture the output of a command and use it as an argument:
```bash
for i in $(seq 1 10); do
    echo "$i"
done
```

- `$(command)` — preferred form (can be nested)
- `` `command` `` — older backtick form (avoid for new code; can't be nested)

### Arithmetic Expansion

Bash treats variables as strings by default. For integer math without external tools (`bc`, `expr`), use these two syntaxes:

**Statement syntax — `(( ... ))`:** Used for side effects and evaluation in loops and conditionals.

```bash
((RUN++))              # Increment variable (like RUN=$((RUN + 1)))
((RUN + 5))            # Evaluate expression (result is thrown away)
if (( RUN > 10 )); then ... fi  # Numeric comparison in conditionals
```

Inside `(( ... ))` you don't need `$` on variable names — `((RUN++))` not `(($RUN++))`.

**Value substitution — `$(( ... ))`:** Returns the result as a string.

```bash
echo $((10 + 5))                    # prints 15
NEXT_RUN=$(( RUN + 1 ))            # assign result to variable
echo $(( (a + b) / c ))            # compose with other operators
```

## Parameter Expansion

Bash has built-in string manipulation that avoids spawning external tools like `sed` or `awk`:

- `${var%pattern}` — remove **shortest** matching suffix
- `${var%%pattern}` — remove **longest** matching suffix
- `${var#pattern}` — remove **shortest** matching prefix
- `${var##pattern}` — remove **longest** matching prefix
- `${var:-default}` — use `default` if `var` is unset or empty

**Examples:**
```bash
FILE="notes.txt"
echo "${FILE%.txt}"          # → "notes" (strip extension)
echo "${FILE%.txt}_2026-08-04.txt"  # → "notes_2026-08-04.txt"

PATH="/home/user/docs/report.pdf"
echo "${PATH##*/}"          # → "report.pdf" (basename)
echo "${PATH%/*}"           # → "/home/user/docs" (dirname)

# Fallback for unset variable
DB_HOST=${DB_HOST:-localhost}  # uses "localhost" if DB_HOST is unset
```

**Why it matters:** Parameter expansion runs inside the shell process — no subprocess spawned, no whitespace splitting, no quoting traps. It's the idiomatic way to manipulate strings in Bash.

## Background Jobs

Normally, when you run a command in the terminal, the shell waits for it to finish before showing the next prompt. Appending `&` at the end of a command line runs it in the background — the shell returns to the prompt immediately and the command keeps running.

```bash
stress --cpu 8 &
```

- `&` — run the preceding command in the background (non-blocking)
- `$!` — special variable holding the PID of the most recent background job
- `kill $PID` — terminate a background process (default signal: SIGTERM)
- `jobs` — list all running background jobs attached to the current shell session
- `fg %1` — bring job number 1 back to the foreground

A practical pattern is to start a long-running task in the background, save its PID, do other work, then clean up:

```bash
# WARNING: This script runs forever — Ctrl+C to stop
long_running_task &
TASK_PID=$!
# ... do other work ...
kill $TASK_PID
```

The `$!` PID is ephemeral — it's overwritten every time a new background job starts.

## Shell Built-ins vs External Programs

Some commands (`cd`, `export`, `set`, `alias`, variable assignment) **must** be shell built-ins. Others (`ls`, `mkdir`, `grep`) work fine as external programs.

### Why built-ins exist: Child Process Memory Isolation

When the shell runs an external command, the OS creates a **child process** with its own copy of the parent's memory. The child can modify its own copy, but the OS **physically prevents** it from writing to the parent's memory space. When the child exits, its memory is wiped — any changes it made vanish.

**Implication:** If `cd` were an external program, it would change its own working directory, then exit — leaving the shell's `$PWD` unchanged. The command would be useless.

### Internal shell state (must be modified by built-ins):
- **Current working directory** (`$PWD`) — modified by `cd`
- **Shell/environment variables** (`PATH`, `USER`, custom vars) — modified by `export`, `unset`, assignment
- **Background jobs list** — managed by `bg`, `fg`, `jobs`, `kill`
- **Shell options** — modified by `set`, `shopt`

### External programs (side-effects on filesystem/stdout):
- `ls` reads directory contents and prints to stdout
- `mkdir` asks the kernel to create a folder on disk
- `grep` reads files and prints matches to stdout

These work as child processes because their output goes to the filesystem or stdout — changes persist on disk regardless of process hierarchy.

**Rule of thumb:** If a command needs to change the shell's own memory (variables, working directory, options), it must be a built-in. If it only needs to read/write files or print output, an external program works.

## Text Slicing & Counting (`cut`, `wc`, history)

These round out the editor/CLI toolkit from the Development Environment lesson.

- `cut -d: -f1 /etc/passwd` — extracts fields from each line. `-d:` sets the field **delimiter** (here `:`, the separator in `/etc/passwd`); `-f1` selects the **1st field** (the username). General form: `cut -d DELIM -f N file`.
- `wc -l file` — counts lines; `wc -l < file` gives the *same count but without the filename* in the output.
- `history | wc -l` — counts saved commands. The shell caps history size (often `HISTSIZE` / `HISTFILESIZE` = 1000 or 2000 lines), so this is *saved* commands, not every command ever run since install.

### Why `wc -l < file` hides the filename

The shell intercepts `<` **before** running `wc`: it opens `shopping.txt` itself, connects the raw text stream to `wc`'s stdin, and `wc` never sees the word `shopping.txt`. So `wc -l < shopping.txt` prints just the number; `wc -l shopping.txt` prints `N shopping.txt` because `wc` opened the file by name and reports it. (Contrast `cp`, which needs the filename to copy — you can't do `notes.txt > backup.txt`.)

## Key Takeaways (Remaining)
7. Pipes (`|`) are the shell's composition mechanism — they let you chain programs together
8. Redirections control where input comes from and output goes to
9. The shell has a full programming language (bash) with conditionals, loops, variables, and functions
10. Always use `set -euo pipefail` at the top of shell scripts for safety
11. `chmod +x` makes a script executable — without it, you need to explicitly invoke the interpreter

## File Permissions (ls -l)

The 10-character string from `ls -l` tells you file type and permissions:

- **Char 1** — File type: `d` = directory, `-` = regular file, `l` = symlink
- **Chars 2-4** — Owner permissions (rwx)
- **Chars 5-7** — Group permissions (rwx)
- **Chars 8-10** — Others/everyone permissions (rwx)

Each `rwx` triplet: `r` = read (view contents), `w` = write (edit/modify), `x` = execute (run as program or enter directory). A `-` means that permission is denied.

Example: `drwxr-xr-x` → directory, owner has full access, group and others can read and enter but not modify.

## Wildcards & Globs

- `*` — matches zero or more characters: `report*` matches report.pdf, report2024.txt, report_final.pdf
- `?` — matches exactly one character: `c?t.png` matches cat.png but not cart.png
- `[abc]` / `[0-9]` — matches one character from a set/range: `doc[1-5].txt` matches doc1 through doc5
- `{a,b}` — brace expansion, generates combinations: `file_{draft,final}.txt` creates file_draft.txt and file_final.txt. Does NOT match existing files — it generates strings.

## Bash Quoting

Three quoting mechanisms control how special characters are interpreted:

- **Single quotes `'...'`** — absolute literal. `$USER` stays as the text `$USER`. Cannot include a literal single quote inside.
- **Double quotes `"..."`** — allows `$USER` expansion, `$(command)` substitution, and `\` escapes. Protects spaces and wildcards.
- **ANSI-C quotes `$'...'`** — processes escape sequences like `\n` (newline) and `\t` (tab). `$` and `!` treated as literal.

## GNU Make

### Targets, Prerequisites & Recipes

A Makefile rule has three parts:
```
target : prerequisites
    recipe
```
- **Target** — the output file to build (e.g. `monitor` binary), or an action name (e.g. `clean`)
- **Prerequisites** — input files needed (e.g. `main.c`). Optional — a rule can have none.
- **Recipe** — shell commands that produce the target from prerequisites. **Must start every line with a tab character** (not spaces). This is the most common Makefile mistake.

A rule need not have prerequisites, but it must have a recipe. If a rule doesn't depend on the default goal, it won't be processed unless you invoke it explicitly (e.g. `make clean`).

make builds the target only when it's missing or any prerequisite is newer.

### Timestamp Evaluation

make's core efficiency: compare modification timestamps.
1. Target doesn't exist → rebuild
2. Any prerequisite newer than target → rebuild
3. All prerequisites older → skip ("up to date")
### Makefile as Its Own Prerequisite (Self-Updating Build)

Add `Makefile` to a target's prerequisite list so make rebuilds when the Makefile itself changes:

```
tests/test_meminfo: tests/test_meminfo.c src/meminfo.c src/meminfo.h third_party/acutest.h Makefile
    $(CC) $(CPPFLAGS) $(CFLAGS) tests/test_meminfo.c src/meminfo.c -o $@
```

make compares **timestamps only** — it never inspects content or semantics. Saving any edit to the Makefile (even just adding a comment) bumps its mtime, so make considers the target out of date and recompiles. Expect a comment-only change to be ignored at your own risk: make knows *that* something changed, never *what*.

### Dependency Tree Resolution

make reads rules top-down to build a dependency tree in memory, but executes bottom-up (leaves first). If a prerequisite is missing, make recursively finds and builds it. The first rule in the Makefile is the default goal (what `make` builds with no arguments).

### Intermediate Object Files (.o)

Split compilation into two stages for speed:
1. `gcc -c file.c -o file.o` — compile source to object file (skip linking)
2. `gcc main.o utils.o -o monitor` — link object files into executable

Only changed `.c` files get recompiled. Massively speeds up large projects.

### Make Variables

Variables like `CC = gcc` and `CFLAGS = -Wall -Wextra -std=c17 -g` keep Makefiles clean. Referenced in recipes as `$(CC)` and `$(CFLAGS)`. Change once at the top instead of editing every recipe line.

`CPPFLAGS = -Isrc -Ithird_party` carries preprocessor include paths — the `-I` directories where `#include "meminfo.h"` and `#include "acutest.h"` resolve.

**Test-target pattern (Teach C Lesson 3):**

```makefile
tests/test_meminfo: tests/test_meminfo.c src/meminfo.c src/meminfo.h third_party/acutest.h
	$(CC) $(CPPFLAGS) $(CFLAGS) tests/test_meminfo.c src/meminfo.c -o $@

test: tests/test_meminfo
	./tests/test_meminfo
```

The `test` target depends on the executable, which depends on the test file + module under test + headers — `make test` rebuilds only when those change, then runs the suite.

### Clean Targets & .PHONY

- `clean:` target removes build artifacts (no prerequisites, recipe is `rm -f monitor`)
- `.PHONY: clean` tells make that `clean` is NOT a real file — always run its recipe even if a file named `clean` exists on disk
- Without `.PHONY`, make would skip the recipe if a file named `clean` exists (thinks it's up to date)

### Phony Targets (General)

Targets that don't refer to files but are just actions are called **phony targets**. `clean` is the common example, but any action-only target qualifies.

Phony targets serve two purposes:
1. **Name conflict avoidance** — prevents make from confusing your action with a real file of the same name
2. **Performance** — phony recipes run only on explicit request, not as part of the default goal's dependency chain

**Default goal rule:** the goal is the target make strives to update. It defaults to the first target in the Makefile — but targets starting with `.` are skipped (unless they contain `/`).
