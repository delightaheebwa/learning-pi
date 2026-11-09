# Review — Cross-Entropy from NLL

> **Date:** 2026-09-09
> **Concept:** Cross-Entropy from NLL
> **Type:** concept · **Track:** aiefs
> **Mistake retry:** Yes (previous fail 2026-09-06 — inverted −log mechanism)
> **Result:** PASS ✅
> **Question (discriminative):** In cross-entropy loss L = −log(ŷ_correct), what happens to the loss when the model assigns a very small probability (say 0.01) to the correct class?
> **Answer:** B — The loss becomes large (−log(0.01) ≈ 4.6) — CE penalizes confident wrong predictions harshly
> **Grade audit:** ✅ Gate confirmed pass
> **Mastery:** 0.62 · **Feynman:** fail (advisory)
> **Next review:** 2026-09-15
> **Interleaving:** discriminative (previous was also discriminative — mistake retry overrides alternation)

## Key Insight
Small ŷ_correct → large loss (−log amplifies). Previously thought CE "keeps values small" — now corrected. CE is effective precisely because it heavily penalizes confident wrong predictions.
