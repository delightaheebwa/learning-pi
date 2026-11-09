<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Covariance and correlation

Covariance and correlation describe how two random variables move together.

## Covariance

Covariance measures whether two variables tend to increase and decrease together.

- Positive covariance: they tend to move in the same direction
- Negative covariance: they tend to move in opposite directions
- Near zero covariance: little linear relationship

## Correlation

Correlation is a scaled version of covariance.

- It is normalized so the result always lies between −1 and 1.
- That makes it easier to compare relationships across different units.

## Why it matters

Covariance tells you about joint variation, while correlation tells you the same story on a standardized scale.

## In NumPy

`np.cov` computes the sample covariance with the `1/(n-1)` normalization, so the sample count appears **only inside the entries** — never as a matrix dimension. The divisor is one less than the number of rows you summed: centering has already consumed one degree of freedom, so dividing by `n` gives a plausible-looking but wrong covariance (paper walk 2026-10-05).

- `np.cov(Xc, rowvar=False)` — each **column** is a variable (features-as-variables), giving a `d×d` matrix for `d` features. This is the layout the PCA recipe assumes.
- The **default is `rowvar=True`**: each *row* is a variable. On a points-as-rows matrix the default silently builds the covariance along the wrong axis (an `n×n` object of point-pairings).
- The result is square and symmetric; a single variable comes back as a 0-d scalar, not a `1×1` matrix.

See [[PCA (Dimensionality Reduction)]] for how this matrix is decomposed.

## Related pages

- [[Probability foundations]]
- [[Gaussian distribution]]
- [[Jacobian matrix]]
- [[PCA (Dimensionality Reduction)]]
- [[PCA Sign Ambiguity (svd_flip)]]
- [[Variance is Non-Negative (PSD Covariance)]]

## Sources

- https://numpy.org/doc/stable/reference/generated/numpy.cov.html
