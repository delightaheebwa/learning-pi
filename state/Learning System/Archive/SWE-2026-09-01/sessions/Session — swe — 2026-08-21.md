# Session — swe — 2026-08-21

**Date:** 2026-08-21
**Topic:** swe Review — Job Control, bat, C Integer Mechanics, What is the Shell, Signals
**Track:** swe

## Concepts Reviewed

| Concept | Status | Interval | Next Review |
|---|---|---|---|
| Job Control (Ctrl-Z, fg/bg, nohup/disown) | developing | 3d → 7d (advanced) | 2026-08-28 |
| bat | developing | 7d → 14d (advanced) | 2026-09-04 |
| C Integer Mechanics (Underflow & Type Promotion) | developing | held @3d | 2026-08-24 |
| What is the Shell | developing | held @7d | 2026-08-28 |
| Signals (Software Interrupts) | developing | 3d → 7d (advanced) | 2026-08-28 |

## Notes
- Large due backlog still queued (next-Round candidates incl. PATH, fd, curl, jq, File Permissions, Makefile Targets, Intermediate Object Files, Make Variables, Clean Targets, Git commit, Shell Built-ins, Command Substitution, Shebang — most overdue). Capped at 5 per the flow; the rest stay queued.
- **Job Control:** ✅ pass (definitional) — nailed the *mechanism*: nohup is a wrapper used **before** the job exists (`nohup cmd &`), disown references an **already-running** job's job-table slot by `%n` (`disown %1`); `disown <cmd>` is a misleading pattern.
- **bat:** ✅ pass (definitional) — paging/scrolling + syntax highlighting recalled; line numbers under-emphasized ("on-demand viewing" was a feeling, not a feature).
- **C Integer Mechanics:** ❌ held (discriminative) — knew `100.0` matters + "integers lose accuracy," but INVERTED cause/cure: integer division **truncates** (`(used/total)*100` → 0.0%); the float literal **promotes** the chain to double. Result type follows its operands. Reforge next round (due 08-24).
- **What is the Shell:** ⚠️ mostly pass (discriminative) — decoded machine/`~`/normal-`$` correctly; MISFIRE: called `#` a "guest" — it is **root/superuser** (opposite; max privileges). Prompt tells you how dangerous your next command could be. Held 7d.
- **Signals:** ✅ pass (discriminative) — full SIGINT/SIGTERM/SIGKILL ladder + why kill -9 skips cleanup; refined: SIGINT/SIGTERM catchable, SIGKILL UNcatchable.
- Interleaving: 5 concepts shuffled, 3 discriminative / 2 definitional.
- No open questions surfaced during review. C Integer Mechanics flagged for a follow-up deep-dive (next due 08-24).

## Queue / Deferred
- Backlog remains queued; next review (08-24) will surface C Integer Mechanics + any newly-due concepts.
