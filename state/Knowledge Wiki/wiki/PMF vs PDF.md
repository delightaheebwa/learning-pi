<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# PMF vs PDF

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L06 + CS229 probability review · **Lang:** Python
> **Insight:** PMF = discrete point probability. PDF = density (integrate for probability). CDF = cumulative. PDF value at a point is NOT a probability.

## PMF
- For discrete random variables
- P(X = k) gives a real probability at each point
- Values sum to 1

## PDF
- For continuous random variables
- f(x) gives density, NOT probability at a point
- P(X = exact value) = 0
- Integrate over interval for probability
- Can exceed 1; total area = 1

## CDF
- F(x) = P(X ≤ x)
- Integral of PDF

## Key Distinction

PDF at a point ≠ probability. PDF = density. Integrate to get probability.

## Related

- [[Probability Mass Function (PMF)]]
- [[Gaussian distribution]]
- [[Probability & Distributions for ML]]

## Sources

- https://en.wikipedia.org/wiki/Probability_density_function
- https://en.wikipedia.org/wiki/Probability_mass_function
