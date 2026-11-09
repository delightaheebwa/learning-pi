# 2026-05-19 — Random variable pre-image, distribution, and ML motivation

Source: Perplexity conversation walking through Mathematics for Machine Learning (MML) section on random variables.

## Key content

### Pre-image X^{-1}(S)

Given X : Ω → T and S ⊆ T:

```
X^{-1}(S) = {ω ∈ Ω : X(ω) ∈ S}
```

The set of all sample points whose X-value lands in S.

### Fundamental identity (equation 6.8)

```
P_X(S) = P(X ∈ S) = P(X^{-1}(S)) = P({ω ∈ Ω : X(ω) ∈ S})
```

"Probability that X is in S" is by definition the probability of the pre-image set.

### Distribution / law of X

```
P_X : T ⊇ S ↦ P_X(S)
```

The function that gives, for every set of possible values S, the probability that X lands in S. Mathematically: P_X = P ∘ X^{-1} (the original measure "pushed through" X).

### Concrete two-coin example

- Ω = {HH, HT, TH, TT}, each with P = 1/4
- X = number of heads, T = {0,1,2}
- X^{-1}({1}) = {HT, TH}, P_X({1}) = 1/2
- X^{-1}({2}) = {HH}, P_X({2}) = 1/4
- X^{-1}({0}) = {TT}, P_X({0}) = 1/4

### Target space: discrete vs continuous

- T finite or countable → discrete random variable
- T = R or R^D → continuous random variable

### ML motivation

Real-world Ω is too complex (images, text, sensor logs). Random variables extract numeric quantities into a simple T where calculus and optimization are tractable. ML models estimate P(X = label | features) — probabilities on T, not on Ω.

### Cat-vs-dog classification example

- Ω = all possible images
- T = {0, 1}
- X(image) = 1 if dog, 0 if cat
- P_X({1}) = P(X^{-1}({1})) = probability of all dog images
