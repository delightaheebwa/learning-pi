# 0009 — The five-step PCA recipe, and reading `eigh`'s output

**Date:** 2026-10-02 · **Lesson:** Phase 1 L10 — Dimensionality Reduction (CP2, minis 1–2) · **Type:** procedure (code recipe)
**Highest Bloom demonstrated:** Apply (wrote/selected correct NumPy lines; predicted shapes; ran the recipe mentally on the toy cloud)

## What was learned

- The canonical from-scratch PCA recipe: **center → covariance → eigenvectors → sort by λ → project** — and why each step exists (centering so spread axes point away from the data's center; covariance as the co-spread table; eigenvectors as the axes with λ's as their importance ranking; sorting to make "top-k" defined; projection rewriting the **data points** via dot products).
- `C = np.cov(Xc, rowvar=False)` — the one-line idiom (or `np.cov(Xc.T)`); $C$ is $d\times d$ and symmetric (a second transpose is a no-op); $n$ appears only inside the entries via $1/(n-1)$.
- `np.linalg.eigh(C)` returns eigenvalues **ascending** and eigenvectors as **columns**; the top-k axes are `order = vals.argsort()[::-1]` then `V = vecs[:, order[:k]]` — shape $d\times k$, **not** $d\times d/2$; axis selection slices columns, never rows; also keep `vals[order[:k]]`.
- Projection: `Xp = Xc @ V` is $n\times k$; each centered dot becomes its coordinate in the new basis (toy: $(2,1)\to\sqrt5$ along $(2,1)/\sqrt5$).
- Eigenvector sign is arbitrary ($C(-u)=10(-u)$): flipping an axis reflects the output; magnitudes, pairwise relations, and λ's are unchanged — sklearn's `svd_flip` is cosmetic.

## Misconception corrected (flagged)

- Claimed `vecs` is $n\times d$ and its rows are the projected data points. Corrected: `vecs` is $d\times d$ — columns are whole eigenvectors (axes), rows are **component slots** across axes; data points live only in `Xc` ($n\times d$) and `Xp` ($n\times k$). **Detector:** shape contains $n$ ⇒ points can be inside; all-$d$ shape ⇒ only feature-direction quantities. Related collision sharpened: `[::-1]` reverses order, `[:-1]` drops the last element.

## Annotated learner quotes (own words to reuse)

- "the length for a certain eigenvector direction is completely collapsed hence spread is found in only one of the two perpendicular directions" (λ=0 ⇒ pure line).
- "along the new perpendicular directions/eigenvectors" (where eigenbasis variance lives).
- "the matrix becomes an nxk matrix. a centered dot becomes the new projected point onto the new eigenbasis."

## Evidence

- Warm-up: W2 pass, W1 fail→repaired pass (grade-audit agreed) · exit ticket X1 B / X2 C pass, X3 fail→sealed (quiz-audit PASS cycle 2, grade-audit agreed) · fact-check PASS on every consolidation step.
