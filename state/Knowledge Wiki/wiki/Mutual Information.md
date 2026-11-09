<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Mutual Information

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 + Olah (Visual Information Theory) · **Lang:** Python
> **Insight:** I(X;Y) is how many bits of X's uncertainty knowing Y removes — the information the two variables share. Symmetric, never negative, and exactly zero when they are independent.

## The defining idea

How much does knowing Y tell me about X? Start from X's own uncertainty H(X) ([[Entropy (Average Surprise)]]) and subtract what is still uncertain once Y is known — the conditional entropy H(X|Y):

**I(X;Y) = H(X) − H(X|Y)**

Mutual information is the *uncertainty deleted*, not "X is now certain": if H(X|Y) > 0 some doubt remains, and MI is only the amount that went away. Two extremes anchor it — if Y determines X perfectly then H(X|Y) = 0 and I(X;Y) = H(X) (all of X's uncertainty, no more); if Y tells you nothing about X then H(X|Y) = H(X) and I(X;Y) = 0.

## Four equivalent forms

1. **Deleted uncertainty:** I(X;Y) = H(X) − H(X|Y) = H(Y) − H(Y|X)
2. **Bars / set form (Olah):** I(X;Y) = H(X) + H(Y) − H(X,Y) — double-count the overlap, subtract the union once
3. **Surprise form:** I(X;Y) = Σ_x Σ_y p(x,y)·log₂( p(x,y) / (p(x)·p(y)) ) — how much more (or less) often the pair occurs than chance would predict
4. **KL form:** I(X;Y) = KL( p(x,y) ∥ p(x)·p(y) ) — the joint, measured against the independence baseline ([[KL Divergence]]). Both arguments are *distributions over the same cells* — the joint table and the product of its own marginals — not the variables X and Y; walked step by step in the next section.

Form 4 is the unification: mutual information *is* a KL divergence — the bits wasted by coding the pairs as though X and Y were independent. Form 1 is where the ≥ 0 and the symmetry are easiest to see, form 2 is the picture, form 3 is what you compute cell by cell.

## The KL connection, walked

Form 4 survives being built slowly, in four moves:

1. **Fix KL's roles first.** KL scores a *model* against a *truth*: the first argument supplies the weights (what actually happens), the second is the distribution being scored ([[KL Divergence]]). Whatever sits in position one is the truth; position two is the claim on trial.
2. **Build the independence baseline cell by cell.** "X and Y are unrelated" is not a vague statement — it is the specific distribution p_indep(x,y) = p(x)·p(y). For the running joint both marginals are 0.5, so the baseline is [[0.25, 0.25], [0.25, 0.25]]: every cell predicted from the marginals alone, all dependence erased.
3. **Name the identification.** I(X;Y) = KL( p(x,y) ∥ p(x)·p(y) ) — mutual information is KL divergence with the independence claim plugged in as the model. The joint is the truth; independence is the approximation being scored.
4. **Check it numerically.** Compare the joint against the baseline cell by cell:

```
diagonals:     0.45·log₂(0.45/0.25) = 0.45·log₂ 1.8 ≈ +0.3816 bits   (two cells)
off-diagonals: 0.05·log₂(0.05/0.25) = 0.05·log₂ 0.2 ≈ −0.1161 bits   (two cells)
total:         2(0.3816) + 2(−0.1161) ≈ 0.7632 − 0.2322 = 0.531 bits
```

— the same 0.531 bits the entropy route (H(X) − H(X|Y) = 1.000 − 0.469) and the bars route give. Three routes, one number.

Two things this walk pins down:

- **The arguments are distributions, not variables.** "The KL between X and Y" is not a thing — X and Y are random variables; p(x,y) and p(x)·p(y) are distributions over the same cells. Joint first (the truth, supplying the weights), product-of-marginals second (the independence model being scored). This wording is a retrieval item — and as of 2026-09-21 it has been **retrieved**: asked directly to fill I(X;Y) = KL( ___ ∥ ___ ), the learner wrote the variables "X (the truth) then Y" again (the truth slot in position one was right; the distributions were replaced by variables), repeating the 2026-09-16 exit-ticket slip — repaired under retrieval on 2026-09-21, when the same fill-in-the-blanks item came back as the joint distribution of X and Y ∥ the product of the marginals (tag `sure`, grade-audit agreed): the first successful recall after the two failures. The ledger row moves `active` → `review` (one consecutive correct); the second consecutive recall is due 2026-09-28.
- **"High relationship = high KL" is not a paradox.** KL measures distance from truth, and here the *independence claim* is the thing being measured — against the joint. So MI reads as "how many bits of truth the independence story fails to capture". The joint does not drift; the independence claim is scored against it.

## Properties

- **I(X;Y) ≥ 0** — read off form 4 with KL ≥ 0 (Gibbs' inequality); no separate proof is needed (see the next section — and the one-line Jensen proof of Gibbs' inequality on [[KL Divergence]]).
- **I(X;Y) = 0 iff X and Y are independent** — then p(x,y) = p(x)·p(y) for every cell, every log-ratio is 0, and the shared information is 0.
- **Symmetric: I(X;Y) = I(Y;X).** "How much Y tells me about X" is the same number as the reverse. This is exactly what [[KL Divergence]] does *not* do — here the arguments are the joint and the product of its marginals, and relabelling X ↔ Y relabels both together, so nothing changes.
- **I(X;X) = H(X)** — a variable tells you everything about itself (H(X) − H(X|X) = H(X) − 0). So MI is bounded above by the entropy of either variable.
- **I(X;Y) ≤ min(H(X), H(Y))** — a variable cannot carry more information about X than X itself contains (for two binary variables: at most 1 bit, reached exactly by a bijection such as Y = 1 − X).

## Why MI can never be negative — and why there is no absolute value

- **Anti-correlated is not punished.** Take X fair on {0,1} and Y = 1 − X. The joint is [[0, 0.5], [0.5, 0]] — no mass on the diagonal. H(X) = H(Y) = 1 bit and H(X,Y) = 1 bit, so I(X;Y) = 1 + 1 − 1 = **1 bit**, the maximum for two binary variables. Knowing Y determines X completely, so MI is maximal; and MI is direction-agnostic — it measures distance from chance, not the sign of co-movement.
- **Individual cell terms can be negative; the weighted total cannot.** In the walkthrough the off-diagonal cells each contribute ≈ −0.1161 bits, because there the pair is *less* likely than independence predicts. Terms are signed; the p-weighted sum is not (Gibbs' inequality / Jensen). The negative cells are the ones where the truth sits closer to the independence baseline than the baseline expects — averaged over what actually happens, the diagonal surpluses outweigh them.
- **There is no absolute value anywhere in the construction.** A mod sign around a log-ratio would be a different quantity, and nothing in the derivation produces it. MI is already non-negative by construction, so wrapping it in bars would change the number — and would break I(X;X) = H(X).
- **The coding reductio (why KL ≥ 0).** H(X) is the average length of the optimal code for X's own distribution; cross-entropy is what your code actually costs. If KL were negative, some code would be *shorter on average than the truth's own optimal code* — the model's code beating the best possible code for the data, "the model more true than the truth". That cannot happen — the formal version is Gibbs' inequality, proved in one line from the concavity of log by Jensen ([[KL Divergence]] carries the proof and the numerator reversal) — which is exactly why cross-entropy has a floor at H(data) and MI a floor at 0.

## The bars picture (Olah)

Draw a bar of length H(X) and a bar of length H(Y):

- the **overlap** is I(X;Y);
- the **union** is H(X,Y);
- the **non-overlapping parts** are H(X|Y) and H(Y|X).

H(X) + H(Y) counts the overlap twice (once inside each bar) and the rest once, while H(X,Y) counts every region once, so H(X) + H(Y) − H(X,Y) leaves a single copy of the overlap — form 2 is that bookkeeping. The picture also shows the bound: two bars can overlap by at most the shorter bar, i.e. ≤ min(H(X), H(Y)).

The fused-bar version is the same arithmetic rearranged. Writing the union as its three disjoint pieces gives the identity confirmed on 2026-09-16:

**H(X,Y) = H(X|Y) + H(Y|X) + I(X;Y)**   ⟺   **I(X;Y) = H(X,Y) − H(X|Y) − H(Y|X)**

and on the running joint 1.469 − 0.469 − 0.469 = 0.531 bits. One fused bar, subtract the two exclusive strips (the "A-only part" and the "B-only part"), and what remains is counted once — the same move as subtracting the union from the stacked bars.

The same picture yields **variation of information** — the two wings, i.e. everything the overlap is not:

V(X,Y) = H(X|Y) + H(Y|X) = H(X,Y) − I(X,Y)

It is 0 exactly when each variable determines the other (the bars coincide), and as large as H(X) + H(Y) when they are independent (no overlap at all). Consolidated on 2026-09-21, including the part MI cannot supply: V is a **true metric** (symmetry, identity, triangle inequality — Meilă 2003 COLT / 2007 *J. Multivariate Analysis*), while MI is an anti-distance (MI(X,X) = H(X) ≠ 0) and every *arithmetic* flip of it dies at axiom 1. Own page: [[Variation of Information]].

## Worked example — the joint [[0.45, 0.05], [0.05, 0.45]]

| P(X,Y) | Y = 0 | Y = 1 | p(x) |
|---|---|---|---|
| **X = 0** | 0.45 | 0.05 | 0.5 |
| **X = 1** | 0.05 | 0.45 | 0.5 |
| **p(y)** | 0.5 | 0.5 | 1 |

Marginals are the row and column sums → both a fair coin, so **H(X) = H(Y) = 1 bit**. Conditionals: given Y = 0 the column becomes (0.45, 0.05)/0.5 = (0.9, 0.1), entropy ≈ 0.137 + 0.332 = 0.469 bits; the Y = 1 column gives the same, and averaging over Y (0.5 each) gives **H(X|Y) = 0.469 bits**.

```
I(X;Y) = H(X) − H(X|Y) = 1.000 − 0.469 = 0.531 bits
```

The other forms agree:

```
bars:       H(X) + H(Y) − H(X,Y) = 1.000 + 1.000 − 1.469 = 0.531
            (H(X,Y) = −[2·0.45·log₂0.45 + 2·0.05·log₂0.05] ≈ 1.469 bits)
set strips: H(X,Y) − H(X|Y) − H(Y|X) = 1.469 − 0.469 − 0.469 = 0.531
surprise:   2·0.45·log₂(0.45/0.25) + 2·0.05·log₂(0.05/0.25) ≈ 0.763 − 0.232 = 0.531
KL:         KL(joint ∥ product of marginals) = 2(0.3816) + 2(−0.1161) = 0.531
```

Cell by cell, the surprise form reads the correlation straight off the table: the diagonal cells are 1.8× more likely than chance predicts (0.45 vs 0.25, ≈ +0.848 bits each) while the off-diagonal cells are 0.2× as likely (0.05 vs 0.25, ≈ −2.322 bits each); any cell whose ratio is exactly 1 contributes 0. Here V(X,Y) = 0.469 + 0.469 = 0.938 bits — the variables are 0.938 bits "away" from being each other's function.

Contrast with independence: the joint [[0.25, 0.25], [0.25, 0.25]] has the same marginals but every cell equals p(x)·p(y), so every log-ratio is 0 and I(X;Y) = 0. Same marginals, zero shared information — MI measures the *dependence*, not the marginals.

## Worked example — the fresh joint [[0.35, 0.15], [0.15, 0.35]] (2026-09-21)

The first I(X;Y) computed on a joint that was not already on this page — the 2026-09-21 CP5 practice item.

| P(X,Y) | Y = 0 | Y = 1 | p(x) |
|---|---|---|---|
| **X = 0** | 0.35 | 0.15 | 0.5 |
| **X = 1** | 0.15 | 0.35 | 0.5 |
| **p(y)** | 0.5 | 0.5 | 1 |

Marginals are a fair coin each, so H(X) = H(Y) = 1 bit, and H(X|Y) comes from the (0.7, 0.3) conditional column:

```
H(X,Y) = −[2·0.35·log₂0.35 + 2·0.15·log₂0.15] ≈ 1.8813 bits
H(X|Y) = 0.7·log₂0.7 + 0.3·log₂0.3 ≈ 0.8813 bits   (= H(Y|X))

entropy difference: I = H(X) + H(Y) − H(X,Y) = 2 − 1.8813 = 0.1187 bits
KL / ratio route:   diagonal 0.35/0.25 = 1.4 → 2(0.35·log₂1.4) ≈ +0.3398 (costs)
                    off-diagonal 0.15/0.25 = 0.6 → 2(0.15·log₂0.6) ≈ −0.2211 (rebates)
                    total ≈ +0.1187 bits
```

Both routes land on the same 0.1187 bits. On this joint V(X,Y) = 1.8813 − 0.1187 = 1.7626 bits ([[Variation of Information]]).

**The sign slip, and the theorem as an error detector.** The first answer was **−0.119 bits** (tag `sure`) — magnitude exactly right, sign impossible, because the arithmetic had been arranged as H(X,Y) − H(X) − H(Y) instead of H(X) + H(Y) − H(X,Y). I(X;Y) ≥ 0 (Gibbs' inequality, from form 4) says no mutual information can be negative: a negative MI should feel like a negative probability. The theorem was known in isolation — it had been exit-ticketed 3/3 on 2026-09-18 — but it was not *used* to reject the impossible number until the grade landed; corrected in the same session, and then reused as a detector on the exit ticket, where a reported I(X;Y) = −0.3 bits was rejected on nonnegativity alone. That is the practical payoff of a floor: **H(P,Q) ≥ H(Q), KL ≥ 0 and I ≥ 0 are free sanity checks on any computation in this family** (the cross-entropy page carries the detector note).

## MI vs correlation — the division of labor

| | [[Covariance and correlation]] | Mutual information |
|---|---|---|
| Sign | Signed — separates "rises together" from "moves oppositely" | Non-negative — direction-agnostic |
| Scale | Units and variances leak in; Pearson sees only *linear* alignment | Bits, unit-free; any dependence at all |
| Zero means | No *linear* relationship | *Statistical independence* |

They coexist because they answer different questions: correlation reports the *direction* of co-movement on a linear scale; MI reports *how much uncertainty* one variable removes about the other, in bits, whatever form the dependence takes. X uniform on {−1, 0, 1} with Y = X² has correlation 0 but I(X;Y) ≈ 0.918 bits — neither number is wrong; they are measuring different things.

## Where it is used

- **Feature selection:** rank features by I(feature; label) — it catches any dependence, including non-linear ones that correlation misses. Example: X uniform on {−1, 0, 1}, Y = X². Covariance(X,Y) = 0, yet Y is a deterministic function of X, so H(Y|X) = 0 and I(X;Y) = H(Y) ≈ 0.918 bits. Correlation says "unrelated"; MI says "0.92 bits of relationship".
- **Decision trees:** a split is chosen to minimise the remaining uncertainty of the label, H(Y|X) — which is exactly maximising I(X;Y) for the chosen feature. A tree's "information gain" *is* mutual information.
- **Redundancy / independence checks:** I(X;Y) ≈ 0 means Y carries nothing about X; I(X;Y) = H(X) means X is a deterministic function of Y (a redundant feature if X is an input and Y another input).

## Nearest neighbour

[[Entropy (Average Surprise)]] is one distribution's own uncertainty; [[Cross-Entropy from NLL]] scores a model against the truth; [[KL Divergence]] is the directed excess of one distribution over another. Mutual information is a KL too, but between a *joint* and the *product of its own marginals* — which is why it is symmetric, non-negative, and 0 only at independence. Against [[Covariance and correlation]]: correlation only sees linear alignment, MI sees any dependence at all.

## Related

- [[Entropy (Average Surprise)]]
- [[KL Divergence]]
- [[Variation of Information]]
- [[Cross-Entropy from NLL]]
- [[Information Content (Surprise)]]
- [[Joint, marginal, and conditional probabilities]]
- [[Independence of random variables]]

## Open questions

- **Variation of information — CLOSED 2026-09-21.** Introduced 2026-09-16 as a wonder-out, consolidated 2026-09-21: a perfect bijection gives V = 0 while I = H(X) = H(Y), and on the running joint V = 1.469 − 0.531 = 0.938 bits (= H(X|Y) + H(Y|X)). Answered: V = H(X|Y) + H(Y|X) = H(X,Y) − I = H(X) + H(Y) − 2I, with 0 ≤ V ≤ H(X) + H(Y), V = 0 at mutual determinism (so V is blind to the *sign* of the relationship — Y = 1 − X gives 0 as well) and V = H(X) + H(Y) at independence; VI is a true metric (Meilă 2003/2007 — triangle inequality, used to compare clusterings) while MI is not (MI(X,X) = H(X)); the arithmetic flips f(I) die at axiom 1 because d(X,X) = f(H(X)) cannot vanish for every entropy, whereas the geometric Venn-complement flip works because its H(X) + H(Y) offsets cancel identically. Reached for when a *distance* between two variables or two clusterings is wanted (cluster comparison, stability, bounds through a reference), not a similarity. Exit ticket 3/3 under `sure`; own page [[Variation of Information]].
- **Nonnegativity — closed 2026-09-18:** Gibbs' inequality stated formally (Σ_i Q_i·log₂(Q_i/P_i) ≥ 0, equality iff P = Q) and its one-line Jensen proof walked, including the deliberate numerator reversal (only P/Q collapses: Σ_i Q_i·(P_i/Q_i) = Σ_i P_i = 1; the KL direction gives Σ_i Q_i²/P_i ≈ 2.778, no collapse) and the Jensen-vs-Gibbs division of labour. Exit ticket 3/3 under `sure` (theorem MCQ, collapse-mechanism MCQ, rebate/cost free recall), so "MI inherits KL ≥ 0" now rests on a proved theorem rather than only on form 4's shape. Still open on this page's account: the fresh I(X;Y) computation on a **new** joint was done on 2026-09-21 — 0.1187 bits via two routes on [[0.35, 0.15], [0.15, 0.35]], with the first attempt's −0.119 rejected by this very theorem.
- **Maximum possible overlap of two binary bars:** ≤ min(H(X), H(Y)) = 1 bit, and the bound is *achieved* — Y = X and Y = 1 − X both give I = 1 bit. Planted 2026-09-15, closed by the anti-correlation case on 2026-09-16; the bound itself is general (I ≤ min(H(X), H(Y)) for any pair).

## Retrieval log (2026-09-24)

Final cumulative quiz of P1 L09, Q3: the KL form (joint ∥ product of the marginals) was retrieved **cold** — first try, under retrieval, not merely after the in-session repair pass — so the 2026-09-16 / 2026-09-18 variables-vs-distributions slip now holds across two later sessions. The 2026-09-21 sign/ordering slip (application) has the MI ≥ 0 detector behind it, rehearsed live on the exit ticket. This is the same KL quantity the new [[Perplexity]] and [[Label Smoothing]] pages orbit — dependence, not calibration.

## Source

Rohit P1 L09 `docs/en.md` (https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/09-information-theory/docs/en.md) + Olah, *Visual Information Theory* (https://colah.github.io/posts/2015-09-Visual-Information/) — the four forms, the bars picture and the variation of information follow Olah; Rohit supplies the ML framing and the feature-selection/decision-tree uses.

- Wikipedia — Mutual information: https://en.wikipedia.org/wiki/Mutual_information
- Meilă, M. (2007). Comparing clusterings—an information based distance. *Journal of Multivariate Analysis*, 98(5), 873–895: https://doi.org/10.1016/j.jmva.2006.11.013
