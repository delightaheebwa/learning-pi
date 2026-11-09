# Review — Memory Management Models — 2026-06-09

**Concept:** Memory management models
**Status:** developing
**Result:** Incomplete — confused reference counting with tracing GC. The three models are: reference counting (track pointers per object, free when count=0), tracing GC (mark from roots, sweep unreachable), and manual (malloc/free). Reachability means: can you reach an object by following references from a root?
**Action:** Reset to 3 days. Next review: 2026-06-12.
