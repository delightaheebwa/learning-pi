<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Categorical Distribution

Generalizes Bernoulli to k possible outcomes: one trial, k mutually exclusive categories.

## Definition

$$P(X = i) = p_i, \quad i \in \{1, 2, \ldots, k\}$$

with constraint $\sum_{i=1}^k p_i = 1$ and $p_i \geq 0$ for all i.

## Why it matters in ML

**This is what sits at the end of every multi-class classifier.** After the softmax, you have a vector of k probabilities that sum to 1 — that's a Categorical PMF.

Examples:
- ImageNet classifier: 1,000 classes → Categorical(1000)
- MNIST digit classifier: 10 classes → Categorical(10)
- Next-token prediction in LLMs: vocabulary size → Categorical(vocab_size)

## Relationship to other distributions

- **Bernoulli** = Categorical(2)
- **Multinomial** = n independent Categorical trials (not a Categorical!)
- **One-hot encoding** is the sample format: a vector of all zeros with one 1 at the chosen category

## Implementation insight

Sampling from a Categorical is inverse transform sampling: build cumulative probabilities [p₁, p₁+p₂, ..., 1], draw u ~ Uniform(0,1), return the index of the first cumulative value ≥ u.

## Source

- Lesson: `Teach/ai-engineering/lessons/0002-probability-foundations.html`

## Sources

- Categorical distribution: https://en.wikipedia.org/wiki/Categorical_distribution
- Multinomial distribution: https://en.wikipedia.org/wiki/Multinomial_distribution
