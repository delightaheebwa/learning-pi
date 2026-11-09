<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Variation of Information

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L09 + Olah (Visual Information Theory) + Meilă 2003 (COLT) / 2007 (*J. Multivariate Analysis*) · **Lang:** Python
> **Insight:** V(X,Y) = H(X|Y) + H(Y|X) — the two Olah wings: how many bits the two variables still *don't* tell each other. Zero when each determines the other, as large as H(X) + H(Y) when they are independent, and (unlike mutual information) a genuine metric.

## The defining idea

[[Mutual Information]] counts the **overlap** of the two bars. Variation of information counts everything the overlap is *not* — the two non-overlapping wings, the uncertainty of one variable that the other leaves standing:

**V(X,Y) = H(X|Y) + H(Y|X)**

Read it as a *dissimilarity*: X and Y are 0 bits apart when each is a function of the other, and maximally far apart when knowing one tells you nothing about the other. The learner's gloss for it: a **"secrecy level"** — what X and Y keep from each other (0 at perfect coupling, maximal at independence).

The same picture, three other ways. Since H(X,Y) = H(X|Y) + H(Y|X) + I(X;Y):

1. **Wings:** V(X,Y) = H(X|Y) + H(Y|X)
2. **Union minus overlap:** V(X,Y) = H(X,Y) − I(X;Y)
3. **Bars:** V(X,Y) = H(X) + H(Y) − 2·I(X;Y)
4. **Entropies only:** V(X,Y) = 2·H(X,Y) − H(X) − H(Y)

Form 1 is the picture, form 3 is the one to reach for when I(X;Y) is already known, form 4 needs no mutual information at all. The two measures partition the same bookkeeping:

**V + I = H(X,Y)**  ·  **V + 2I = H(X) + H(Y)**

Add the overlap once to the wings and you have the union; add it twice and you have the two bars. So everything on [[Mutual Information]] is already enough to get V — the same entropy-difference / bars / cell-by-cell ratio routes, combined with H(X) + H(Y) and H(X,Y).

## Range, and both extremes

**0 ≤ V(X,Y) ≤ H(X) + H(Y)**

- **V = 0 iff the two variables determine each other** (mutual determinism: H(X|Y) = 0 *and* H(Y|X) = 0). Y = X gives V = 0 — and so does the anti-correlated Y = 1 − X (both conditionals are 0 there too), so **V is blind to the sign** of the relationship; it measures how strongly the two are coupled, never in which direction.
- **V = H(X) + H(Y) iff X and Y are independent.** Then each conditional entropy equals the variable's own entropy (H(X|Y) = H(X), H(Y|X) = H(Y)): nothing is shared, so everything is "secret". Independence is the one point that is MI's minimum *and* V's maximum — so the classic distractor ("V = 0 bits when the variables are independent") is MI's zero read onto the wrong measure. Getting this backwards is a *maximum*-strength error, not a rounding slip.
- **Everything in between:** the running joint [[0.45, 0.05], [0.05, 0.45]] has I = 0.531 bits, so V = 1.469 − 0.531 = **0.938 bits** (= 0.469 + 0.469).

## Worked example — the fresh joint [[0.35, 0.15], [0.15, 0.35]] (2026-09-21)

Consolidated on the same joint that produced the lesson's first fresh MI computation.

| P(X,Y) | Y = 0 | Y = 1 | p(x) |
|---|---|---|---|
| **X = 0** | 0.35 | 0.15 | 0.5 |
| **X = 1** | 0.15 | 0.35 | 0.5 |
| **p(y)** | 0.5 | 0.5 | 1 |

Both marginals are a fair coin, so H(X) = H(Y) = 1 bit; the joint is

```
H(X,Y)  = −[2·0.35·log₂0.35 + 2·0.15·log₂0.15] ≈ 1.8813 bits
H(X|Y)  = column (0.7, 0.3) → 0.7·0.5146 + 0.3·1.7370 ≈ 0.8813 bits  (= H(Y|X))
I(X;Y)  = H(X) + H(Y) − H(X,Y) = 2 − 1.8813 = 0.1187 bits
```

All four V-forms on the same numbers:

```
wings:       0.8813 + 0.8813          = 1.7626 bits
union minus: 1.8813 − 0.1187          = 1.7626
bars:        1 + 1 − 2(0.1187)        = 1.7626
entropies:   2(1.8813) − 1 − 1        = 1.7626
```

Range check: 0 ≤ 1.7626 ≤ 2, comfortably inside. The two variables are 1.7626 bits "away" from being each other's function — most of the two bars' 2 bits of total uncertainty is still secret.

A second, marginal-only item from the same exit ticket: given H(X) + H(Y) = 3 bits and I(X;Y) = 0.8 bits, V = 3 − 2(0.8) = **1.4 bits** — form 3 earns its keep when only the marginals and the overlap are known.

## Why V is a metric — and MI is not

A metric needs (1) d(X,X) = 0 with d ≥ 0, (2) symmetry, (3) the triangle inequality.

- **Identity and non-negativity:** V = 0 exactly when each variable determines the other — the measure-zero analogue of d(X,Y) = 0 iff X = Y (variables that are bijections of one another are the same point of the space), and V ≥ 0 since each conditional entropy is.
- **Symmetry:** V(X,Y) = H(X|Y) + H(Y|X) is symmetric term by term even though neither conditional entropy is — the same repair of directionality that makes [[Mutual Information]] the one symmetric KL application.
- **Triangle inequality — Meilă's theorem.** Marina Meilă (*Comparing clusterings by the variation of information*, COLT 2003; *Comparing clusterings — an information based distance*, J. Multivariate Analysis 98 (2007) 873–895) proved VI is a **true metric** on the space of clusterings / partitions of a finite set. Writing V(X,Y) = H(X|Y) + H(Y|X) is literally Meilă's VI on the partitions that X's and Y's level sets induce (the block weights are the induced probabilities), so the theorem covers this two-variable reading as well, for discrete variables of finite support. Scope note: with *differential* entropies the conditional term can go negative, so the metric property is a finite/discrete statement, not a universal one.

