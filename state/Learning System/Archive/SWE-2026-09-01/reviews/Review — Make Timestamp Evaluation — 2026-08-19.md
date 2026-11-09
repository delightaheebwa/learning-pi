# Review — Make: Timestamp Evaluation — 2026-08-19

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 14d (advanced)

**Question:** How does make decide whether to rebuild a target? Walk through the cases, what make never inspects, and why mtimes are both power and blind spot.

**Answer (user):** If target doesn't exist OR a prerequisite is newer than target → rebuild; if all prerequisites are older → no rebuild. Make never inspects WHAT changed — any modification (significant or insignificant) triggers a rebuild. Uses mtimes to decide.

**Assessment:** ✅ Clean pass. Correct on all three cases, the core 20% (make is a timestamp machine, never inspects content — comment-only save forces rebuild), and the power/blind-spot framing. No misconception.

**Next Review:** 2026-09-02 (14d)
