<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Parsing Text with sscanf %n

## Overview

Robust line-by-line parsing of structured text (like `/proc/meminfo`) in C. Two classic traps: `strchr(line, '\n')` pointer jumping that silently skips lines, and `%n` pointer advancement that leaves trailing units behind.

## Trap 1: strchr Is Not Line-Aware

Advancing with `strchr`:

```c
line = strchr(line, '\n');
if (line == NULL) break;
line++;
```

- **Missing trailing newline on the last line:** `strchr` returns `NULL` and the loop breaks cleanly — the last line *was* already parsed by `sscanf`. Fine.
- **Missing newline in the *middle* of the buffer:** `strchr` scans forward through the *entire remaining string* and lands on the next `\n` further down — silently jumping over unread lines. Data is dropped without an error. `strchr` has no concept of "the current line".

## Trap 2: %n Reports Match Progress, Not Lines

`sscanf(line, "%31[^:]: %lu%n", key, &value, &consumed)` — `%n` (with an `int *`) reports how many characters were consumed *up to that point*.

- `%lu` stops at the first non-digit — so on `"MemTotal: 1000 kB"`, `consumed` stops right after `1000`, leaving `" kB"` behind.
- Advancing `line += consumed` then leaves the pointer at `' '`, and a whitespace-skip loop (`while (*line == ' ' || *line == '\n') line++;`) stops at `'k'` — the next `sscanf` **does not fail**: `%[^:]` swallows newlines, so on `"kB\nMemAvailable..."` it reads key `"kB\nMemAvailable"` up to the colon and `%lu` parses the value → `sscanf` returns 2 with a garbage key. `strcmp` misses, the value is silently lost, and the loop only dies on the following iteration when the leftover `" kB"` can't match.
- **Fix:** match the full line pattern so `%n` captures everything: `sscanf(line, "%31[^:]: %lu kB%n", ...)`, or keep `strchr`-based line advancement for the whole line instead.

## Working Pattern (Common Case)

```c
const char *line = text;
while (line != NULL && sscanf(line, "%31[^:]: %lu", key, &value) == 2) {
    if (strcmp(key, "MemTotal") == 0) out->total_kb = value;
    if (strcmp(key, "MemAvailable") == 0) out->available_kb = value;
    line = strchr(line, '\n');
    if (line != NULL) line++;
}
```

**Caveat:** this loop still returns success based on non-zero payloads (`total_kb != 0 && available_kb != 0`) — the sentinel-value flaw from [[Sentinel Values vs Presence Flags]]. The line advancement here is solid, but pair it with presence flags for a fully correct parser.

Advance past what `sscanf` consumed (or read line-by-line with `fgets` / `strtok_r`) rather than hunting for `\n` blindly.

## Key Insight

- `sscanf` stops scanning at the first non-matching byte — it reads tokens, not lines.
- `strchr` finds the *first* newline anywhere ahead, not the one ending the current line.
- `%n` reports characters consumed in the format match, not where the line ends. The pointer must jump by *consumed bytes*, and the format string must consume the trailing unit — or `line += consumed` leaves `" kB"` behind.
- The two traps are independent: the `strchr` trap affects *any* line-by-line parser; the `%n` trap only bites when advancing by `%n`-consumed bytes.
- Related: [[Sentinel Values vs Presence Flags]] — the return-check half of this parser's correctness.

## Sources

- Gemini Socratic tutoring on parsing `/proc/meminfo` (notebook: https://gemini.google.com/app/8870dcd71e2919f5)
- `fscanf`/`sscanf` (cppreference): https://en.cppreference.com/w/c/io/fscanf
