<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Information_content | verified-by=fact-check-agent | date=2026-10-26 -->

# Information Content (Surprise)

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 + Olah (Visual Information Theory) · **Lang:** Python
> **Insight:** I(x) = −log p(x). Rare events carry more surprise; certain events carry zero. The minus sign makes surprise non-negative.

## Definition

I(x) = −log p(x). Log base 2 gives bits; natural log gives nats (1 nat ≈ 1.4427 bits).

## Why the minus sign

Probabilities live in (0, 1], where log p ≤ 0 — raw log p is most *negative* for rare events, the wrong direction for "surprise". The minus flips it: −log p ≥ 0, large for unlikely events, exactly 0 at p = 1.

## Code-length view (Olah)

−log p is the optimal code length for an event of probability p: p = 1/8 → about 3 bits. Rare events need long codes; common events need short ones.

## Examples

| Event | p | −log₂(p) |
|---|---|---|
| Fair coin heads | 0.5 | 1 bit |
| Die face | 1/6 | ≈ 2.585 bits |
| 1-in-1000 event | 0.001 | ≈ 9.97 bits |
| Certain event | 1.0 | 0 bits |

## Nearest neighbor

Surprise is per-event; [[Entropy (Average Surprise)]] averages it over a distribution. Feeds into [[Cross-Entropy from NLL]] (surprise under the model's distribution).

## Related

- [[Entropy (Average Surprise)]]
- [[Cross-Entropy from NLL]]
- [[PMF vs PDF]]

## Sources
- Wikipedia, "Information content": https://en.wikipedia.org/wiki/Information_content
- Shannon, "A Mathematical Theory of Communication" (1948): https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf
