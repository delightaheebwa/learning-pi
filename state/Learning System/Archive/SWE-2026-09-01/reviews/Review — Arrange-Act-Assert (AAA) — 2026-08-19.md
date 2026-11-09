# Review — Arrange-Act-Assert (AAA) — 2026-08-19

**Track:** SWE (Shell & Terminal)
**Question Type:** definitional
**Interval:** 7d → 14d (advanced)

**Question:** Explain AAA — the three phases, the frame-first writing order, the "no fourth A" point, and when a series of asserts is fine.

**Answer (user):** Three phases Arrange/Act/Assert: Arrange sets up the test and checks it fails (write test first to see it fail); Act defines the functionality to test; Assert checks if still failing and fixes functionality to pass. No fourth A because testing individual functionality; multi-act tests test too much at once. A series of asserts is fine when a single functionality can behave in different ways.

**Assessment:** ⚠️ Partial. Strong on: "no fourth A" (multi-act tests test too much) and "multiple asserts on one act are fine (dimensions of a single behavior) — multiple acts are the smell." **Key correction — conflated AAA with Red-Green-Refactor:** AAA (Given/When/Then) is the STRUCTURE of one test — Arrange (set up) → Act (ONE targeted call) → Assert (claim observable outcome); it assumes code exists. RGR (write failing test first → minimal code to pass → refactor) is the WRITING WORKFLOW — that's the "see it fail first, then fix to pass" the user described, not AAA. Also nudge: Act isn't "define the functionality" — it's the single call exercising existing code. The AAA-vs-RGR distinction is the 20% insight.

**Next Review:** 2026-09-02 (14d)
