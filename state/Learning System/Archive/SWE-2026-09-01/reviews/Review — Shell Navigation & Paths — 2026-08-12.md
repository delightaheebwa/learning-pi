# Review — Shell Navigation & Paths — 2026-08-12

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 7d (keep)

**Question:** You type `cd /var/log`, then `cd ../lib`. Where are you now? And what does `cd ~` do that `cd /home/you` doesn't — when would the two *not* be equivalent?

**Answer:** Now in `/var/lib` — `..` resolves from the cwd, so `/var/log/../lib` = `/var/lib`, not `/lib`. `~` expands to the *current user's* home, so it still works when you're not the user `you` or when home is elsewhere; `/home/you` hardcodes a username.

**Assessment:** ⚠️ Partial. Got "lib" but dropped `/var` — didn't show that `..` resolves relative to cwd (the point of the two-step). `~` part: named speed, missed portability to other usernames/HOME locations.

**Next Review:** 2026-08-19 (7d)
