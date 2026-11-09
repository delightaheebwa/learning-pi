<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Curse of Dimensionality

> Related: [[PCA (Dimensionality Reduction)]], [[Covariance and correlation]], [[Variance is Non-Negative (PSD Covariance)]]

**The curse of dimensionality** is the family of failures that show up as the number of features `d` grows: the geometry that makes low-dimensional intuition work stops holding, even though every individual coordinate still behaves perfectly.

## Distance concentration

The headline effect: pairwise distances become **more alike**. The *relative contrast* — the ratio of the largest to the smallest pairwise distance — collapses toward 1. Working numbers from this track's lesson source: max/min ≈ **1.8 at d = 10** → ≈ **1.02 at d = 1000**.

- The distances are **not getting smaller**; they are getting **more similar**. Nearest and farthest neighbours become nearly equidistant, so "closest" stops being informative. A claim that high dimensions "shrink distances" has the direction wrong.
- **Detector:** read a max/min ratio as a **contrast** measure — a ratio near 1 means the metric has little left to say. This is the failure mode behind distance-based methods (k-NN, k-means, plain Euclidean clustering) degrading in high dimensions, and behind the need for dimensionality reduction *before* distance work.

## Why this bites PCA: compressibility needs anisotropy

PCA can keep `k < d` axes only when the spread is **unequal** across directions. The total spread is fixed — `Σλ = trace(C)` is invariant under rotation — so PCA **redistributes** variance; it never removes it.

- **Isotropic case** (`C = λI`): every direction is an eigenvector, the scree is flat, and not one axis can be dropped — see [[PCA (Dimensionality Reduction)]] § *the round cloud*.
- **Anisotropic case** (`λ = (99, 1)`): one axis holds 99% of the pie and the rest can go at ~1% loss.
- So more dimensions makes dimensionality reduction **more desirable** (more coordinates to carry, more near-noise directions to shed) and, for isotropic data, **harder** at the same time. The learner's own phrasing: "PCA lives and dies on whether the spread is irregular or not."

## Field notes

The learner's synthesis (2026-10-07), with the two corrections applied:

- "PCA just cuts a slice of the cake but doesnt make the cake as a whole smaller." — right, and sharpened twice: PCA **bakes** (rotates) before it cuts, and the cake's total (`Σλ = trace(C)`) is unchanged by the rotation.
- "since distances are getting less and less" — repaired to **concentration**: distances become more alike, not smaller; the contrast is what collapses.
- "10 equal bars; cutting even one loses too much" and "the scree is a bunch of bars of equal height of 100" — the isotropic read was correct on both halves.
- Micro-check passed (grade-audit agreed): `λ = (99, 1)` compresses to `k = 1` at 1% loss, while `λ = (50, 50)` — the same total — loses 50%.

## Sources

- Wikipedia — Curse of dimensionality: https://en.wikipedia.org/wiki/Curse_of_dimensionality
- Aggarwal, Hinneburg & Keim (2001), "On the Surprising Behavior of Distance Metrics in High Dimensional Space": https://bib.dbvis.de/uploadedFiles/104.pdf

## Open questions

- Is the max/min collapse derivable by hand (the volume/annulus argument), or are the d = 10 → d = 1000 numbers the working empirical anchor?
- Distance-preserving methods are the standard answer to concentration (t-SNE, UMAP — CP4–CP5 of this lesson). How much of the fix is the objective, and how much is redefining "neighbourhood" locally? Pending CP4.
