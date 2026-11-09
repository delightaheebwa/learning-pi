<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# C Integer Mechanics (Underflow & Type Promotion)

## Overview

Two silent C integer traps sit in the middle of the `/proc/meminfo` percentage calculation. Both are invisible on happy-path data and both produce wildly wrong numbers on the edge — which is exactly why the smoke-test guards exist (see [[Static Fixtures & Boundary Cases]] and [[Sentinel Values vs Presence Flags]]).

The monitoring code at issue:

```c
unsigned long used_kb = memory.total_kb - memory.available_kb;   // subtraction
double used_percent   = 100.0 * used_kb / memory.total_kb;        // percentage
```

## Trap 1 — Unsigned Underflow (Not Negatives)

`unsigned long` **cannot hold a negative sign** — it only represents `0 … 2^64−1` (on 64-bit). So when `available_kb > total_kb`, `total_kb - available_kb` does **not** become a negative number.

Instead it performs **unsigned integer underflow** and **wraps** to a massive positive value near the maximum — e.g. `total - available` with available slightly bigger yields something like `18,446,744,073,709,550,616` kB. If that value then feeds `100.0 * used_kb / total_kb`, the tool prints nonsense like *"1125899906842.6% used"*.

**Why the guard exists:** the corrupt state must be caught *before* the subtraction or division:

```c
if (memory.total_kb == 0 || memory.available_kb > memory.total_kb) {
    fputs("invalid memory totals\n", stderr);
    return 1;
}
```

This prints a clean error to `stderr` and aborts safely with return code `1` — instead of wrapping and reporting a garbage percentage.

## Trap 2 — The Integer-Division Truncation Trap

This is **type promotion** interacting with **integer division**, and it's the subtler bug.

### Why `100.0` (not `100`)?

When C mixes an `unsigned long` with a `double`, the *usual arithmetic conversions* kick in and promote the integer to `double` **before** the operation. So `100.0 * used_kb` converts `used_kb` to floating point, keeping the result a `double` for the division that follows — precision is preserved.

### The subtle bug in `(used_kb / memory.total_kb) * 100`

Rewrite it with parentheses and the trap reveals itself:

```c
double used_percent = (used_kb / memory.total_kb) * 100;
```

1. The parentheses force `(used_kb / memory.total_kb)` first — **two integers** divided.
2. C integer division **truncates the fractional part toward zero**. `8000000 / 16000000 = 0.5 → 0`.
3. `0 * 100 = 0`.

So for **any** usage under 100%, `used_percent` evaluates to `0.0%`. The bug isn't a lost decimal — integer division zeroed the whole fraction *before* the multiply ever ran.

By contrast `100.0 * used_kb / memory.total_kb` is evaluated left-to-right: `100.0 * used_kb` becomes a large float, then dividing that `double` by `total_kb` yields the correct `50.0%`.

## One Line Summary

Guard **before** subtracting unsigned values (they wrap, never go negative), and lead a percentage calculation with a float literal (`100.0`) so the division stays floating-point instead of truncating.

## Related

- [[Static Fixtures & Boundary Cases]] — `total_kb > 0` guards the divide-by-zero variant; `available_kb <= total_kb` is the true RAM invariant
- [[Sentinel Values vs Presence Flags]] — catching missing/corrupt fields before math
- [[C Memory Regions (Stack vs Heap vs Swap)]] — where these values live

## Sources

- Gemini C tutoring on the meminfo module (notebook: https://gemini.google.com/app/ed55c6cdf10c8c2a)
- C integer conversions (usual arithmetic conversions): https://en.cppreference.com/w/c/language/conversion
- Unsigned integer overflow/wraparound: https://en.cppreference.com/w/c/language/operator_arithmetic
