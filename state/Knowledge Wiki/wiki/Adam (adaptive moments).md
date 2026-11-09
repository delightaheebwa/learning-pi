<!-- provenance: status=verified | source=https://arxiv.org/abs/1412.6980 ; https://arxiv.org/abs/1705.08292 ; https://www.ruder.io/optimizing-gradient-descent/ | verified-by=fact-check-agent | date=2026-10-26 -->

# Adam (adaptive moments)

Adam combines two running averages per weight — momentum (first moment, mean gradient) and RMSProp (second moment, mean squared gradient) — with a bias-correction step, to give each weight its own adaptive learning rate without manual tuning.

## The equations (Kingma & Ba, 2015)

Given gradient \(g\) at step \(t\), with \(\beta_1 = 0.9\), \(\beta_2 = 0.999\), \(\epsilon = 10^{-8}\):

- First moment: \(m \leftarrow \beta_1 m + (1 - \beta_1) g\) — mean gradient (direction)
- Second moment: \(v \leftarrow \beta_2 v + (1 - \beta_2) g^2\) — mean squared gradient (scale)

Bias correction:

- \(\hat{m} = m / (1 - \beta_1^t)\)
- \(\hat{v} = v / (1 - \beta_2^t)\)

Update:

- \(w \leftarrow w - \eta \, \hat{m} / (\sqrt{\hat{v}} + \epsilon)\)

Default: \(\eta = 0.001\).

## Why bias correction

Both \(m\) and \(v\) are initialized to zero. On early steps, this zero-initialization biases the estimates downward (too small), making the first steps timid. Dividing by \((1 - \beta^t)\) compensates: at \(t=1\), \(\hat{m} = g\) (the true gradient, unshrunk), and as \(t\) grows, \(\beta^t \to 0\) so the correction fades to 1. It is not a hack — it compensates for the cold-start artifact and becomes irrelevant once history accumulates.

## Optimizer lineage (Ruder's genealogy)

1. SGD — one shared \(\eta\) for every weight. Can't handle weights with wildly different gradient scales.
2. Adagrad — divides by running *sum* of \(g^2\). Adapts per weight but the sum only grows, so effective lr shrinks to zero.
3. RMSProp — replaces the sum with an exponentially decaying *average* of \(g^2\) (\(v\)). Fixes the collapse.
4. Adam = RMSProp + momentum + bias correction. Combines both averages, corrects cold start.

## Key insight from Rosenbrock race (CP3, 2026-09-08)

On a clean, smooth, deterministic benchmark (Rosenbrock), **SGD with momentum converged first** (~2941 steps) while **Adam converged later** (~6156 steps). The per-weight adaptivity Adam provides is not needed on a two-dimensional problem with uniform curvature structure — the overhead costs time. But on real neural nets (sparse, high-dimensional, wildly different gradient scales per weight), Adam's self-tuning is a major practical advantage.

A second, separate claim: tuned SGD + momentum *can* reach lower final loss / better test accuracy than Adam on some tasks, argued to be because adaptive methods find sharper minima that generalize worse (Wilson et al., 2017, "The Marginal Value of Adaptive Gradient Methods"). This is empirical and task-dependent, not a theorem — on many benchmarks Adam/AdamW matches or beats SGD. Note the sharp-minima explanation is a hypothesis under active debate (e.g. "sharp minima" reparameterization critiques), so treat it as one account, not settled fact.

## When to use

- **Adam** is the robust default — good out of the box with little tuning (Kingma & Ba: "typically require little tuning").
- **SGD + momentum** can achieve better final accuracy when tuning budget allows; Wilson et al. show adaptive methods can generalize worse on some problems, while other benchmarks show the opposite.
- The choice is task-dependent, not a fixed hierarchy.

## Related pages

- [[Gradient descent]]
- [[Momentum (SGD with Momentum)]]
- [[Learning Rate]]
- [[Optimizers (SGD, Adam, AdamW)]]

## Sources

- Kingma & Ba, "Adam: A Method for Stochastic Optimization" (ICLR 2015), Algorithm 1 and §3.1 defaults (α=0.001, β₁=0.9, β₂=0.999, ε=1e-8): https://arxiv.org/abs/1412.6980
- Ruder, "An overview of gradient descent optimization algorithms": https://www.ruder.io/optimizing-gradient-descent/
- Wilson, Roelofs, Stern, Srebro & Recht, "The Marginal Value of Adaptive Gradient Methods in Machine Learning" (NeurIPS 2017): https://arxiv.org/abs/1705.08292
- PyTorch `Adam` implementation defaults: https://pytorch.org/docs/stable/generated/torch.optim.Adam.html
- Lesson: Phase 1 L08 — Optimization (Gradient Descent Family), 2026-09-07/08
- Note: the Rosenbrock step counts (~2941 vs ~6156) are a local experiment (CP3), not independently reproducible from these sources.

**Corrections (2026-10-26):** softened the SGD-vs-Adam generalization claim — "achieves lower final loss on many practical tasks" is too strong; it is an empirical, task-dependent finding (Wilson et al.) and the sharp-minima account is contested. Equations and defaults checked against the paper and match.


## Role summary (handwritten notes, 2026-09-08)

- **m** (tracked by β₁): the moving-average direction ⇒ tells the update **which way** to go.
- **v** (tracked by β₂): the moving-average scale ⇒ tells the update **how big a step** each weight can tolerate.

Consistently large gradient → v is large → scale down → steps stay bounded. Rare weight with very large movement → the size of the scaling matrix rescales the direction.

Adam is the reliable default — a self-tuner for weight learning rates. On messy real neural-net objective function landscapes with wildly different gradient scales across parameters, it just works out of the box. But Adam isn't "better" in all senses: SGD + momentum often beats Adam on final test accuracy because SGD's residual noise keeps it from settling into sharp minima (worse generalizers), whereas Adam's smooth adaptation can land in a sharp narrow valley that doesn't perform well on unseen data.

## Retrieval log (2026-09-26)

- Review FAIL metacognitive ("didn't know", own words) at the first graded retrieval of the m̂₂/v̂₂ machinery since L08. Walk-through delivered same session (fact-checked): m = smoothed direction (0.9 old + 0.1 new), v = smoothed ∣g∣²; the averages START at zero so early estimates are only a fraction of the way home — the hats divide by that fraction: m̂₂ = 0.00019/(1−0.81) = 0.001; v̂₂ = 1.999e−9/(1−0.998001) = 1e−6; step = 0.001/√1e−6 = 1.0 × lr. The units story: m̂/√v̂ is dimensionless (gradient units over gradient units) ≈ ±1 — Adam asks only which SIGN and steps by a fixed lr, i.e. scale-invariant sign-descent behavior. New Mistakes row (metacognitive); retry 2026-10-03. `next_review` 2026-10-03 (interval_index 1, consecutive_wrong 1).
