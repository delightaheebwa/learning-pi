# Review — curl (Web Fetching) — 2026-08-08

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d

**Question:** You want to count how many times a URL contains a phrase, without saving the page. Why pipe `curl -s` into `grep` instead of saving to a file first?

**Answer:** Websites are streams — `curl -s URL | grep -c 'pattern'` composes directly; no intermediate file needed. grep operates on stdin fine.

**Assessment:** Correct — understood that grep doesn't need a saved file and the output flows straight through the pipe.

**Next Review:** 2026-08-15 (7d)
