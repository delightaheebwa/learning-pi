# Session — SWE Review — 2026-08-23

**Date:** 2026-08-23 · **Track:** SWE (Shell & Terminal) · **Type:** Scheduled review (cap 5)
**Due (Next Review ≤ 2026-08-23):** 5 concepts · **Result:** 2 PASS · 3 HOLD

| Concept | Q Type | Verdict | Interval |
| --- | --- | --- | --- |
| sed (Stream Editor) | definitional | HOLD — `/g` misremembered as "do nothing else"; it = global per-line | held 7d → 2026-08-30 |
| Shell Config & Dotfiles | discriminative | PASS — export lives in shell-process memory, dies at logout; startup files persist | 3d → 7d → 2026-08-30 |
| C String Buffer Boundaries | discriminative | HOLD — NUL instinct right; +1 terminator off-by-one & pre-copy bounds check unpinned | held 7d → 2026-08-30 |
| Sentinel Values vs Presence Flags | definitional | PASS — 0 ambiguous when 0 is a valid value; presence flags decouple presence from payload | 7d → 14d → 2026-09-06 |
| C Memory Regions (Stack vs Heap vs Swap) | discriminative | HOLD — leak ✓, dangling inverted (stack array dangles on return; heap block leaks instead) | held 3d → 2026-08-26 |

**Interleaving:** 5 concepts shuffled, adjacency constraint respected (two Gemini-sourced concepts separated); 2 discriminative / 3 definitional.

**Pattern noticed:** both C holds are lifetime/boundary confusions (who owns the memory, when does it die) — candidate thread for the next Monitor lesson (A5).

**Open questions:** none parked in the SWE section this session.

**Notes:** Terminal backend dropped mid-session (~21:40–22:09 UTC); session state reconstructed from the live transcript, zero data loss. C Integer Mechanics (due 2026-08-24) intentionally left for its own slot tomorrow.
