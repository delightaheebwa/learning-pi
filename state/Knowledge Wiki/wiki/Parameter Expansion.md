<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Parameter Expansion

## Core Insight

Bash parameter expansion (`${var...}`) lets you transform variable values inline — strip prefixes/suffixes, provide defaults, substring — without spawning external tools like `sed` or `awk`.

## Key Patterns

| Pattern | What it does | Example |
|---|---|---|
| `${var%pattern}` | Remove shortest **suffix** matching `pattern` | `${FILE%.txt}` → strips `.txt` from end |
| `${var%%pattern}` | Remove **longest** suffix matching `pattern` | `${file}` (where `file=file.tar.gz`) → `%%.*` → strips `.tar.gz` |
| `${var#pattern}` | Remove shortest **prefix** matching `pattern` | `${path#/}` → strips leading `/` |
| `${var##pattern}` | Remove **longest** prefix matching `pattern` | `${file##*/}` → strips everything before last `/` (basename) |
| `${var:-default}` | Use `default` if `var` is unset or empty | `${NAME:-anonymous}` → falls back to "anonymous" |
| `${var:=default}` | Assign `default` to `var` if unset/empty | `${PORT:=8080}` → sets PORT to 8080 if unset |
| `${var:+replacement}` | Use `replacement` if `var` IS set | `${DEBUG:+--verbose}` → adds flag only if DEBUG set |
| `${var:?error}` | Error with message if `var` unset/empty | `${TOKEN:?Missing token}` → exits with error |

## Practical Examples

### File extension stripping (backup loops)
```bash
for FILE in *.txt; do
    cp "$FILE" "${FILE%.txt}_$(date +%Y-%m-%d).txt"
done
```
`notes.txt` → `notes_2026-08-04.txt`

### Extracting basename from path
```bash
fullpath="/home/user/docs/report.pdf"
echo "${fullpath##*/}"   # report.pdf (strips longest prefix matching */)
echo "${fullpath%/*}"    # /home/user/docs (strips shortest suffix matching /*)
```

### Default values
```bash
echo "Hello, ${USER:-stranger}"   # prints username or "stranger"
${1:?Usage: script.sh <filename>} # exits with error if no argument
```

## Why It Matters

- **No subprocess overhead** — parameter expansion runs inside the shell process, unlike `sed`, `awk`, or `cut` which fork a child process
- **Essential for safe scripting** — combined with quoting (`"${FILE%.txt}"`), it handles filenames with spaces correctly
- **Core building block** — loops, argument validation, path manipulation, and conditional defaults all rely on it

## Gotchas

- `%` removes from the **end**, `#` removes from the **beginning**
- Single `%`/`#` = shortest match; double `%%`/`##` = longest match
- Without quotes, filenames with spaces will word-split
- Pattern matching uses glob-style (`*`, `?`, `[...]`), NOT regex

## Related

- [[Shell Loops]] — parameter expansion + for loops + glob patterns
- [[Bash Quoting]] — why quoting around `${var}` matters
- [[Command Substitution & Arithmetic]] — combining `$(...)` with parameter expansion
- [[MIT Missing Semester — Shell]] — source course

## Sources

- Source: Gemini conversation — shell scripting safety flags and file operations (2026-08-04)
- Reference: https://missing.csail.mit.edu/2026/course-shell/
- Reference: https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
