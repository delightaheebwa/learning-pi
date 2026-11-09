<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Cross-Entropy from NLL

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L06 + Rohit P1 L09 (its `en.md` uses the ML lettering — see the conventions table) + Olah (Visual Information Theory) + PyTorch `CrossEntropyLoss` · **Lang:** Python
> **Insight:** H(P,Q) = Σ q(x)·(−log₂ p(x)) — the model's surprise, weighted by the truth. It is the CE loss, it equals the NLL under one-hot labels, and it never falls below the entropy of the *true* distribution.
> **Also named in this track:** *Cross-entropy (H(P,Q), CE loss, NLL)* — Rohit P1 L09, Checkpoint 3.

## Definition (two distributions)

H(P,Q) = Σ_x q(x)·(−log₂ p(x))

The two letters do different jobs:

- **q(x) — the weights — the true/data distribution Q.** The average is taken over what actually happens.
- **p(x) — the surprises — the model distribution P.** Each surprise −log₂ p(x) is scored against the model.

In words: *the average surprise the model assigns to the truth*. No labels are needed — it is defined for any two distributions over the same events.

## Letter conventions (the classic confusion)

Both conventions write "H(P,Q)" but swap which letter means the truth:

| Convention | Weights (truth/data) | Surprises (model) | Floor |
|---|---|---|---|
| **Olah (Visual Information Theory) — and this lesson as taught** | Q (the second argument — the truth) | P (the first argument — the model) | H(P,Q) ≥ **H(Q)** |
| **Rohit `en.md` (the P1 L09 source doc) + most ML code and texts** | P (the labels y) | Q (the model ŷ) | H(P,Q) ≥ **H(P)** |

Both are correct — it is the same formula with the letters renamed, and for the same pair of distributions the number is identical. What never changes: **the floor is the entropy of the distribution that supplies the weights — the data's entropy.** Anchor phrase: "in cross-entropy − entropy = KL, the entropy term is always the data's entropy."

**The letters used in this lesson are a deliberate deviation from the cited source, not something the source says.** Rohit's P1 L09 `docs/en.md` writes `H(P, Q) = −Σ p(x)·log q(x)` with "P is the true distribution (the labels). Q is your model's predictions", and `D_KL(P ‖ Q) = H(P, Q) − H(P)` — that is the ML lettering in the table's second row. This page and the lesson's worked examples use Olah's lettering instead (truth in Q, model in P), so the floor reads H(Q). When cross-checking against the `en.md`, translate the letters first.

So "H(P,Q) ≥ H(P)" is the floor rule only under the Rohit/ML lettering (P = truth). Under this lesson's lettering it is **not a valid floor rule** — the floor is H(Q) — and it can fail outright: truth Q = (0.99, 0.01) with model P = (0.9, 0.1) gives H(P,Q) ≈ 0.184 bits, below H(P) ≈ 0.469 bits. Both worked coins on this page happen to satisfy it, which is exactly why the tracked "floor = H(P)" misconception is sticky: check the letters, never the coincidence.

## Loss view (Rohit P1 L06)

With one-hot labels the truth q is 1 on the correct class and 0 elsewhere, so every term but one vanishes:

L = −Σ_j y_j log(ŷ_j) = −log(ŷ_correct)

That is exactly the negative log-likelihood ([[Negative Log-Likelihood (NLL)]]) — the CE loss *is* the NLL. Small ŷ_correct → large loss and large gradient; minimizing pushes ŷ_correct toward 1 without forcing the other outputs to be equal.

Gradient through softmax: ∂L/∂z_j = softmax(z)_j − y_j.

PyTorch: `nn.CrossEntropyLoss()` takes **raw logits** plus integer class targets, applies `log_softmax` internally, and averages the per-example NLL over the batch (`reduction='mean'`, the default). Do not pass softmax outputs (that double-applies the softmax).

## Why minimizing cross-entropy works

H(P,Q) = H(Q) + KL(Q∥P) — the KL bridge below. H(Q) depends only on the data, so it is a constant with respect to the model's parameters: minimizing cross-entropy is exactly minimizing KL(Q∥P), the extra bits the model wastes over the best possible code. The floor H(Q) is unreachable unless the model can match the truth exactly.

## Floor rule

H(P,Q) ≥ H(Q), with equality **iff P = Q** (Olah convention; read ≥ H(P) in the Rohit/ML letters).

Perfect-model check: if the model *is* the data (P = Q) then H(P,Q) = −Σ q(x) log q(x) = H(Q). An imperfect model scores above the floor, and the gap is the KL divergence.

Worked coin — truth Q = (0.75, 0.25), model P = (0.5, 0.5) (a fair coin):

```
H(P,Q) = 0.75·(−log₂0.5) + 0.25·(−log₂0.5) = 1.0 bit     (exact)
H(Q)   = −0.75·log₂0.75 − 0.25·log₂0.25   ≈ 0.811 bits  ← the floor
H(P)   = 1.0 bit (the model is a fair coin)              ← NOT the floor
KL(Q∥P) = 1.0 − 0.811                     ≈ 0.189 bits
```

