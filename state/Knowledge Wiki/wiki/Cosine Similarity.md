<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Cosine Similarity

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L02 + 3Blue1Brown · **Lang:** Python
> **Insight:** For unit vectors u·v = cos(θ). Measures alignment −1 to +1. Orthogonality is special case.

## Definition

u · v = |u| · |v| · cos(θ). For unit vectors: u · v = cos(θ).

## Scale
| Value | Angle | Meaning |
|-------|-------|---------|
| +1 | 0° | Same direction |
| 0 | 90° | Orthogonal |
| −1 | 180° | Opposite |

## Common Mistake

Confusing general meaning (continuous alignment) with special case (orthogonality).

## AI Applications

Word embeddings, semantic search, recommendation.

## Related

- [[Orthogonality]]
- [[Linear Algebra Intuition]]
- [[Word Embeddings (nn.Embedding)]]

## Sources

- https://en.wikipedia.org/wiki/Cosine_similarity
