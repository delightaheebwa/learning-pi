<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# PCA Sign Ambiguity (svd_flip)

> Related: [[PCA (Dimensionality Reduction)]], [[Variance is Non-Negative (PSD Covariance)]], [[Covariance and correlation]]

An eigenvector is defined **up to sign**: if `u` is an eigenvector of `C` with eigenvalue λ, so is `-u`, because `C(-u) = λ(-u)`. PCA therefore has no canonical sign for its components, and two implementations can disagree component-by-component while computing the identical decomposition.

## What flips and what does not

- **Immune to sign:** eigenvalues, explained variances, reconstruction error, and anything squared (trace, determinant).
- **Flip together:** each direction (`components_`) and the signed projected coordinates of that direction (`transform` / the scores). The axis stays the same line; only which end is called positive changes.

The correct comparison between two implementations is therefore on **magnitudes and variances** — never on signed coordinate values.

## The seeded race

`MyPCA` (eigh-based, from scratch) vs `sklearn.decomposition.PCA(n_components=1)`, seed = 3, n = 200, 2-D cloud with covariance `[[4,2],[2,1.5]]`, k = 1:

| Quantity | MyPCA | sklearn | Reading |
| --- | --- | --- | --- |
| explained variance | 4.98024987 | 4.98024987 | identical |
| component | (−0.88907314, −0.45776516) | (0.88907314, 0.45776516) | exact sign flip |
| max signed coordinate gap | — | — | 13.201563505 |
| max magnitude gap | — | — | 8.881784197e-16 |

**Verdict: a tie up to sign.** The magnitude gap at 1e-15 is float noise — there is no real discrepancy.

## Why the signed gap is large and still harmless

With `my_i = −sk_i`, the signed difference is `my_i − sk_i = −2·sk_i`. Its maximum is therefore **twice the cloud's biggest coordinate** — the scale of the data itself, not the size of an error. It is a **label mirror**: the same points, the same axis, the opposite names for the two ends.

## The practical caveat: sign-sensitive thresholds

Any rule that compares a signed score to a threshold — "flag if score > +2", "keep the top 1% by signed loading" — is **convention-dependent**, and it breaks when the sign convention changes (a different NumPy/LAPACK build, a different solver, a different implementation).

- Restate such rules as **`|score|` thresholds** before shipping them.
- Variance-based and reconstruction-based rules are immune: the sign dies in the square.

## svd_flip

scikit-learn's SVD-based solvers post-process components through `svd_flip`, which flips each component so that its largest-magnitude entry is positive. That flip is a **cosmetic sign convention**, not part of the mathematics: it changes neither the eigenvalues nor the projected variances, and an `eigh`-based implementation is not expected to reproduce it.

## Open questions

- With **tied eigenvalues** the ambiguity is bigger than a per-component sign: the whole eigenspace is free to rotate within itself, so not even the *directions* are determined. Carried to CP3 with the round-cloud degenerate case.

## Sources

- scikit-learn svd_flip — https://scikit-learn.org/stable/modules/generated/sklearn.utils.extmath.svd_flip.html
