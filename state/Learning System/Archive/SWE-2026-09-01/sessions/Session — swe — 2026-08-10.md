# Session — swe — 2026-08-10

**Date:** 2026-08-10
**Topic:** swe Review — find, jq, Sentinel Values vs Presence Flags, Arrange-Act-Assert, Shell Redirections & Streams
**Track:** swe

## Concepts Reviewed

| Concept | Status | Interval | Next Review |
|---|---|---|---|
| find | developing | 3d (reset — command recall missed) | 2026-08-13 |
| jq | developing | 7d (advanced) | 2026-08-17 |
| Sentinel Values vs Presence Flags | developing | 3d (kept — fuzzy on sentinel-safety condition) | 2026-08-13 |
| Arrange-Act-Assert (AAA) | developing | 7d (advanced) | 2026-08-17 |
| Shell Redirections & Streams | developing | 3d (reset — missed `2>&1` order gotcha) | 2026-08-13 |

## Notes
- 17 concepts were due; shuffled, capped at 5.
- Strong on jq vs grep (structural parse vs text match) and AAA's single-Act focus.
- Two resets: `find` (wrong syntax: `find -f` instead of `find <dir> -type f -name`) and `Shell Redirections & Streams` (`2>&1 > file` sends stderr to terminal, not file — order matters).
- Sentinel: close but fuzzy — couldn't state the "value can never be a legitimate payload" condition crisply.
- Interleaving: 5 concepts shuffled, 3 discriminative / 2 definitional.
- No open questions surfaced during review.
