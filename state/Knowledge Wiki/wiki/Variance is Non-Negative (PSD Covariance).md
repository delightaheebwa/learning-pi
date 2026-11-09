<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Variance is Non-Negative (PSD Covariance)

> Related: [[Covariance and correlation]], [[PCA (Dimensionality Reduction)]], [[PCA Sign Ambiguity (svd_flip)]]

Variance is an **average of squared deviations** from the mean. The square destroys the sign of a deviation, so variance can never be negative — and that single fact is why a covariance matrix's eigenvalues can never be negative.

## The chain

1. `Var(X) = E[(X − μ)²] ≥ 0`, because every term is a square. It equals 0 only for a constant variable.
2. For a unit direction `u`, the variance of the projected coordinates `xᵀu` is `uᵀCu`; for non-unit `u` it scales by `‖u‖²`. This *projected variance* is exactly what PCA maximizes.
3. Writing `C = 1/(n−1)·XcᵀXc` with `Xc` the centered data, `uᵀCu = ‖Xc u‖²/(n−1) ≥ 0`.
4. So `uᵀCu ≥ 0` for **every** vector `u` — the definition of a **positive semidefinite (PSD)** matrix.
5. A PSD matrix has non-negative eigenvalues: take `u` an eigenvector, then `λ = uᵀCu ≥ 0`.

## Why it matters here

- The eigenvalues of a covariance matrix **are variances along directions**, so `λ ≥ 0` is not a coincidence — it is the PSD property restated.
- `λ = 0` therefore means **zero spread** in that direction (a rank-deficient cloud, e.g. points on a straight line through the origin), not a negative variance. PCA can drop such an axis at no loss.
- A negative eigenvalue out of a numerically computed covariance is **float noise**, not information.

## Precise scope

- PSD is a property of covariance matrices, **not of symmetric matrices in general**: `[[0,1],[1,0]]` is symmetric with eigenvalues +1 and −1.
- The `1/(n−1)` sample covariance is always PSD; with `n < d` it is additionally singular (rank ≤ n−1), so it carries zero eigenvalues.
- Standard deviation — the square root of a variance — is also non-negative by construction.

## Field note (2026-10-03)

The learner's own consolidation: "all its doing is summing squared deviations and a mere sign flip doesnt matter because of the square."

## Sources
- https://en.wikipedia.org/wiki/Covariance_matrix
- https://en.wikipedia.org/wiki/Positive-semidefinite_matrix
