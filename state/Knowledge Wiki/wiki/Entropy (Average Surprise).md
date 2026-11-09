<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Entropy (Average Surprise)

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 + Olah (Visual Information Theory) · **Lang:** Python
> **Insight:** H(P) = E[−log p(X)] — the probability-weighted average of surprise. Max at uniform, 0 at deterministic.

## Definition

H(P) = −Σ p(x) log p(x) = Σ p(x)·(−log p(x)).

## Expectation reading

E[X] = Σ p(x)·x weights each value by its probability. Entropy is the expectation *of the surprise* −log p(x), with p(x) as the weight — not "the expected value of p(x)".

## Why the weights are the probabilities (2026-09-24)

On the final cumulative quiz an entropy of (0.5, 0.25, 0.25) came back as 5 bits — the *unweighted* surprise sum 1 + 2 + 2 — the p(x) weights had silently vanished. The repair: the weights **are** the probabilities. p(x) appears twice in H(P) = −Σ p(x)·log p(x): inside the log as the surprise *generator*, outside as the *weight*. The distribution feeds itself, so there is no second distribution to borrow weights from — that is [[Cross-Entropy from NLL]] (weights from the truth Q, surprises from the model P). Correct value here: 0.5·1 + 0.25·2 + 0.25·2 = **1.5 bits**. Re-tested isomorphically on a 4-sided die (0.5, 0.125, 0.125, 0.25) → **1.75 bits** (sure, grade-audit agreed). The same H is later exponentiated into [[Perplexity]] (2^H in bits, e^H in nats — [[Bits vs Nats]]).

## Rare events don't blow it up

A 1-in-1000 event has surprise ≈ 9.97 bits but contributes only 0.001 × 9.97 ≈ 0.01 bits, because it is weighted by its tiny probability. p·log p → 0 as p → 0.

## Examples

- Fair coin: H = 1.0 bit (maximum for a binary variable)
- 99%-heads coin: H ≈ 0.08 bits (near-certain → almost nothing learned per flip)
- Fair die: H = +log₂ 6 ≈ 2.585 bits (positive — entropy is non-negative)

## Nearest neighbor

Entropy is a property of one distribution; [[Cross-Entropy from NLL]] measures a distribution *against* another. Entropy is also the average length of the optimal code (Olah).

## Sources

- Olah, *Visual Information Theory*: https://colah.github.io/posts/2015-09-Visual-Information/
- Wikipedia — Entropy (information theory): https://en.wikipedia.org/wiki/Entropy_(information_theory)

## Related

- [[Information Content (Surprise)]]
- [[Cross-Entropy from NLL]]
- [[PMF vs PDF]]