**MI is the anti-distance.** MI(X,X) = H(X), not 0 — on a fair die, 2.585 bits. A variable shares *maximal* information with itself instead of being zero apart, so MI is a similarity measure that grows with closeness, and its ceiling is the "distance end".

**Why you cannot just flip MI.** The obvious candidates f(I) — −I, c − I, 1/(1 + I) — all die at **axiom 1**: d(X,X) = f(I(X,X)) = f(H(X)) would have to be 0 for *every* possible entropy value H(X) (a die's 2.585 bits, a coin's 1, a deterministic variable's 0), which forces f ≡ 0 and collapses the measure to the trivial one. They also fail the triangle inequality, but they never get that far.

**Why the geometric flip survives.** V(X,Y) is *not a function of I alone*. It is the **Venn complement of the overlap inside the union**, built jointly out of H(X), H(Y) and H(X,Y) — and that extra structure is exactly what cancels the dependence on the variable's own entropy:

```
V(X,X) = H(X) + H(X) − 2·I(X,X) = 2H(X) − 2H(X) = 0
```

for *every* H(X). The H(X) + H(Y) offsets cancel identically, so nothing has to be tuned to how uncertain the compared variable happens to be. This is the resolution of the apparent contradiction "MI's flip is VI, yet flips die at axiom 1": the arithmetic flips are pure functions of I; VI is a geometric rearrangement of the Venn diagram.

## What the metric property buys (why anyone reaches for it)

- **Free bounds through a reference point.** A metric gives the triangle inequality: with VI(A,B) = 0.8 bits and VI(B,C) = 0.6 bits, 0.2 ≤ VI(A,C) ≤ 1.4 without ever measuring A against C. That is what makes a *distance* composable and a *similarity* not.
- **Raw similarity is not transitive** — the 2026-09-21 counterexample: take independent fair binary X and Y, and let A = X, C = Y, B = (X,Y). Then I(A;B) = H(X) = 1 bit and I(B;C) = 1 bit, yet I(A;C) = 0 — A is as close to B as B is to C, while A and C share nothing, so "close" loops back on itself. The same three objects under VI: V(A,B) = 1, V(B,C) = 1, V(A,C) = 2, and 2 ≤ 1 + 1 holds *tight* — the triangle inequality satisfied with equality, exactly as a metric should.
- **Comparing clusterings** (Meilă's application). For two partitions of the same data, VI = 0 exactly when they agree up to relabelling; no label matching, no assumption about the number of clusters, and the unit is bits. That makes it usable for cluster-stability checks and for scoring a method's output against a reference partition — and the metric property means the numbers compose: a small VI to a reference keeps you inside a known ball of it.

## Nearest neighbour

[[Mutual Information]] is the overlap; variation of information is everything the overlap is not. Both come out of the same Olah picture, and only one of them is a metric. [[Entropy (Average Surprise)]] supplies the pieces (H(X), H(X|Y)), while [[KL Divergence]] and [[Cross-Entropy from NLL]] supply the identity H(X,Y) = H(X|Y) + H(Y|X) + I that V rearranges. Against [[Covariance and correlation]]: correlation is signed and linear; V is symmetric, non-negative, unit-free, blind to the sign of the relationship, and transitive by theorem.

## Open questions

- **Continuous variables.** Meilă's theorem is a finite-partition statement; with differential entropies H(X|Y) can be negative and V loses non-negativity. Open: which continuous analogue (a regularized/quantized VI, or a different divergence) is the standard replacement when clusterings are density-based rather than discrete.
- **Quotienting.** V = 0 identifies variables that are bijections of one another, so V is really a metric on the quotient of random variables by mutual determinism — worth naming explicitly when comparing variables on different alphabets (it is why VI can compare a clustering into 3 groups with one into 7).

## Retrieval log (2026-09-24)

Open of the lesson's final session — warm-up 2/2 (pass, sure, grade-audit agreed): the independence MCQ picked **H(X) + H(Y)** (dodging the MI-zero distractor — independence is MI's minimum *and* V's maximum), and the on-paper two-route computation gave V = H(X) + H(Y) − 2I = 1.2 + 0.9 − 1.0 = **1.1 bits**. V's row now returns 2026-10-24. The subtraction V = H(X,Y) − I(X,Y) sits directly on [[Mutual Information]] and, through it, on [[KL Divergence]].

## Source

Rohit P1 L09 `docs/en.md` (https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/09-information-theory/docs/en.md) + Olah, *Visual Information Theory* (https://colah.github.io/posts/2015-09-Visual-Information/) — the wings and the union/overlap picture; Meilă, *Comparing Clusterings by the Variation of Information* (COLT 2003) and *Comparing clusterings — an information based distance* (J. Multivariate Analysis 98 (2007) 873–895) — the metric theorem and the clustering application. Introduced in this track 2026-09-16 as a wonder-out; consolidated 2026-09-21 (idea + practice 2/2 + exit ticket 3/3, all under `sure`).

## Sources
- https://en.wikipedia.org/wiki/Variation_of_information
