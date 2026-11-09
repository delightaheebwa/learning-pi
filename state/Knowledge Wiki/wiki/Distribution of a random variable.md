<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Distribution of a random variable

The **distribution** (or **law**) of a random variable X is the function that assigns a probability to every set of possible values S ⊆ T:

```
P_X(S) = P(X ∈ S) = P(X^{-1}(S))
```

This is equation (6.8) from MML — the bridge between probabilities on the target space T and probabilities on the underlying sample space Ω.

## Intuition

To compute "what's the probability X lands in S?" you:
1. Find all outcomes ω ∈ Ω where X(ω) ∈ S — this is the pre-image X^{-1}(S)
2. Add up the probabilities of those outcomes

So: **probability about values of X = probability about underlying sample points whose X-value falls in that set.**

## Concrete example: two coins

- Ω = {HH, HT, TH, TT}, each with P = 1/4
- X = number of heads, T = {0, 1, 2}

| S | X^{-1}(S) | P_X(S) |
|---|---|---|
| {0} | {TT} | 1/4 |
| {1} | {HT, TH} | 1/2 |
| {2} | {HH} | 1/4 |

The distribution P_X is this table — for every set of values S, it tells you the probability.

## Mathematical perspective

P_X is the original probability measure P "pushed through" the mapping X:

```
P_X = P ∘ X^{-1}
```

This means: to get the probability of S in T-space, first pull back to Ω-space via X^{-1}, then apply P.

## ML significance

In ML we rarely work with P on raw Ω (too complex). Instead:
1. Define a random variable X that extracts the quantity we care about
2. Work with the distribution P_X on a simple, numeric T
3. Models estimate P(X = label | features) on T, not probabilities on the vast raw sample space

## Sources

- Deisenroth, Faisal & Ong — *Mathematics for Machine Learning* (Ch. 6): https://mml-book.github.io/
- Wikipedia — Pushforward measure: https://en.wikipedia.org/wiki/Pushforward_measure

## Related pages

- [[Random variable]]
- [[Probability foundations]]
- [[Probability mass and density functions]]
- [[Cox-Jaynes view]]