Misconception to avoid: calling the floor "the model's own entropy H(P)". Here H(P) = 1.0 bit is the *model's* entropy, not the floor; the floor is the truth's 0.811 bits. The floor is set by the data, not by the model. (Tracked in `Core/🧯 Mistakes.md`, 2026-09-12 row; re-sealed on exit-ticket E3 with a different coin: Q = (0.9, 0.1), P = (0.25, 0.75) → H(P,Q) = 1.84 bits, floor H(Q) ≈ 0.47 bits, not the near-miss H(P) ≈ 0.81 bits.) The 2026-09-14 regression on the **direction** (picked H(P,Q) ≤ H(Q), tag sure) was re-tested by retrieval on 2026-09-18: H(P,Q) ≥ H(Q) picked under `sure`, with the grade-audit agreeing — so the direction now holds both after the explanation and under retrieval, and that ledger row graduates.

**Why the floor is a theorem, not a coincidence.** H(P,Q) = H(Q) + KL(Q∥P), and KL ≥ 0 *is* Gibbs' inequality — proved in one line from the concavity of log (Jensen): Σ_i Q_i·log₂(P_i/Q_i) ≤ log₂( Σ_i Q_i·(P_i/Q_i) ) = log₂( Σ_i P_i ) = log₂ 1 = 0, then negate term by term. So the floor rule and KL's non-negativity are one fact stated twice; [[KL Divergence]] carries the proof, the deliberate numerator reversal (P/Q collapses to Σ P = 1 — the KL direction Σ Q_i²/P_i does not) and the rebate/cost reading of the per-term signs.

## The floor as an error detector (2026-09-21)

H(P,Q) ≥ H(Q) is not only a fact to recall — it is a free sanity check on every computation in this family. On 2026-09-21 a mutual information computed on a fresh joint came out as **−0.119 bits**: magnitude exact, sign impossible, because the arithmetic had been arranged as H(X,Y) − H(X) − H(Y) instead of H(X) + H(Y) − H(X,Y). I(X;Y) ≥ 0 is the same statement as H(P,Q) ≥ H(Q) and KL ≥ 0, read on a joint and its marginals, and it caught the flip even though the ordering had been recalled correctly in isolation — a negative information quantity should feel like a negative probability. The learner then reused the rule as a detector on the exit ticket, rejecting a reported I(X;Y) = −0.3 bits on nonnegativity alone. Cross-entropy below its own H(Q) — or any of these quantities below its floor — is a flip, never a discovery.

The paired arithmetic that makes the floor usable in practice: two routes to one number, on the fresh joint [[0.35, 0.15], [0.15, 0.35]] (marginals 0.5/0.5, so independence predicts 0.25 per cell).

```
entropy difference: H(X) + H(Y) − H(X,Y) = 1 + 1 − 1.8813 = 0.1187 bits
KL / ratio route:   diagonal ratio 1.4 → 2(0.35·log₂1.4) ≈ +0.3398 (costs)
                    off-diagonal 0.6   → 2(0.15·log₂0.6) ≈ −0.2211 (rebates)
                    total ≈ +0.1187 bits
cross-entropy route: 2.000 bits (every cell at −log₂0.25 = 2) − H(X,Y) 1.8813
                    = 0.1187 bits of KL
```

The last line is the identity of this page doing its job: the joint scored against the uniform independence model costs exactly 2.000 bits, the joint's own entropy is 1.8813 bits, and the difference is the KL — which for this pair *is* the mutual information. Every term in the ratio route is that cell's cross-entropy contribution q·(−log₂ p) minus its entropy contribution q·(−log₂ q), summed under the truth's weights.

## KL bridge — [[KL Divergence]]

KL(Q∥P) = H(P,Q) − H(Q) ≥ 0    (Olah convention: weights from Q)

Equivalently H(P,Q) = H(Q) + KL(Q∥P) — cross-entropy = the data's entropy + the model's excess. Under the Rohit/ML letters (P = truth) the identical identity reads KL(P∥Q) = H(P,Q) − H(P).

Coin numbers above: 1.0 − 0.811 = 0.189 bits. KL is zero iff the two distributions agree, and both KL and cross-entropy are directional: swapping which distribution supplies the weights changes the value (for this coin pair the reversed KL is 0.208 bits, and cross-entropy with the letters swapped is 1.208 bits). CP4 (KL) was practiced and graded pass on 2026-09-14, so this identity is banked — [[KL Divergence]] carries the full treatment.

## Units

log base 2 → bits; natural log → nats (1 nat ≈ 1.4427 bits, so 0.811 bits ≈ 0.562 nats). Fix the base per problem — mixing bits and nats is a silent factor of 1.4427. PyTorch reports cross-entropy in nats.

## Nearest neighbour

[[Entropy (Average Surprise)]] H(Q) is a single distribution's own expected surprise — the best achievable when the model *is* the data. Cross-entropy H(P,Q) scores a model *against* the data; subtract the data's entropy and the leftover is KL. [[Negative Log-Likelihood (NLL)]] is the same quantity in training clothes (one-hot labels), and [[Information Content (Surprise)]] is the single-event term −log p(x) that both are built from.

## Related

- [[Entropy (Average Surprise)]]
- [[Information Content (Surprise)]]
- [[Negative Log-Likelihood (NLL)]]
- [[KL Divergence]]
- [[Softmax Function]]
- [[Loss Functions (PyTorch)]]

## Source

Rohit P1 L06 (CE from NLL) + P1 L09 (Information Theory) — source doc: https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/09-information-theory/docs/en.md (uses the ML lettering, P = truth; this page teaches Olah's) — plus Olah, *Visual Information Theory* (https://colah.github.io/posts/2015-09-Visual-Information/) and the PyTorch `nn.CrossEntropyLoss` docs.
