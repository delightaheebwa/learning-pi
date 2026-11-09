# Learning Record — PCA CP2 Practice Repairs — 2026-10-05

**Lesson:** Phase 1 L10 — Dimensionality Reduction (CP2 practice, paper walk)
**Highest Bloom demonstrated:** Apply (computed C by hand, characteristic polynomial, eigenvalues, kept fraction) with one Analyze reach (n==d contents-over-shapes reasoning, self-derived).

## What was learned

- Covariance entry recipe, in the learner's own words after repair: "a covariance entry is the centered **dot product** of the two feature columns, divided by n−1" — re-anchored from their own 09-30 exit-ticket phrasing, then re-derived by hand (dot products 8/4/8 for the practice set).
- The divisor detector: "with n points, the denominator is always one less than the number of rows you summed — centering ate one degree of freedom."
- Variance lives on the diagonal: "variance = a feature compared with itself ⇒ always diagonal; anything off-diagonal involves two different features." (Relapse repaired: they had called the off-diagonal 2 "the variance" under pressure — "any number of the minor diagonal is the variance".)
- The kept-spread pie is the trace: kept fraction = λ_top / Σλ (6/8 = 3/4), never 1 − λ2/λ1 — "any 'fraction of total spread' has the sum of ALL the λ's in the denominator."
- Shape detector, self-repaired: "n in a shape ⇒ rows can hold data points ⇒ Xp is n×k"; and the n==d edge resolved in their own words: when every array is d×d, "you check the contents it can hold" (Xp rows = points, V columns = directions).

## Evidence

- Paper walk P1–P4 (grade-audited): P1 fail → repaired through hint → hand-computed C = [[4,2],[2,4]] after the ÷n slip; P2 λ = 6, 2 ✓, top axis λ=6 ✓, fraction repaired to 3/4; P3 self-repaired to n×k + n==d contents rule; P4 pass (sign flip changes nothing).
- Isomorphic micro-checks all clean: biggest |coord| 10 ⇒ gap 20; 4 pts SS=12 ⇒ variance 4; [[5,1],[1,3]] diagonal roles; λ (9,3) ⇒ 3/4.
- Pause exit ticket 3/3 all `sure`: n−1 · 5/6 · "check the contents it can hold."

## Corrected misconceptions (this record)

1. **1/n vs 1/(n−1):** divided the centered dot products by n ("divided by 3"); detector = denominator one less than rows summed.
2. **Off-diagonal = variance (relapse):** "minor diagonal is the variance"; detector = self-dot ⇒ diagonal.
3. **Top λ as the pie:** kept fraction 1 − λ2/λ1 = 2/3; detector = denominator is Σλ (the trace).

## Durable learner preference (extended 2026-10-05)

The no-code rule now covers the learner's own environment too: no from-memory code writes as learning-system tasks — code in their own time only. Practices are paper walks (compute on paper, reply numbers/prose) or graded MCQ batches. The CP2 code-write integration is folded into the final cumulative quiz.
