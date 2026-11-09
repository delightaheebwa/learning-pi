# REVIEW: Posterior Probability — 2026-09-21 (II)

## Review Info

- **Date:** [[2026-09-21]] (second review session of the day)
- **Concept:** Posterior Probability
- **Slot:** 4 — due review 2026-09-21 + due mistake (2026-09-17 row)
- **Q Type:** discriminative (Last Q Type was definitional)

---

## Assistant's Prompt

> *"Same coin setup: 5 flips, 3 heads, θ = heads-probability, with prior p(θ). Write the posterior p(θ | D) as a proportionality in terms of the likelihood and the prior, then say in one phrase what each factor contributes."*

---

## Your Answer

- **Answer:** "posterior proportional to (prior * likelihood). the prior provides the belief of what the posterior should look like. the likelihood is the probability before observation. posterior is the result of multiplying those two"

---

## Assistant's Evaluation

- **Result:** Fail (grade-audit agreed)
- **Feedback:** Half-and-half, and the wrong half matters. The proportionality is right — p(θ|D) ∝ p(D|θ)·p(θ) — so the 09-17 slip (prior doubled, likelihood missing) is repaired. But the role descriptions are swapped: "the likelihood is the probability before observation" describes the PRIOR. The prior is the pre-data belief about θ; the likelihood is the post-data evidence factor — for each candidate θ, how well does it explain the observed data? It is the term that reweights the prior. With 3/5 heads the likelihood peaks near θ = 0.6, and that peak drags the posterior toward 0.6.
- **Attempt:** fail — mastery 0.19, interval_index 0, next_review 2026-09-24.
- **Mistakes row:** stays active, next 09-24 (formula half repaired; role half now the open item).
