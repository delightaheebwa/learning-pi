<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# C Memory Regions (Stack vs Heap vs Swap)

## Overview

A C program's memory isn't one undifferentiated blob — it's a set of regions with different lifetimes, speeds, and management rules. Confusing them causes most of the classic bugs (memory leaks, dangling pointers, buffer overflows). Think of them as different physical "drawers."

| Region | What it is | Managed by | Speed | Lifetime |
| --- | --- | --- | --- | --- |
| **Stack** | Fast automatic scratchpad for function locals | Compiler / CPU | Blazing fast | Destroyed when the function returns |
| **Heap** | Dynamic storage warehouse (`malloc` / `realloc`) | You (`malloc` & `free`) | Moderate | Persists until you call `free()` |
| **Swap** | Emergency overflow space on disk | Linux kernel | Slow | Used only when real RAM is full |

## The Stack (and the Caller's Stack)

The **stack** is a fast, temporary scratchpad managed automatically by the CPU. Every time a function is called, a small **frame** is pushed on top for that function's local variables; when the function returns, that frame is instantly wiped away.

**The caller's stack:** when `main()` declares `struct memory memory = { 0 };` and passes `&memory` into `read_meminfo()`, that variable lives on `main()`'s stack frame. `read_meminfo()` writes results *into that address* — the caller's stack outlives the callee.

Pros: extremely fast, zero manual cleanup. Cons: fixed, relatively small size (typically a few MB per thread), set by the OS/runtime rather than growable on demand.

## Heap Memory

The **heap** is a warehouse you rent from manually with `malloc()` / `realloc()`. Unlike the stack, heap memory stays allocated until you explicitly `free()` it — the CPU does not clean it up.

Why `read_file` uses it: we don't know `/proc/meminfo`'s size ahead of time. Stack sizes are fixed at compile time; the heap can grow dynamically on demand (`realloc` doubles the buffer), essential for variable-size virtual files.

**The catch:** forget `free()`, and the rented block stays locked until the program exits — a **memory leak**.

### Mental model: `char *buf = malloc(4096);`

The two parts live in *different* regions:

```
STACK (fast, local)          HEAP (warehouse)
+----------------------+     +------------------------+
| buf: 0x7fff00A1  --->|---->| [ 'M', 'e', 'm', ... ] |  (4,096 bytes)
+----------------------+     +------------------------+
```

- **`buf` (the pointer variable) lives on the stack** — an 8-byte slot holding the address `malloc` returned.
- **The 4,096-byte block lives on the heap** — the actual data `buf` points to.

If the function returns without saving the address or calling `free(buf)`, the heap block stays rented forever with no way to reach it — a memory leak. A plain local array (`char buffer[4096]` — no `malloc`) lives entirely on the stack and is reclaimed automatically on return (no leak possible).

## Swap

**Swap** is an overflow emergency room on your hard drive (SSD/HDD). When real RAM runs low, the kernel temporarily moves cold, inactive pages out of RAM and writes them to disk. It stops the system from crashing under memory pressure, but disk access is exponentially slower than RAM.

## Dangling Pointers vs Memory Leaks (the distinction)

Returning the address of a stack array is the classic dangling-pointer bug:

```c
char *read_file_broken(const char *path) {
    char text[4096];   // on the STACK
    // ... fill text ...
    return text;       // returns address of stack array
}
```

When `read_file_broken()` returns, its stack frame is destroyed. The returned pointer points at invalid stack memory — reading through it later is undefined behavior (corrupted data or crash). GCC/Clang warn on `return text;` because they can statically see it returns an address to local stack memory.

**Half-right trap:** the user guessed this was both a dangling pointer *and* a leak. The compiler warning is a *dangling pointer* warning — a stack array **cannot leak**, because stack memory disappears on exit. **Memory leaks only happen on the heap** when you fail to `free()`.

## Design Trade-off: Buffer-Passing vs Heap Allocation

Instead of allocating in `read_file`, pass a stack buffer in from the caller:

```c
int read_file_safe(const char *path, char *buf, size_t buf_size) { ... }
```

**Pros (faster, safer):**
- **Zero dynamic overhead** — no `malloc()`/`realloc()` system calls and lock synchronization; allocating stack memory is roughly a single CPU instruction.
- **Leak-proof** — the caller owns the buffer on its own stack frame, so it's cleaned up automatically when the caller returns; no `free()` needed anywhere.

**Limitation (fixed capacity):**
- A stack array has a fixed compile-time size and can't grow. If `/proc/meminfo` output exceeds `buf_size`, `read_file_safe` must truncate to prevent a stack overflow — and if fields like `MemAvailable` sit near the bottom of the truncated file, the parser silently fails to find them.

## One Line Summary

Stack = fixed-size, auto-cleaned scratchpad (can't leak, but returning its address dangles); heap = dynamic warehouse you must `free()` (leak-prone, but grows); swap = disk fallback when RAM is full; buffer-passing trades growth for speed + leak-safety.

## Related

- [[C Pointers (&, *, ->)]] — `&` / `*` / `->` operate across these regions
- [[C String Buffer Boundaries]] — why buffers reserve space for `'\0'`
- [[Memory management]] — the GC / manual / ownership *strategies* (a different axis from the physical regions here)
- [[C Integer Mechanics (Underflow & Type Promotion)]] — the validation wrapping this memory logic

## Sources

- Gemini C tutoring on the meminfo module (notebook: https://gemini.google.com/app/ed55c6cdf10c8c2a)
- C memory management: https://en.cppreference.com/w/c/memory
- Stack vs heap: https://en.wikipedia.org/wiki/Call_stack
