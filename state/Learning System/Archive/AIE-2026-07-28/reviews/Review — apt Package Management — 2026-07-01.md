# Review — apt Package Management

**Date:** 2026-07-01
**Track:** AI Engineering (aie)
**Interval:** Kept current

## Retrieval Result

Commands mostly right. Missed:
- `upgrade` (applies updates after `update`)
- `apt clean` clears cached `.deb` files from `/var/cache/apt/archives/` (disk space), not specifically failed installs
