# Review — Make: Timestamp Evaluation — 2026-08-04

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d (2nd review)

**Question:** When does `make` decide to **skip** rebuilding a target vs rebuild it? What specific comparison determines the outcome?

**Answer:** Make compares the timestamp of the target file against its prerequisites. If the target is more recent than all prerequisites, it skips. If any prerequisite is newer, it rebuilds.

**Assessment:** Correct. The user nailed the core mechanism: timestamp comparison between target and prerequisites determines rebuild vs skip.

**Notes:** Target doesn't exist → always rebuild. Any prerequisite newer → rebuild. All prerequisites older → skip.

**Next Review:** 2026-08-11 (7d interval)
