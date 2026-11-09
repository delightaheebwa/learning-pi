<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# KL Divergence

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 + Olah (Visual Information Theory) · **Lang:** Python
> **Insight:** KL(Q∥P) = Σ q(x)·log₂(q(x)/p(x)) = H(P,Q) − H(Q) — the extra bits a model wastes over the truth's own entropy. Never negative, zero only when the model *is* the data, and not symmetric.

## Definition

KL(Q∥P) = Σ_x q(x)·log₂(q(x)/p(x))

In this lesson's letters **Q is the truth — it supplies the weights — and P is the model — it supplies the scored probabilities** — the same lettering as [[Cross-Entropy from NLL]]. Each event contributes its surprise *gap* log₂(q/p), averaged over what actually happens. (Rohit's `en.md` and most ML code flip the letters and write D_KL(P∥Q) = H(P,Q) − H(P); it is the same identity with the letters renamed — see the conventions table on the cross-entropy page.)

The operational form is cross-entropy minus the data's entropy:

**KL(Q∥P) = H(P,Q) − H(Q) = CE − H(data)**

## Two properties that define it

- **KL(Q∥P) ≥ 0** (Gibbs' inequality) — H(Q) is the average length of the optimal code for the truth ([[Entropy (Average Surprise)]]), and no other code beats it; the difference is the excess the model's distribution costs. For the coin below: 1.0 − 0.811 ≈ 0.189 bits.
- **KL(Q∥P) = 0 iff P = Q** — equality exactly when the model agrees with the data on every event. Terms where q < p contribute negatively and terms where q > p positively, and Gibbs' inequality says the positives always win unless the two distributions match — a theorem, not a coincidence: the one-line Jensen proof is in the section below.

## KL ≥ 0 is Gibbs' inequality — proved in one line of Jensen

The non-negativity of KL is not something you read off the shape of the formula; it is a theorem with a name and a one-line proof.

**Gibbs' inequality.** For any two distributions Q and P over the same outcome space (finite, or continuous densities), Σ_i Q_i·log₂(Q_i/P_i) ≥ 0, with equality **iff P = Q** — and KL *is* that sum. No joint structure and no independence assumption is needed: any two distributions on the same outcome space qualify.

**The one-line proof (Jensen).** log is concave, so for any weights w_i and inputs x_i, f(Σ w_i x_i) ≥ Σ w_i f(x_i). Take w_i = Q_i and x_i = P_i/Q_i:

```
Σ_i Q_i·log₂(P_i/Q_i)  ≤  log₂( Σ_i Q_i·(P_i/Q_i) )  =  log₂( Σ_i P_i )  =  log₂ 1  =  0
```

The inner sum collapses precisely because the weights are Q and Q is normalised: Σ_i Q_i·(P_i/Q_i) = Σ_i P_i = 1 — a number we know *without* knowing anything else about the two distributions. Now negate both sides (multiply the whole inequality by −1: arithmetic, not logical; ≤ flips to ≥). The negated left side is exactly KL, because log(a/b) = −log(b/a) term by term:

```
Σ_i Q_i·log₂(Q_i/P_i)  ≥  0        ⟺   KL(Q∥P) ≥ 0
```

**The deliberate numerator reversal.** KL keeps Q on top *and* Q is the weighting, but the Jensen step is applied to the flipped ratio P_i/Q_i. That is not a typo — only that direction collapses: Q_i·(P_i/Q_i) = P_i sums to 1, while the KL direction gives Σ_i Q_i·(Q_i/P_i) = Σ_i Q_i²/P_i, which on the Q = (0.5, 0.5) vs P = (0.9, 0.1) pair equals 0.25/0.9 + 0.25/0.1 ≈ 2.778 — a number that still depends on both distributions and collapses to nothing. So the proof routes through the Jensen-friendly twin (≤ 0) and flips back by term-wise negation. Rule to carry: **the weights are always the truth Q; the numerator tells you which direction the sum points** (Q on top → KL ≥ 0; P on top → the Jensen-friendly twin ≤ 0).

**Concavity means "the curve sits above its chords".** That is the definition doing the work: the average of the function values lies on the chord at the mixed input, while the function of the average lies on the curve above it. Numeric feel: log₂ at equal weights between 1 and 9 gives f(5) = 2.32 ≥ 1.585 = ½(0 + 3.17). In this proof it does exactly one job — swap "average, then function" for "function of the average", and the function of *that particular* average is log 1 = 0, a number we already know.

**Jensen vs Gibbs — the division of labour.** Johan Jensen (Danish; the inequality published 1906) supplied the *general* concave-function tool: f(Σ w_i x_i) ≥ Σ w_i f(x_i), equality iff all the x_i are equal (strictly concave f). Josiah Willard Gibbs (the distribution statement appears in his 1902 statistical-mechanics work) supplied the *specific* statement Σ p_i·log(p_i/q_i) ≥ 0, equality iff p = q. **"Gibbs is the what, Jensen is the how."**

**The rebate/cost reading (why the per-term signs behave).** Each term Q_i·log₂(Q_i/P_i) is signed by *who assigned more weight to that outcome*:

- **P_i > Q_i** (the model overestimates the outcome) → log₂(Q_i/P_i) < 0 → a per-outcome **rebate**: the model's code is shorter than the truth-optimal code there.
- **P_i < Q_i** (it underestimates the outcome) → log₂(Q_i/P_i) > 0 → a per-outcome **cost**.
- **P_i = Q_i** → exactly 0.

Both distributions sum to 1, so every overestimation is matched by an underestimation somewhere; and because the truth supplies the weights, the rebates can never out-pay the costs — that *is* Gibbs' inequality. Worked on Q = (0.5, 0.5) vs P = (0.9, 0.1): a rebate of 0.5·log₂(0.5/0.9) = −0.424 bits plus a cost of 0.5·log₂(0.5/0.1) = +1.161 bits gives KL = −0.424 + 1.161 = **0.737 bits** > 0. A large negative term does not make the floor harder to reach — it pulls the total *down* toward 0.

⚠️ **A per-term sign says nothing about "the relationship between P and Q".** The two distributions live over one outcome space with no pairing, so a negative term is *not* evidence of a negative relationship the way a correlation sign between two *variables* would be. The anti-correlated case is the trap in the other direction: X fair with Y = 1 − X has negative correlation yet *maximal* MI = 1 bit ([[Mutual Information]]). Terms are signed; the Q-weighted total is not.

**What it buys.** In the lesson's letters the floor follows immediately: H(P,Q) = H(Q) + KL(Q∥P) ≥ H(Q) ([[Cross-Entropy from NLL]]), and [[Mutual Information]] = KL(joint ∥ product of marginals) inherits ≥ 0 for free — no separate proof. The information-theoretic reading is the coding reductio: a negative KL would mean some code is shorter *on average* than the truth's own optimal code, which cannot happen.

## Not symmetric

KL measures a *directed* gap: swapping which distribution supplies the weights changes the average.

Coin — truth Q = (0.75, 0.25), model P = (0.5, 0.5):

```
KL(Q∥P) = H(P,Q) − H(Q) = 1.000 − 0.811 ≈ 0.189 bits   (CE − the data's entropy)
KL(P∥Q) = H(Q,P) − H(P) = 1.208 − 1.000 ≈ 0.208 bits   (the same move, letters swapped)
```

Both are small and both are non-negative, but they are different numbers — so "the KL" means nothing until the direction is named. Cross-entropy is directional in exactly the same way (the same swap moves CE from 1.000 to 1.208 bits).

A second pair — truth Q = (0.6, 0.4), model P = (0.9, 0.1):

```
KL(Q∥P) = 0.6·log₂(0.6/0.9) + 0.4·log₂(0.4/0.1) ≈ −0.3510 + 0.8000 ≈ 0.449 bits
KL(P∥Q) = 0.9·log₂(0.9/0.6) + 0.1·log₂(0.1/0.4) ≈  0.5265 − 0.2000 ≈ 0.326 bits
```

The gap is ≈ 0.12 bits, and which direction is larger is not something you can read off the shape of the two distributions — it depends on which event each distribution over-weights. Compute both, then name the direction. (This pair is the re-check that held the non-symmetry rule on 2026-09-15, after a resume warm-up had regressed it: the rule survives re-testing, not re-recalling. On 2026-09-16 a fresh non-symmetry item passed again, so the rule now holds across two sessions, and on 2026-09-21 the **identity** half was re-confirmed under fresh definitional recall (MCQ, tag `sure`, grade-audit agreed) — the CP4 identity is holding.)

## Why minimizing cross-entropy ≡ minimizing KL

H(Q) depends only on the data, so it is a constant with respect to the model's parameters:

min_θ H(P_θ, Q) = H(Q) + min_θ KL(Q∥P_θ)

Same argmin, same gradient direction — training on [[Negative Log-Likelihood (NLL)]] / cross-entropy *is* pulling the model distribution toward the data distribution. In general the floor H(Q) is unreachable; KL is the part that can be driven toward 0.

## Infinity, and why smoothing exists

If an event has q(x) > 0 while the model puts p(x) = 0, that one term q(x)·log₂(q/p) is +∞ — cross-entropy and KL become infinite there, not merely large. The data's own entropy H(Q) stays finite: that event is a real one and Q gives it positive probability, so it contributes q(x)·(−log₂ q(x)), a finite number. What diverges is the *model's* score for the event (log₂(1/p) → ∞), which is why both H(P,Q) and KL(Q∥P) blow up while H(Q) does not. A hard count-based model can hit that zero exactly (Naive Bayes with an unseen count — see [[Add-1 Smoothing]], [[Laplace Smoothing]]); a softmax model only approaches p(x) = 0 as a logit → −∞, so it yields a loss that grows without bound and a log-probability that eventually underflows to −inf. Never assign zero probability to something that can happen — label smoothing is the loss-side version of the same fix (CP6, not yet taught).

## Mutual information is a KL divergence

The same measure, built from a different pair of distributions, gives information theory's other headline quantity:

I(X;Y) = KL( p(x,y) ∥ p(x)·p(y) )

— the *joint* distribution measured against the product of its own marginals, i.e. exactly "how many bits are wasted by treating X and Y as independent". It is built in the same four moves as any other KL application:

1. **Roles.** The first argument is the truth and supplies the weights — the joint, what actually happens. The second is the model being scored — the independence claim p(x)·p(y).
2. **Baseline.** "X and Y are unrelated" is a *distribution*, not a vibe: for a joint with 0.5/0.5 marginals the independence claim is the uniform table [[0.25, 0.25], [0.25, 0.25]] — every cell predicted from the marginals alone.
3. **Score.** KL( p(x,y) ∥ p(x)·p(y) ) = Σ Σ p(x,y)·log₂( p(x,y) / (p(x)·p(y)) ).
4. **Number.** On [[0.45, 0.05], [0.05, 0.45]] the diagonal cells contribute +0.3816 bits each and the off-diagonal cells −0.1161 bits each: 2(0.3816) + 2(−0.1161) ≈ 0.531 bits — the same value the entropy route (H(X) − H(X|Y) = 1.000 − 0.469) and the bars route give.

Three notes that matter:

- **The arguments are distributions, not variables.** It is KL between the joint and the product of the marginals — not "between X and Y". Both are distributions over the same cells; swapping X ↔ Y relabels both sides together, which is why this is the one KL application that comes out **symmetric** (I(X;Y) = I(Y;X)) and 0 exactly when X and Y are independent.
- **MI inherits KL ≥ 0.** Its non-negativity needs no separate proof — it *is* Gibbs' inequality, read on a joint and its marginals. That inheritance settles the anti-correlation case: X fair with Y = 1 − X gives the joint [[0, 0.5], [0.5, 0]], so I = H(X) + H(Y) − H(X,Y) = 1 + 1 − 1 = 1 bit, the maximum for two binary variables. Signed direction is correlation's job; KL and MI measure distance from a baseline, not co-movement.
- **"Wasted bits" is the right reading.** The independence claim is the model, the joint is the truth, and the number is how many bits of the truth the independence story fails to capture — which is why a *high* KL here means "far from independence", not "a bad model of the joint".

**The ratio route, worked on a fresh joint (2026-09-21).** The same KL can be summed cell by cell instead of via CE − H(data). On [[0.35, 0.15], [0.15, 0.35]] (marginals 0.5/0.5, so the independence baseline is 0.25 in every cell) the diagonal cells have ratio 0.35/0.25 = 1.4 and contribute 2(0.35·log₂1.4) ≈ **+0.3398 bits** (costs), while the off-diagonal cells have ratio 0.15/0.25 = 0.6 and contribute 2(0.15·log₂0.6) ≈ **−0.2211 bits** (rebates) — total ≈ **0.1187 bits**, matching H(X) + H(Y) − H(X,Y) = 2 − 1.8813 exactly, and matching the cross-entropy route too: the joint scored against the uniform independence model gives Σ c·(−log₂ 0.25) = 2.000 bits, and 2.000 − 1.8813 = 0.1187 bits of KL. Each term is that cell's cross-entropy contribution minus its entropy contribution ([[Cross-Entropy from NLL]]), so the rebate/cost reading and the CE − H(data) identity are the same statement seen at two scales — the truth supplies the weights, so the rebates can never pay the costs. The first attempt at this computation came out negative from a sign/ordering flip; KL ≥ 0 rejected it (the detector note lives on the cross-entropy page).

Full treatment: [[Mutual Information]].

## Retrieval log (2026-09-24)

Final cumulative quiz of P1 L09: the floor identity carried the arithmetic (cross-entropy 1.75 bits − H(Q) 1.50 bits = **KL 0.25 bits**, pass), and the KL form of dependence — I(X;Y) = KL(p(x,y) ∥ p(x)p(y)) — came back **cold** (final-quiz Q3, pass) after the 2026-09-16 → 2026-09-21 repairs. Both `sure`, grade-audit agreed. The ∞ case rehearsed here is exactly what the smoothing family exists to remove: [[Label Smoothing]] on the target side, [[Laplace Smoothing]] / [[Add-1 Smoothing]] on the counts side.

## Units

log₂ → bits, ln → nats (1 nat ≈ 1.4427 bits, so 0.189 bits ≈ 0.131 nats). Changing the base multiplies every KL and cross-entropy number by the same constant, so it never moves the minimum — but mixing bits and nats is a silent factor of 1.4427. PyTorch's native losses report nats.

## Nearest neighbour

[[Entropy (Average Surprise)]] is one distribution's own expected surprise — the best achievable average code length, reached only when the model equals the data. [[Cross-Entropy from NLL]] is H(Q) + KL: the model's average surprise measured against the truth. KL is the *difference* between the two — the waste. Cross-entropy is what the training loop computes; KL is what that number is actually spending itself on. Feed KL a joint and the product of its marginals and it becomes [[Mutual Information]].

## Related

- [[Entropy (Average Surprise)]]
- [[Cross-Entropy from NLL]]
- [[Negative Log-Likelihood (NLL)]]
- [[Mutual Information]]
- [[Add-1 Smoothing]]
- [[Laplace Smoothing]]

## Sources

- https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence
