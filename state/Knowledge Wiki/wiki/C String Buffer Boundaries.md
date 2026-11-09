<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# C String Buffer Boundaries

## Overview

C strings are null-terminated, so every buffer must reserve one extra byte for the `'\0'`. Getting this wrong at *maximum* input lengths is a classic hidden bug — exactly the kind boundary testing surfaces.

## The +1 Null-Terminator Bug

The database tutorial stored `username` and `email` in structs sized to the column max:

```c
char username[COLUMN_USERNAME_SIZE];      // 32 bytes
```

Inserting a username of exactly 32 characters wrote `'\0'` **out of bounds**, corrupting the next field (or crashing). The fix:

```c
char username[COLUMN_USERNAME_SIZE + 1];  // 33 bytes — room for the terminator
```

The test that caught it: inserting strings of the maximum expected length and asserting the row prints back intact.

## sscanf → strtok

`sscanf()` into fixed buffers can overflow on long inputs — it copies without bound checks. The tutorial replaced it with `strtok()` (split the input into tokens) plus explicit `strlen()` checks, validating each field's length *before* copying into the struct. Validate first, copy second.

## What Boundary Tests Surface (from Part 4)

- **Max payload sizes** — strings at exact `COLUMN_USERNAME_SIZE` / `COLUMN_EMAIL_SIZE` limits (catches missing +1).
- **Overflow** — strings beyond max limits → clean parser error, not a crash.
- **Capacity** — inserting 1,401 rows into a 1,400-row table → table-full error state.
- **Invalid input types** — negative IDs → clean validation error.

Happy-path tests miss all four; boundary tests prove the code fails *cleanly*.

## One Line Summary

Boundary-test at maximum lengths and beyond: a clean error beats silent corruption, and `+ 1` for the null terminator is non-negotiable.

## Sources

- cstack — Let's Build a Simple Database, Part 4: https://cstack.github.io/db_tutorial/parts/part4.html
- Gemini primary-source reading guide (notebook: https://gemini.google.com/app/f3ceade4034d6bf0)
