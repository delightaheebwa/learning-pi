# SESSION: Taylor Series and Maclaurin Series — 2026-04-16

> **Purpose:** Capture what happened in this learning session. Zo will use this to update the Knowledge Base at the end of the session.

## Session Info

- **Date:** 2026-04-16
- **Topic:** Taylor Series and Maclaurin Series
- **Prerequisites Reviewed:** Difference quotient, derivative, local approximation intuition
- **New Concepts Introduced:** Taylor series, Maclaurin series, coefficient structure, example Maclaurin series for e^x

---

## What We Covered

> Summary of the session content.

- Defined Taylor series as an infinite polynomial centered at any point a.
- Built the idea from derivatives at the center point: value, slope, curvature, and higher-order shape information.
- Clarified that higher derivatives do not add information from other parts of the curve; they add more local information at the chosen center.
- Defined Maclaurin series as the special case of Taylor series centered at 0.
- Used e^x as the example Maclaurin series: 1 + x + x^2/2! + x^3/3! + ...
- Practiced truncating the series to approximate e^0.1 and got 1.105.
- Corrected the confusion between a derivative and the corresponding term in the series.

---

## Concepts Status After Session

> Updated statuses for concepts discussed in this session.

| Concept | Previous Status | New Status | Notes |
|---------|----------------|------------|-------|
| Taylor series | not_started | mastered | User explained the centered-series idea and coefficient structure correctly after correction |
| Maclaurin series | not_started | mastered | User correctly identified it as Taylor series centered at 0 |

---

## Demonstrations of Understanding

> Proof that you could explain / apply the concepts. Zo will ask you to demonstrate — record the results here.

- **Concept:** Taylor series / Maclaurin series
  - **Your explanation:** Taylor series is centered at any point a, and Maclaurin is the same idea centered at 0.
  - **Zo evaluated:** Pass

- **Concept:** Maclaurin approximation
  - **Your explanation:** Using the series for e^x up to x^2 gave 1 + 0.1 + 0.1^2/2 = 1.105.
  - **Zo evaluated:** Pass

---

## Open Questions

> Questions that came up but weren't fully resolved.

- [ ] None

---

## Gaps & Misconceptions

> Things that tripped you up or weren't fully clear.

- [x] Derivative vs term in the series — you initially treated the 4th term like the 4th derivative, then corrected it once we separated f^{(4)}(0) from the x^4/4! term.

---

## Next Steps

> What to tackle in the next session.

- [ ] Review Taylor series and Maclaurin series on the next spaced-repetition date.
- [ ] Move next to Taylor polynomials and remainder/error if you want to know how accurate a truncated series is.

---

## Zo's Summary

> Zo will write a brief summary here at the end of the session.

You now know the core structure of Taylor and Maclaurin series, how derivatives determine the coefficients, and why the approximation improves near the center point.
