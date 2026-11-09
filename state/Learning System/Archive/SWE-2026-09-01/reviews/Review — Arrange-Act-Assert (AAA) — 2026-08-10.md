# Review — Arrange-Act-Assert (AAA) — 2026-08-10

**Concept:** Arrange-Act-Assert (AAA)
**Source:** Bill Wake 3A (xp123) + Teach C Lesson 2
**Q Type:** Discriminative
**Confidence:** 4/5

**Q:** What does a properly AAA-structured test give you that a sloppy "call the function, check the output" test doesn't? What does the Act step force you to do?

**A (user):** Act forces you to define what specific thing in a function you are testing, giving more precision when debugging.

**Evaluation:** Pass. Act = one targeted invocation per test → when it fails you know exactly which behavior broke; failures localize.

**Next Review:** 2026-08-17 (7d — advanced)
