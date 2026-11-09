<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Label Smoothing

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 (CP6) + PyTorch `CrossEntropyLoss` docs + Inception (Szegedy et al., 2016) · **Lang:** Python
> **Insight:** Replace the one-hot target with `soft = (1−ε)·one-hot + ε/K` — the label structure survives, scaled by (1−ε), with an ε/K smear over *every* class.

## The mixture

For K classes and true class c:

- soft target at c: (1−ε) + ε/K
- soft target at any j ≠ c: ε/K

At ε = 0.2, K = 5: **0.84** on the true class and **0.04** on each of the other four. At ε = 1 the mixture collapses to 1/K everywhere — the label is erased. (That extreme is what the CP6 practice answer picked: 0.2 everywhere at ε = 0.2, K = 5 — see the slip below.)

## The loss, regrouped

The smoothed loss is ordinary cross-entropy against the soft target, not against the one-hot:

L = (1−ε)·CE(hard, p) + ε·H_uniform(p),  with H_uniform(p) = −Σ_c (1/K)·log p_c.

Cross-entropy against the soft target is −Σ_c q_c log p_c; expanding q = (1−ε)·one-hot + ε/K gives the two terms, and the per-class coefficient **ε/K lives in the second term** (the ε·H_uniform term). That term penalizes predictions that sit far from uniform — it is the anti-overconfidence term.

## Motivation: what the one-hot actually demands

A one-hot target wants p_true = 1, i.e. −log p_true = 0, which only a runaway logit gap reaches in the limit — so the model is pushed into chasing certainty with ever-larger logits (see [[Logits & Log-odds]]). Smoothing lowers the demand to (1−ε) and puts a floor of ε/K under every other class, so a *finite* logit gap is optimal and the push stops. Two side readings: the target's entropy goes from 0 to positive (the loss floor lifts off 0), and the model is discouraged from saturating — a calibration / regularization effect.

## In code

PyTorch `CrossEntropyLoss(label_smoothing=ε)` takes ε as a float in [0, 1] (default 0.0), applies the Inception ratio-preserving mixture above, and is equivalent to `LogSoftmax` + `NLLLoss` on the soft target — in nats (see [[Bits vs Nats]]).

## The practiced slip (2026-09-24) and the open question

Practice item ε = 0.2, K = 5: answered "0.2 everywhere" (the ε = 1 pure-uniform target) instead of 0.84 / 0.04 — the smoothing amount was read as the whole target, missing that the one-hot structure survives scaled by (1−ε). Repaired with the mixture algebra the same session; the final-quiz own-words item then passed ("the target stops demanding probability 1, so finite logits suffice").

Open question (learner's own wonder-out, 2026-09-24): what would an information-theoretically principled *adaptive* ε look like? A task-dependent ε is a real research direction (distillation, Hinton 2015, is the principled informed-smoothing version — it replaces the uniform smear with the teacher's distribution); note the lever distinction below.

## Nearest neighbour

[[Laplace Smoothing]] / [[Add-1 Smoothing]] smooth **counts/estimates** (avoiding zero probabilities in naive Bayes); label smoothing smooths the **training target distribution** of a classifier or LM head. Same motive — remove an extreme demand — different object.

## Related

- [[Cross-Entropy from NLL]]
- [[KL Divergence]]
- [[Logits & Log-odds]]
- [[Perplexity]]
- [[Laplace Smoothing]]

## Source

- Rohit ai-engineering-from-scratch — `phases/01-math-foundations/09-information-theory/docs/en.md`
- PyTorch `torch.nn.CrossEntropyLoss` — https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html (`label_smoothing`, Inception mixture, LogSoftmax+NLLLoss equivalence, nats)
- Lesson `Learning System/Lessons/Lesson — Information Theory — 2026-09-11.md` (CP6, 2026-09-24), teaching note `Learning System/Sessions/Session — Information Theory (P1 L09 resume, CP6 + Feynman + final quiz) — 2026-09-24.md`, Learning Record 0008.

## Sources

- https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
- https://arxiv.org/abs/1512.00567
