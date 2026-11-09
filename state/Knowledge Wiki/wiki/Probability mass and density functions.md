<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Probability mass and density functions

A PMF and a PDF are two different ways to describe uncertainty, depending on whether the random variable is discrete or continuous.

## PMF

A **probability mass function** assigns probability to each discrete state of a random variable.

- The probabilities are nonnegative.
- They sum to 1.
- This is what we use for discrete or categorical variables.

## PDF

A **probability density function** is the continuous analogue.

- Probabilities come from areas under the density curve.
- To get the probability of an interval, you integrate the PDF over that interval.
- The probability of one exact point is effectively zero.

## The key difference

- PMF: probability is attached directly to individual states.
- PDF: probability is attached to ranges, not exact points.

## Why it matters

This distinction tells you whether to sum probabilities or integrate densities when you work with a model.

## CDF: the bridge between PDF and probability

The **cumulative distribution function (cdf)** $F_X(x) = P(X \leq x)$ accumulates probability from $-\infty$ up to $x$. It works for both discrete and continuous variables.

For continuous variables: $F_X(x) = \int_{-\infty}^x f(z) \, dz$ — so $f(x) = \frac{d}{dx} F_X(x)$. The pdf is the derivative of the cdf.

## Why f(x) can exceed 1

A pdf value like $f(5) = 2.0$ is perfectly valid — it doesn't mean "200% probability." The only requirements for a pdf are:
- $f(x) \geq 0$ for all $x$
- $\int_{-\infty}^{\infty} f(x)dx = 1$ (total area under the curve)

Think of population density: 2,000 people per km² doesn't mean 2,000 people stand on a single point. It means the concentration per unit area is high. Similarly, $f(5) = 2.0$ means probability is tightly concentrated near $x = 5$.

When you integrate over an interval, you get an actual probability between 0 and 1:
```latex
P(4.9 \leq X \leq 5.1) = \int_{4.9}^{5.1} f(x) \, dx
```

## Visual distinction

- **Discrete**: probability appears as isolated vertical lines with dots (lollipop/stem plots). Probability is zero between points. Each dot height = $P(X = x)$.
- **Continuous**: probability appears as a smooth density curve. The *area* under a segment of the curve gives probability, not the height at a point.

## Related pages

- [[Probability foundations]]
- [[Bayes rule]]
- [[Gaussian distribution]]
- [[Cumulative distribution function]]
- [[Joint, marginal, and conditional probabilities]]
- [[Independence of random variables]]

## Sources

- https://en.wikipedia.org/wiki/Probability_density_function
- https://en.wikipedia.org/wiki/Probability_mass_function
