<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Logits & Log-odds

> **Type:** concept (supporting) · **Track:** AIEFS · **Source:** Rohit P1 L09 (CP6 follow-ups) + PyTorch `CrossEntropyLoss` docs · **Lang:** Python
> **Insight:** Logits are unnormalized scores; softmax turns them into probabilities. "Logit = log-odds" is exact only for two classes — in multi-class the log-odds live in logit *differences*.

## Logits

z = Wx + b at the head; p_c = e^{z_c} / Σ_j e^{z_j} ([[Softmax Function]]). Only differences matter — shift invariance: z + c·1 leaves p unchanged, so an absolute logit is not a probability of anything. Losses take raw logits ([[Softmax Subtract-Max Trick]] / LogSoftmax + NLLLoss) for numerical stability, and a logit gap is exactly the "confidence" the loss grades.

## Log-odds

- Two classes: z = log(p/(1−p)) exactly, and p = σ(z). This is the only place where "logit" and "log-odds" are the same object.
- K classes: the invariant object is the pairwise log-odds **z_c − z_j = log(p_c/p_j)**. A multi-class logit is a log-odds only relative to a designated reference class.
- Probability 1 ⇔ log-odds → +∞: certainty sits at infinity, which is why [[Label Smoothing]] exists.

## Why the log stretch matters

Probability space squeezes certainty: 0.999 → 0.9999 shrinks the error mass 10× but moves only 0.001 in linear distance. Log-odds re-rules the line so equal multiplicative changes are equal steps — log 999 ≈ 6.9 nats → log 9999 ≈ 9.2 nats — which is exactly the −log p_true loss scale and which makes evidence additive (Bayes updates add in log-odds). The middle of the line is compressed intentionally: what looks "lost" near p = 0.5 is the resolution that the extremes buy.

## Nearest neighbour

Logits are *scores before normalization* (any real value, no constraint); probabilities are the normalized, bounded versions. Log-odds is a particular re-parameterization of probability; entropy/information quantities ([[Information Content (Surprise)]], [[Cross-Entropy from NLL]]) are built on −log p, not on log-odds.

## Related

- [[Softmax Function]]
- [[Label Smoothing]]
- [[Cross-Entropy from NLL]]
- [[Perplexity]]
- [[Bits vs Nats]]

## Source

- Rohit ai-engineering-from-scratch — `phases/01-math-foundations/09-information-theory/docs/en.md`
- PyTorch `torch.nn.CrossEntropyLoss` — https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html (takes raw logits)
- https://en.wikipedia.org/wiki/Logit
- Lesson `Learning System/Lessons/Lesson — Information Theory — 2026-09-11.md` (CP6 follow-ups, 2026-09-24: logits/softmax, two-class exactness, logit differences, shift invariance, the squeeze/stretch elaboration), teaching note `Learning System/Sessions/Session — Information Theory (P1 L09 resume, CP6 + Feynman + final quiz) — 2026-09-24.md`, Learning Record 0008.
