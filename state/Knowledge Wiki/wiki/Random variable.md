<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Random variable

A random variable is a function that maps outcomes from the sample space to values in a target space.

## Formal definition

- Let Ω be the sample space — the set of all possible outcomes of an experiment.
- Let T be the target space — the set of possible values the variable can take. Elements of T are called **states**.
- A random variable X is the function:

```
X : Ω → T
```

It takes an outcome ω ∈ Ω and returns a value x = X(ω) ∈ T.

## Key insight

A random variable is the **mapping**, not the value. The value x is a realization — the output you get when a particular outcome occurs. The function X is what converts raw outcomes into numbers you can work with.

## Pre-image

Given a subset S ⊆ T, the **pre-image** of S under X is:

```
X^{-1}(S) = {ω ∈ Ω : X(ω) ∈ S}
```

This is the set of all outcomes whose X-value falls in S. It lives in Ω, not T.

## Target space: discrete vs continuous

- If T is **finite or countable**, X is a **discrete random variable** (e.g., counts like 0, 1, 2, ...)
- If T = R or R^D, X is a **continuous random variable**

The same probability space (Ω, F, P) can produce many different random variables, each with its own T.

## Why formalize it this way

- Separates the source of randomness (Ω) from the quantity of interest (T)
- Makes it clear that probability distributions on T are **induced** by the probability measure on Ω through X
- Unifies discrete and continuous cases under one definition
- P_X(S) = P(X^{-1}(S)): probability about values of X = probability of underlying outcomes whose X-value is in S

## Why this matters for ML

Real-world sample spaces Ω are enormous (millions of pixels, sequences of words, sensor logs). Working directly with probabilities on Ω is infeasible. Random variables extract numeric quantities into a simple T where calculus, linear algebra, and optimization work. ML models estimate probabilities on T — e.g., P(X = 1 | pixel values) for classification — not on the vast space of all images.

**Example (cat vs dog classifier):**
- Ω = all possible images
- T = {0, 1}
- X(image) = 1 if dog, 0 if cat
- P_X({1}) = P(X^{-1}({1})) = probability of all underlying dog images

## Related pages

- [[Distribution of a random variable]]
- [[Probability foundations]]
- [[Probability mass and density functions]]
- [[Cox-Jaynes view]]

## Sources (verified)

- https://en.wikipedia.org/wiki/Random_variable
