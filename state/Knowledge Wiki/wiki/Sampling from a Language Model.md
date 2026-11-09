<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Sampling from a Language Model

## Overview
Generating text from a language model by repeatedly picking the next token according to the model's predicted probability distribution.

## Bigram Sampling
```python
g = torch.Generator().manual_seed(2147483647)
ix = 0  # start with sentinel '.'
while True:
    p = P[ix]           # row = distribution for current char
    ix = torch.multinomial(p, 1, replacement=True, generator=g).item()
    if ix == 0:         # sentinel '.' → end of word
        break
    out.append(itos[ix])
```

## Autoregressive Loop
1. Start with sentinel token
2. Look up probability distribution for current token
3. Sample next token from that distribution
4. Feed sampled token as the next input
5. Repeat until end sentinel is generated

## Key Insight
The same sampling loop works at every scale — bigram, RNN, GPT — just with richer probability distributions. The interface is always: "given context, give me P(next token)."

## Sources

- Karpathy, "The spelled-out intro to language modeling: building makemore" (Neural Networks: Zero to Hero, Lecture 2) — https://www.youtube.com/watch?v=PaCmpygFfXo
- makemore repository: https://github.com/karpathy/makemore
