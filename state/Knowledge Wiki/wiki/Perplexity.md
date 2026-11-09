<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Perplexity

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 (Information Theory) + PyTorch `CrossEntropyLoss` docs · **Lang:** Python
> **Insight:** Perplexity = 2^H in bits (e^H in nats) — the *effective number of equally likely choices* a model is hesitating between. A uniform model over k outcomes has perplexity exactly k.

## Definition

PPL = 2^{H(P,Q)} with the cross-entropy in bits, or e^{H(P,Q)} with it in nats (see [[Bits vs Nats]]).

Equivalent reading: PPL = 1 / (the geometric mean of the probabilities the model assigns to the true tokens) — exponentiating the average log-probability undoes the log and turns "average surprise" into "a count of choices". It is a monotone re-expression of cross-entropy, so ranking perplexities is ranking cross-entropies; only compare models on the *same* tokenization.

## The uniform anchor

Uniform over k → H = log₂ k → PPL = 2^{log₂ k} = k. So perplexity reads directly as "as uncertain as if it were choosing uniformly among k options".

- GPT-2 ≈ 30 on standard LM benchmarks; modern frontier models sit in the single digits.
- Perplexity is reported per token; a change of tokenizer changes the number without changing the model.

## Two unrelated "uniform"s (2026-09-24)

- Perplexity's uniform = a **hypothetical yardstick**: every distribution has PPL = 2^H, and a *non-uniform* model can have PPL 7. Nothing in the model is uniform.
- [[Label Smoothing]]'s uniform = a **real ingredient** of the training target (the ε/K share).

Same word, unrelated mechanisms. The staging differs too: perplexity is an **evaluation-time, output-side** conversion (mainly LM reporting), while label smoothing is a **training-time, input-side** modification of the target. There is no cross-entropy → perplexity → smoothing pipeline.

## A third use: t-SNE's per-point perplexity (2026-10-09)

The same `2^H` reappears in t-SNE with a different object underneath it. Every point gets its own neighbour distribution `P_i`, and t-SNE tunes that point's bandwidth `σ_i` by binary search until `Per(P_i) = 2^{H(P_i)}` equals the user's **perplexity knob** (typical 5–50):

- It reads as the *effective* number of neighbours the point attends to — a soft count (23.7 is a legal value), not a cutoff at *k*.
- **Ceiling:** `P_i` lives on the other `n−1` points, so the most spread-out it can be is uniform → `H = log₂(n−1)` → `Per ≤ n−1`. On 20 points a knob of 30 is an unreachable target; this is the mechanism behind the "perplexity must be smaller than the number of points" guardrail.
- **Difference from the reading above:** here the uniform anchor is *reachable* (a large enough `σ_i` flattens `P_i` toward uniform), whereas a language model's perplexity uniform is a hypothetical yardstick the model never realizes.

See [[t-SNE (Dimensionality Reduction)]].

## Unit discipline (the practiced slip, 2026-09-24)

Give the entropy in the base whose exponential you use: cross-entropy in bits → 2^H; in nats → e^H (the two bases differ by a factor 1.4427 — 1 nat = 1.4427 bits).

Worked example, one H on both sides — **H = 5 bits**: the correct perplexity is 2^5 = 32; applying the nats base to that same 5-bit H instead gives e^5 ≈ 148.4, not 32. The repair is the detector on [[Bits vs Nats]] ("bits → base 2, nats → base e"). Cross-model comparison must convert first — 4 nats = 5.77 bits > 5 bits.

*Recorded session slip (not part of the worked example above): the CP6 practice answer on that 5-bit item was "11.048 ≈ e^{2.4}" — the learner's verbatim answer as recorded, kept for the record (Learning Record 0008).*

## Nearest neighbour

[[Cross-Entropy from NLL]] is the number; perplexity is that number re-expressed as a count of equally likely choices. It is *not* the model's own entropy H(P) — it is built from the cross-entropy against the data, so its floor is the data's entropy expressed in the same base.

## Related

- [[Cross-Entropy from NLL]]
- [[Entropy (Average Surprise)]]
- [[Bits vs Nats]]
- [[Label Smoothing]]
- [[Logits & Log-odds]]
- [[t-SNE (Dimensionality Reduction)]]

## Source

- Rohit ai-engineering-from-scratch — `phases/01-math-foundations/09-information-theory/docs/en.md`
- PyTorch `torch.nn.CrossEntropyLoss` — https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
- Wikipedia — Perplexity — https://en.wikipedia.org/wiki/Perplexity
- Lesson `Learning System/Lessons/Lesson — Information Theory — 2026-09-11.md` (CP6, 2026-09-24), teaching note `Learning System/Sessions/Session — Information Theory (P1 L09 resume, CP6 + Feynman + final quiz) — 2026-09-24.md`, Learning Record 0008.
