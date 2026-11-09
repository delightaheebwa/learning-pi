# Review — C String Buffer Boundaries — 2026-08-23

**Track:** SWE (Shell & Terminal / C monitor project)
**Question Type:** discriminative (alternated from definitional)
**Interval:** held 7d

**Question:** Two inputs both hit the size limit — one silently corrupts memory, the other returns a clean error. What single off-by-one in the buffer declaration causes the corruption, and what turns it into a clean error?

**Answer:** "This is because of the non-use or use of the NUL byte."

**Assessment:** ⚠️ Hold. Right instinct — the NUL terminator is involved — but the mechanism went unpinned: (1) the declaration must reserve room for '\0': `char username[COLUMN_USERNAME_SIZE + 1]` — at max-length input WITHOUT the +1 the terminator writes out of bounds (silent corruption); (2) the clean-error path is a bounds check (strlen) BEFORE copying, rejecting over-long input rather than letting it overflow. Held 7d.

**Next Review:** 2026-08-30 (held 7d)
