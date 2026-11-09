# Learning Record 0008 — Perplexity, units, and label smoothing

- **Date:** 2026-09-24
- **Lesson:** Information Theory (Phase 1 L09) — CP6 + Feynman + final cumulative quiz (lesson completed)
- **Concepts:** Perplexity (new), Bits vs Nats (new), Label Smoothing (new), Logits & log-odds (supporting), Entropy (repaired regression), KL Divergence / Mutual Information / Variation of Information (retrieval-confirmed)

## What was learned

1. **Bits vs nats:** log base is a pure unit change — bits (log2, information theory), nats (ln, ML convention, PyTorch/TF default), hartleys (log10, rare); 1 nat = 1.4427 bits. Detector: cross-entropy in bits → exponent base 2; in nats → base e. Applied: 2.3 nats → 3.3 bits (pass).
2. **Perplexity** = 2^H(P,Q) in bits, e^H in nats — the effective number of equally likely choices; uniform over k → PPL exactly k; GPT-2 ~30, modern models single digits. Perplexity's "uniform" is a hypothetical yardstick (a non-uniform model can have PPL 7), *not* an ingredient — unrelated to label smoothing's uniform. Staging: perplexity is an evaluation-time, output-side conversion; label smoothing is a training-time, input-side target modification. First computation failed (11.048 ≈ e^2.4 — nats base on a bits value) and was repaired in-session.
3. **Label smoothing:** soft_target = (1−ε)·one-hot + ε/K; the one-hot structure survives scaled by (1−ε) (0.84/0.04 for ε=0.2, K=5 — the 0.2-everywhere answer is the ε=1 extreme that erases the label). The smoothed loss L = (1−ε)·CE(hard, pred) + ε·H_uniform(pred) is ordinary CE against the soft target, regrouped — ε/K lives in the second term (ε·H_uniform = Σ(ε/K)(−log p_c)), which penalizes predictions far from uniform. Motivation: one-hot targets demand probability 1 ⇒ infinite logits ⇒ overconfidence chase; smoothing removes the demand. Calibration/regularization reading. Open question surfaced by the learner: an adaptive, task-dependent ε (distillation as the principled informed version).
4. **Logits & log-odds:** unnormalized scores; softmax = exp/normalize; "logit = log-odds" exact only in two-class; in multi-class, pairwise log-odds are logit differences (z_c − z_j = log p_c/p_j; shift-invariance). Probability-space squeeze vs log-odds stretch: 0.999→0.9999 = 10× error-mass shrink but 0.001 linear; log-odds re-rules to odds-ratio distance and makes evidence additive (Bayes); certainty sits at +∞ — why one-hot targets need infinite logits.
5. **Entropy regression caught and repaired:** on the final quiz the learner computed an *unweighted* surprise sum (1+2+2 = 5) — the weights had "vanished". Repair: the weights ARE the probabilities (the distribution feeds itself — p_i inside the log as surprise generator, outside as weight); isomorphic re-test on a 4-sided die passed (1.75 bits, sure).

## Evidence (highest Bloom level demonstrated)

- **Evaluate:** Q5 — comparing models cross-unit (4 nats vs 5 bits) required unit conversion before comparison; answered correctly under sure.
- **Analyze:** Q4 VI/MCQ — two-clause fact jointly correct (V=0 iff mutual determinism + VI metric/MI anti-metric).
- **Apply:** KL via floor identity (0.25 bits), MI = KL(joint ∥ product) retrieved cold (the repaired 09-18 slip), V from marginals (1.1 bits).
- Feynman explain-back passed on attempt 3 (rubric: why-used, KL-vs-CE floor distinction, GPT-2 concrete anchor).

## Misconceptions / corrections

- Unweighted-surprise entropy slip (application error; repaired + isomorphic re-test pass same session).
- Nats-base-on-bits-value perplexity slip (application error; repaired same session).
- ε=1-extreme misread of the smoothing mixture (application error; repaired same session).
- Feynman floor sentence sharpened: both CE and KL have floors (CE ≥ H(data), KL ≥ 0).

## Status

- Curriculum row L09 Information Theory → done (pending Clerk reconciliation). Next: L10 Dimensionality Reduction.
