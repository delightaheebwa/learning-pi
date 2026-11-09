<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Sentinel Values vs Presence Flags

## Overview

*(Scope: base content ingested 2026-08-07 from Teach C Lesson 3 + Gemini notebook 8870dcd71e2919f5; the "Sentinel in the Smoke Test" section (2026-08-15) is from notebook e338aa05afbec7a2.)*

A **sentinel value** is a special value chosen to mark "absent" or "not found" (e.g. `0` or `-1` meaning "missing"). The trap: if that value is also a legitimate value in the domain, you can't tell a real zero from a missing field.

## The Trap

Parsing `/proc/meminfo` into a struct that returns success when the fields are non-zero:

```c
return (out->total_kb != 0 && out->available_kb != 0) ? 0 : -1;
```

Two failure modes:

1. **Valid zeroes:** `MemAvailable: 0 kB` (an out-of-memory container) is a *successful parse* of zero, but the check treats it as a parsing failure (false negative).
2. **Accidental true negative:** a field never present stays `0` (thanks to `struct memory memory = {0}`), which happens to satisfy the error branch — but only because `0` was recycled to mean both "uninitialized" and "zero memory". The check is correct *by coincidence*, not by design.

Reusing an ordinary value to represent *structural* status (present vs missing) is a classic systems-programming trap: `0` is simultaneously a valid quantity and an absence marker — ambiguous.
## The Naive Fix the Lesson Teaches (Teach C Lesson 3)

*(Scope: this section documents the Teach C Lesson 3 practice exercise from an earlier ingest — external to the Gemini session reviewed in this update.)*

The lesson's practice fix is the two-field sentinel check this page replaces:

```c
return out->total_kb != 0 ? 0 : -1;   // lesson starter: only checks total
// practice fix — still a sentinel check:
return (out->total_kb != 0 && out->available_kb != 0) ? 0 : -1;
```

Requiring both fields is better than one, but both are sentinel checks on payload values — the presence-flag version below is the robust replacement.

## The Fix: Separate Presence from Value

*(Scope: the Gemini 2026-08-15 session names presence flags as one of the two standard patterns — "Sentinel Values" vs "Presence Flags: track explicitly whether the key was found (e.g. `bool has_available`)". The detailed struct/code implementation below is an expansion written by the implementer on top of that mention, plus the Teach C Lesson 3 seam context.)*

**Explicit presence flags:**

```c
struct memory {
    unsigned long total_kb;
    unsigned long available_kb;
    bool has_total;
    bool has_available;
};
```

Inside the parse loop, set the flag when the key is matched:

```c
if (strcmp(key, "MemTotal") == 0) {
    out->total_kb = value;
    out->has_total = true;
}
```

Return success on structural presence, not on non-zero payload:

```c
return (out->has_total && out->has_available) ? 0 : -1;
```

`true != false` checks are valid but redundant — write `out->has_total` directly.

**Alternatives:** bitmask flags (`found_mask |= MEM_TOTAL_BIT`) checked after the loop, or field counters.

## Sentinel in the Smoke Test (continuation, 2026-08-15)

A follow-up session extended this into a live-system smoke test with the `{0}` default:

```c
struct memory memory = {0};
TEST_CHECK((read_meminfo("/proc/meminfo", &memory) == 0) &&
           (memory.total_kb > 0) &&
           (memory.available_kb <= memory.total_kb));
```

The trap: if `MemAvailable` is missing from `/proc/meminfo`, `available_kb` stays `0` (from `{0}` init) and `0 <= total_kb` **passes silently** — the smoke test reports green on fake data. `0` is simultaneously a valid quantity and an absence marker, so it cannot distinguish *parsed zero* from *never set*.

**The `ULONG_MAX` sentinel fixes it:** initialize `available_kb = ULONG_MAX` before scanning; after parsing, a value still equal to `ULONG_MAX` means the key was never found. The smoke test then proves three facts at once:

```c
TEST_CHECK((read_meminfo("/proc/meminfo", &memory) == 0) &&
           (memory.total_kb > 0) &&                              // MemTotal found & valid (also guards divide-by-zero)
           (memory.available_kb <= memory.total_kb) &&           // physical sanity
           (memory.available_kb != ULONG_MAX));                  // MemAvailable actually found
```

**When sentinel vs flags:** a sentinel is safe only when the chosen value is *outside the legitimate domain* — `ULONG_MAX` for memory sizes is fine, `0` is not (it is a valid quantity). Presence flags (`has_available`) work universally and are the robust choice when no safe sentinel exists (see Overview). Both solve the same problem: decoupling structural presence from numeric payload.

## Key Insight

- Decouple *structural presence* from *numeric payload*. Presence is tracked by flags; the value stores only the quantity.
- A sentinel works when the sentinel value is outside the legitimate domain (`ULONG_MAX`); `0` fails because it is a valid quantity.
- A `{0}` default silently turns "field missing" into "zero", which can pass `<=` sanity bounds — green tests on fake data.
- C `bool` is `int` under the hood, so `x != false` is exactly `x != 0` — true for any nonzero value (including a negative `int`), and the expression evaluates to `int`, not `bool`. *(clarification added by implementer; `true`/`false` checks discussed in Teach C Lesson 3)*

## Sources

- Gemini Socratic tutoring on parsing `/proc/meminfo` (notebooks: https://gemini.google.com/app/8870dcd71e2919f5, https://gemini.google.com/app/e338aa05afbec7a2)
- Teach C Course — Lesson 3: Acutest and the Parser Seam (practice exercise)
- C `_Bool` / `bool` (cppreference): https://en.cppreference.com/w/c/types/boolean
- `/proc/meminfo` (kernel docs): https://www.kernel.org/doc/Documentation/filesystems/proc.rst
