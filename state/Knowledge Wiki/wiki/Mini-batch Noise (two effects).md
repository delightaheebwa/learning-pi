<!-- provenance: status=verified | source=legacy (P1 L08 lesson) + Keskar 2017 / Wilson 2017 / Li 2018 | verified-by=fact-check-agent | date=2026-10-26 | note=attribution corrected 2026-10-17 (in-session fact-check): SGD-vs-Adam gap = Wilson et al. 2017; sharp minima = Keskar et al. 2017; Li et al. 2018 = visualization only -->

# Mini-batch Noise (Two Effects)

The noise in SGD and mini-batches is not a bug. It does two genuinely different things — keep them on two different questions.

| Effect | Mechanism | Answers |
|---|---|---|
| **Optimization** | The noisy mini-batch gradient is **almost never exactly zero**, so SGD doesn't stall at **saddles / plateaus** | "Can I keep moving?" |
| **Generalization** | Noise stops you settling into **sharp minima** → you land in **flat minima** → better test accuracy | "Am I parking in a wide valley or a narrow crack?" |

## Full-batch exact vs mini-batch noisy estimate

With full-batch GD the gradient uses the entire dataset every step — the exact gradient. At a saddle where the true gradient is exactly zero, there is no direction to move, so it can sit on the flat spot. With mini-batch GD the gradient uses only a small random slice — a noisy estimate of the true gradient. Even where the true gradient is zero, the mini-batch estimate usually is not, and that random push moves the iterate off the saddle. (Handwritten notes, 2026-09-09.)

## The anchor

"**Escape**" goes with **saddles** (optimization). "**Avoid / settle into**" goes with **sharp minima** (generalization). One is about *moving*, one is about *where you stop*.

Saying "noise helps generalization" and "noise escapes saddles" in the same breath without separating them is the classic conflation — they act at different stages (training progress vs train→test gap).

## Why it matters: SGD vs Adam on test accuracy

Sharp minima are narrow pits overfit to training quirks — they generalize poorly. Flat minima are wide basins, whole neighborhoods of good solutions robust to the train→test shift — they generalize well. This is one reason SGD with momentum often beats Adam on final test accuracy even where Adam's adaptivity makes faster early progress: SGD's noise keeps it out of the sharp pits. (Attribution: the flat-vs-sharp generalization link is **Keskar et al. 2017**; the SGD-vs-Adam final-test-accuracy gap is **Wilson et al. 2017**. **Li et al. 2018** — filter normalization — is the loss-landscape *visualization* of sharp vs flat basins: it renders these objects, it is not the source of either generalization claim.)

## Related pages

- [[Saddle Points (critical point triage)]]
- [[Optimizers (SGD, Adam, AdamW)]]
- [[Optimizer Selection (Rohit heuristic)]]

## Sources

- **Lesson:** Rohit P1 L08 — Optimization (Gradient Descent Family), 2026-09-10
- **Source:** `phases/01-math-foundations/08-optimization/docs/en.md` (Rohit Phase 1 L08)
- **Primary source — sharp minima:** [Keskar et al. 2017 — *On Large-Batch Training for Deep Learning: Generalization Gap and Sharp Minima*](https://arxiv.org/abs/1609.04836) — the sharp-minima / generalization-gap claim.
- **Primary source — SGD vs Adam:** [Wilson et al. 2017 — *The Marginal Value of Adaptive Gradient Methods in Machine Learning*](https://arxiv.org/abs/1705.08292) — adaptive methods (Adam) can generalize *worse* than SGD on final test accuracy.
- **Primary source — visualization only:** [Li et al. 2018 — *Visualizing the Loss Landscape of Neural Nets*](https://arxiv.org/abs/1712.09913) — filter normalization; renders sharp vs flat basins. It is **not** the evidence for either generalization claim above.
- **Correction (2026-10-17):** this page previously closed the SGD-vs-Adam paragraph with “(Visualization: Li et al. 2018, filter normalization.)”, which credited the generalization gap to the visualization paper. The in-session fact-check re-attributed it: the SGD-vs-Adam test-accuracy gap is Wilson et al. 2017, the sharp-minima side is Keskar et al. 2017, and Li et al. 2018 is strictly the loss-landscape visualization. Page substance is unchanged — attribution only.
