# Review — Static Fixtures & Boundary Cases — 2026-08-11

**Track:** SWE (Shell & Terminal)
**Question Type:** discriminative
**Interval:** 3d → 7d (advanced)

**Question:** What's the difference between a *regular* fixture and a *boundary/adversarial* fixture — and what's the practical point of the boundary ones?

**Answer:** Regular fixture = controlled, predictable sample data. Boundary/adversarial = malformed input (extra spaces, missing headers), extreme values, empty files, max-size strings — they exist because fixture assumptions break in production (format drift, missing fields, overflow); they force the parser to handle input it assumed would never come.

**Assessment:** Correct — captured normal-vs-messy; added the "assumptions break in production" point.

**Next Review:** 2026-08-18 (7d)
