<!-- provenance: status=verified | source=https://man7.org/linux/man-pages/man5/proc_meminfo.5.html ; https://kernel-internals.org/mm/understanding-proc-meminfo | verified-by=fact-check-agent | date=2026-10-26 -->

# Feature Probing vs Kernel Version Checking

## Overview

When a kernel feature may be absent (e.g. `MemAvailable` in `/proc/meminfo`, only added in **Linux 3.14**), production tools like `free` and `top` do **not** check the kernel version. They **probe for the feature at runtime** and degrade gracefully with a fallback formula.

## Why Not Version Checking

1. **Backports make versions lie** — enterprise distros (RHEL, Debian) backport features to older kernels; a 3.10 kernel from RHEL can have `MemAvailable`. `uname` also can be spoofed.
2. **Multi-binary shims are a maintenance nightmare** — shipping a separate `free` for 2.6 / 3.10 / 4.20 / 5.x is unmanageable; users expect one binary that "just works" across kernel generations.

## The Pattern: Runtime Feature Probing

Ask "is the feature present?", never "what version are you?":

```c
memory.available_kb = ULONG_MAX;   // sentinel: "not seen yet"
// parse /proc/meminfo...
if (memory.available_kb == ULONG_MAX) {
    // MemAvailable line never appeared → feature unsupported on this kernel
}
```

The sentinel value doubling as a feature probe is the same idea as [[Sentinel Values vs Presence Flags]] — `ULONG_MAX` is outside the legitimate domain, so "still sentinel" reliably means "absent".

## Graceful Fallback Math

When `MemAvailable` is absent (pre-3.14), estimate from fields present since Linux 2.6:

```
Estimated Available ≈ MemFree + Buffers + Cached
```

Not as precise as the kernel's internal estimation, but remarkably close for older systems.

## Key Insight

- **Probe capability, not version.** Version strings are fragile (backports, spoofing); feature presence is truth.
- Degrade gracefully: use the real value when present, a documented fallback formula when not — never crash, never lie.
- This is why the smoke test keeps the sentinel check (`available_kb != ULONG_MAX`): the sentinel is both a correctness check and the feature probe.

## Which "Available" Field to Use (MemFree vs MemAvailable vs SwapFree)

The retrieval-check question — "which is best for *memory available to start an app*?" — is `MemAvailable`, and the reason is the kernel semantics behind each field (added 2026-08-18 from Gemini notebook ed55c6cdf10c8c2a):

- **`MemFree`** is strictly the RAM that is *completely unused and untouched right now*. Linux intentionally keeps this low, because unused RAM is wasted RAM.
- **`MemAvailable`** is a kernel **estimate** that combines `MemFree` with *reclaimable* memory — file caches and buffers the kernel can throw away or flush to disk *without swapping*, if a new app needs memory. This is what actually predicts "can I start an app without paging?"
- **`SwapFree`** is only unused space on the secondary disk/swap partition, **not** main memory (RAM) at all.

So `MemFree` undercounts headroom (ignores reclaimable cache) and `SwapFree` is the wrong axis (disk, not RAM). `MemAvailable` gives the truest picture of headroom before the system starts paging.

## Sources

- Gemini Socratic session — robust `/proc/meminfo` smoke test (notebook: https://gemini.google.com/app/e338aa05afbec7a2)
- https://man7.org/linux/man-pages/man5/proc_meminfo.5.html
- https://kernel-internals.org/mm/understanding-proc-meminfo
