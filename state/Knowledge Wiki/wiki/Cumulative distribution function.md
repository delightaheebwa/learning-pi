<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Cumulative distribution function

The **cumulative distribution function (cdf)** of a random variable $X$ gives the probability that $X$ is less than or equal to some value $x$:

```latex
F_X(x) = P(X \leq x)
```

It exists for both discrete and continuous random variables (unlike the pdf, which only exists for continuous ones).

## For continuous variables

The cdf is the integral of the pdf from $-\\infty$ up to $x$:

```latex
F_X(x) = \int_{-\infty}^{x} f(z) \, dz
```

Equivalently, the pdf is the derivative of the cdf:

```latex
f(x) = \frac{d}{dx} F_X(x)
```

## Key properties

- $F_X(x)$ is always between 0 and 1 — it's an actual probability, unlike the pdf
- $F_X(x)$ is non-decreasing: as $x$ increases, more probability mass is accumulated
- $\\lim\_{x \\to -\\infty} F_X(x) = 0$ and $\\lim\_{x \\to \\infty} F_X(x) = 1$

## PDF vs CDF

Think of it this way:

- **PDF $f(x)$**: the density (relative concentration) of probability near $x$. The height of the curve. Not a probability by itself — must be integrated.
- **CDF $F_X(x)$**: the accumulated probability from the left edge up to $x$. This *is* a probability.

Example: if height follows some distribution:

- $f(1.7) = 2.5$ means probability is concentrated near 1.7m (not a probability)
- $F_X(1.7) = 0.4$ means 40% of people are 1.7m or shorter (this *is* a probability)

## Multivariate case

For a $D$-dimensional random vector $\\mathbf{x}$:

```latex
F_X(\mathbf{x}) = \int_{-\infty}^{x_1} \cdots \int_{-\infty}^{x_D} f(z_1, \ldots, z_D) \, dz_1 \cdots dz_D
```

## Sources

- Wikipedia — Cumulative distribution function: https://en.wikipedia.org/wiki/Cumulative_distribution_function
- Deisenroth, Faisal & Ong — *Mathematics for Machine Learning*: https://mml-book.github.io/

## Related pages

- [[Probability mass and density functions]]
- [[Probability foundations]]
- [[Joint, marginal, and conditional probabilities]]
- [[Distribution of a random variable]]