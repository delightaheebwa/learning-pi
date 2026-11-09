<!-- provenance: status=verified | source=https://github.com/karpathy/makemore ; https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf | verified-by=fact-check-agent | date=2026-10-26 -->

# Hidden Layers Generalize via Shared Weights

**The problem:** A trigram needs 27³ entries. A 10-character context needs 27¹⁰ ≈ 200 trillion entries. Counting tables explode exponentially with context length.

**The neural fix:** Hidden layers with **shared weights**.

Instead of one row per possible character sequence, a hidden layer uses a fixed number of neurons (e.g. 200) that all work together:

```text
Hidden State = tanh(Inputs · W₁ + b₁)
```

**Weight sharing:** Every neuron in the hidden layer fires on every input. The pattern "if the last 4 characters are 'scop', the next character is probably a vowel" is a single neuron's behavior — learned once, applied everywhere. This is fundamentally different from counting, where "th → e" and "sh → e" are separate table entries with zero shared information.

**Why it works at test time:** The model doesn't learn on the fly. During training, the hidden layer learns general pattern detectors. At test time, these detectors are frozen but fire on any input. A model that's never seen "microscop" can predict it correctly because it has seen the sub-pattern "scop" in "telescop" — and the shared weights recognize the pattern.

| Model | Context Scaling | Unseen Combinations |
|---|---|---|
| Counting table | Exponential (27^N) | Fails (0 count → -inf loss) |
| Hidden layer NN | Linear (add fixed neurons) | Generalizes via shared weights |

Related: [[Distributed Representations (Character Embeddings)]] | [[Bigram Language Model]]

Part of: Socratic tutoring session on neural network scalability (Gemini)

## Sources
- Bengio et al., "A Neural Probabilistic Language Model" (2003): https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf
- Karpathy, "makemore": https://github.com/karpathy/makemore
