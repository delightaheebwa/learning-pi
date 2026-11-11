# Review — Bayesian A/B Testing — 2026-09-08

**Concept:** Bayesian A/B Testing
**Type:** procedure (review)
**Verdict:** ✅ PASS
**Mastery:** 0.50
**Next Review:** 2026-09-14

## Question (definitional)
You're A/B testing two button colors. In a Bayesian approach, after collecting click data, how do you decide which button to ship? What are the three advantages over frequentist?

## Answer
Ship if P(B>A) crosses 0.95, ship the other if below 0.05, keep collecting in between. Advantages: early peeking allowed, clearer communication to stakeholders (no null hypothesis jargon), can factor in past data.

## Gate
GATE:grade_audit — PASS (decision rule and all three advantages correct)
