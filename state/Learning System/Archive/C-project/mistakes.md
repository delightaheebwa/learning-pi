# Mistakes — C project era (archived 2026-08-25, refiled 2026-09-09)

> Rows kept verbatim when the Terminal System Monitor strand was archived;
> no longer in the review queue. Reference only.

| Date | Concept | Question | Expected | Error Type | Self-Attribution | Status | Retries | Next Retry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-20 | GCC Compilation Stages | Map flags to stages | -E preprocess, -S compile->asm, -c assemble->.o, link no-flag | structural | Mapped -r/-e, missed -E/-S/-c | active | 0 | 2026-08-24 |
| 2026-08-21 | C Integer Mechanics (Underflow & Type Promotion) | Why does (used/total)*100 give 0% for 8M/16M? | Integer division truncates before float; lead with 100.0 * to promote | structural | Inverted cause/cure (called promotion the problem) | active | 0 | 2026-08-24 |
| 2026-08-23 | C Memory Regions (Stack vs Heap vs Swap) | Does returning stack array leak or dangle? | Dangling (frame destroyed); stack cannot leak, only heap leaks | structural | Inverted dangling vs leak | active | 0 | 2026-08-24 |
| 2026-08-23 | C String Buffer Boundaries | Why char buf[SIZE+1]? | +1 for NUL terminator; validate before strcpy, else overflow | deviation | Named NUL but missed bounds-check-before-copy | active | 0 | 2026-08-24 |
