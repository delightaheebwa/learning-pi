<!-- provenance: status=verified | source=Knowledge Wiki/raw/sources/2026-09-25 - dimensionality-reduction - rohit.md (Rohit P1 L10) + Wattenberg, Viégas & Johnson, *How to Use t-SNE Effectively* (Distill 2016) + van der Maaten & Hinton 2008 (JMLR) | verified-by=fact-check-agent | date=2026-10-26 | learner-note block: the "## My understanding" section is the learner's verbatim note (learner-note; thirteen statements as of 2026-10-12) -->

# t-SNE (Dimensionality Reduction)

> **Type:** concept · **Track:** AIEFS · **Source:** Rohit P1 L10 (Dimensionality Reduction) + Wattenberg, Viégas & Johnson, *How to Use t-SNE Effectively*, Distill 2016 + van der Maaten & Hinton 2008, *Visualizing Data using t-SNE* (JMLR 9) · **Lang:** Python (`sklearn.manifold.TSNE`)
> **Insight:** t-SNE maps high-dimensional data into 2D/3D by **preserving which points are near each other** — it builds a probability distribution over point *pairs* (near = high, far = low) and searches for an arrangement whose pair distribution matches it.
> Related: [[PCA (Dimensionality Reduction)]], [[Curse of Dimensionality]], [[Perplexity]], [[KL Divergence]], [[Covariance and correlation]]

## The goal, in the source's words

Rohit, Phase 1 L10: t-SNE "maps high-dimensional data to 2D (or 3D) while preserving which points are near each other." The pitch is explicitly about **neighbourhoods, not distances**: "Points that were neighbors in 784 dimensions stay neighbors in 2D."

Two properties the lesson source states outright:

- **Non-linear.** It "can unfold complex manifolds that PCA cannot." Standard PCA finds linear subspaces — rotate the coordinate system, drop axes — so a curved manifold (a rolled sheet, the classic Swiss roll) has no single linear cut that exposes its structure.
- **For visualization, not preprocessing.** The source's comparison table files t-SNE under "publication-quality 2D plots / local neighborhoods", and its glossary line is "Good for visualization, not for preprocessing."

## The mechanism — and whose mechanism it is

**The pair-probability mechanism is Rohit's, not Distill's.** The construction, as the lesson source gives it: "in the original space, compute a probability distribution over pairs of points based on their distances. Near points get high probability. Far points get low probability. Then find a 2D arrangement where the same probability distribution holds."

So the algorithm has two halves: (1) a high-dimensional pair distribution `P` built from distances, with neighbours carrying high mass; (2) a low-dimensional pair distribution `Q` over the 2D coordinates, plus a search for the coordinates that make `Q` look like `P`. The name expands to *t-Distributed Stochastic Neighbor Embedding*; the details of the low-dimensional kernel and of the objective that scores the `P`-vs-`Q` match are the later CP4 minis (they connect to [[KL Divergence]]), not this page.

**Attribution note (2026-10-08).** An earlier draft of this track credited the probability framing to Distill. That was wrong: the framing above is already in Rohit's lesson text. Distill's distinctive contribution is the **interpretation-caution layer** documented in its own section below.

## Why a linear squash invents false neighbours (CP4 mini 1, 2026-10-08)

The failure mode that motivates a non-linear method, as derived in this track:

- A linear projection can only **shrink or preserve** pairwise distances; it can never enlarge them.
- So a straight squash of a curved manifold never **tears true neighbours apart** — the sheet's local pairs stay close in the shadow.
- But it does **collapse distinct regions onto each other**: the two layers of a rolled sheet land on top of one another, so points that were far apart in the original space become apparent neighbours. These are **false neighbours**.
- The learner's own phrasing: "non-neighbors can become neighbors in the flatten and i guess that doesnt work for the vice versa case." The flattened picture is a **smeared shadow** of the sheet, not the unrolled sheet.

That asymmetry — never tear, but often merge — is the precise sense in which PCA "cannot" show a manifold's structure, and it is the property t-SNE's pair-distribution match is built to defend.

## The interpretation-caution layer (Distill 2016)

Distill's essay is a catalogue of ways to misread a t-SNE picture. The headline cautions:

- **Cluster sizes mean nothing.** t-SNE "naturally expands dense clusters, and contracts sparse ones, evening out cluster sizes" — density equalisation is **by design**, not an ordinary distance distortion. Two Gaussians, one 10× more dispersed than the other, come out looking about the same size.
- **Distances between clusters may mean anything or nothing.** "The basic message is that distances between well-separated clusters in a t-SNE plot may mean nothing." Global geometry comes through only at the right perplexity, and the right value is data-dependent: in the essay's three-Gaussian example, perplexity 50 read the geometry well, lower values made the clusters look equidistant, and with 200 points per cluster *none* of the trial perplexities recovered it.
- **Random noise looks structured at low perplexity.** On 500 points drawn from a unit Gaussian in 100 dimensions, the perplexity-2 plot "seems to show dramatic clusters" — pure artifact. The same example doubles as a win: the perplexity-30 plot's oddly even density is a truthful statement about high-dimensional Gaussians, more accurate than a linear projection could be.
- **Stopping early invents shapes.** Non-converged runs give "seemingly 1-dimensional and even pointlike images" of the clusters; "if you see a t-SNE plot with strange 'pinched' shapes, chances are the process was stopped too early." Runs may also differ wildly — in the trefoil-knot example, three of five perplexity-2 runs introduced artificial breaks, while five perplexity-50 runs were visually identical up to symmetry. Stochasticity is a reading hazard, not just a nuisance.
- **Density equalisation distorts shape subtly even when it works.** Long parallel clusters come out slightly bowed outward, because the middles are denser and get magnified relative to the ends; contained clusters are exaggerated in size.
- **For topology, use several plots.** Low and high perplexity can tell different stories about containment or connectedness, and the essay's own recommendation is to analyse multiple perplexities.

## The misreading protocol (CP4 mini 4, 2026-10-10)

Distill's two headline cautions, taught and sealed at CP4 mini 4. Both are about *quantities read off the layout* — the sibling of CP4 mini 1's caution, which was about *pairwise relationships being spoofed*.

**1. Cluster sizes are meaningless.** The apparent size of a cluster is nothing but the **spread of the 2-D coordinates the optimizer produced** inside it. There is no route by which the knob could manufacture a size difference: one plot carries **one** user-set [[Perplexity]] target (only each point's `σ_i` adapts, per mini 2), so every point in every cluster is chased toward the same *effective* neighbour count. Consequences: sizes shift with perplexity and can shift across re-runs (the optimizer is stochastic); pure noise at low perplexity still shows dramatic clumps. Distill's misreading #1: **never read group size off the plot** — check the raw data's counts.

**2. Cluster distances mean little at an untuned perplexity.** The [[KL Divergence|KL cost]] pins *neighbourhoods* — the pairs that carry real `P` weight — and leaves the rest to the optimizer. Pairs from different clusters carry `P_{ij} ≈ 0` at low perplexity, so their fine is ≈ 0 under *any* separation: the objective is indifferent to where whole clusters sit relative to one another. The visible gap is therefore dictated by the optimizer's arrangement (initialization, the other fines, the knob acting through `σ_i`), not by the data — and the objective guarantees **no direction**: the clusters are free to rearrange either way. Low-perplexity runs render clusters almost equidistant for exactly this reason.

**The fragile exception.** Tuning perplexity to the data's **natural cluster structure** gives cross-cluster pairs small-but-real `P` weights, and inter-cluster distances become *somewhat* meaningful. Fragile on two counts: heterogeneous cluster densities may admit no single valid perplexity, and even then no directional bet is guaranteed.

## ⚠️ Sources disagree on cluster distances — resolved at CP4 mini 4 (2026-10-10)

- **Rohit (unconditional):** "Distances between clusters in the output are not meaningful. Only the clusters themselves are."
- **Distill (conditional):** distances between well-separated clusters "may mean nothing" — *at arbitrary perplexity*. In their three-Gaussian example, perplexity 50 did give a good sense of the global geometry; low perplexity flattened the clusters to looking equidistant.

**Resolution carried in this track:** Rohit's blanket rule is the **safe default**; Distill's "distances can be read if the perplexity is tuned" is the **fragile exception**. Both hold at their own scope — the unconditional claim is what to believe unless you have deliberately tuned perplexity and verified the picture is stable on your own data. **Resolved as taught (CP4 mini 4, 2026-10-10):** the two sources are not contradicting each other about the same quantity — Rohit speaks about the *default, untuned* picture, Distill about a *verified, tuned* one. So: **Rohit's blanket rule is the safe default rule; Distill's conditional is the fragile exception that only a deliberate tuning experiment on your own data can establish.** The ⚠️ stays on the page as the record of the split (nothing is smoothed away), but it is **closed**, not live.

## Perplexity = `2^H` on one point's neighbour distribution (CP4 mini 2, 2026-10-09)

Both sources describe perplexity as the neighbour-count knob. Rohit: it "controls how many neighbors to consider (typical range: 5-50)" and "Controls the **effective** number of neighbors each point considers". Distill calls it "a guess about the number of close neighbors each point has", quotes the original paper's 5–50, then adds two refinements: the effect "is more nuanced than that" — "getting the most from t-SNE may mean analyzing multiple plots with different perplexities" — and it must stay **smaller than the number of points**.

**The name collision resolves into a reuse.** t-SNE's perplexity is the *same* `2^H` banked in [[Perplexity]], now applied not to a model's token distribution but to **one point's neighbour distribution** `P_i`:

$$\mathrm{Per}(P_i) = 2^{H(P_i)}, \qquad H(P_i) = -\sum_j p_{j|i}\log_2 p_{j|i}$$

- Each point carries its own bandwidth `σ_i`; the algorithm tunes `σ_i` (a binary search in the original paper) until `Per(P_i)` equals the knob. The knob therefore rescales every point's neighbourhood to the same *effective* width.
- **Effective, not exact.** It is a soft count — a distribution can have perplexity 23.7 — not a hard cutoff at *k* neighbours.
- **What the knob buys:** low perplexity ⇒ very local attention; high ⇒ broader patterns. Distill frames the same dial as balancing attention between local and global structure.
- **Ceiling.** `P_i` lives on the other `n−1` points, and the most spread-out it can be is uniform: `H = log₂(n−1)`, so `Per ≤ n−1`. On 20 points the ceiling is 19, which makes a knob of 30 an **unreachable target**. That is the precise mechanism behind Distill's "smaller than the number of points" guardrail.

The difference from [[Perplexity]]'s uniform yardstick: there the uniform is hypothetical (a non-uniform model never realizes it); here it is *reachable* — a large enough `σ_i` flattens `P_i` toward uniform over the neighbours.

## The objective: minimize KL(P‖Q) (CP4 mini 3, 2026-10-09)

Rohit's recipe ends with "find a 2D arrangement where the same probability distribution holds"; the quantity being driven down is the mismatch between the high-dimensional pair distribution `P` and the 2D pair distribution `Q`, scored by [[KL Divergence]]:

$$\min_{\{y_i\}}\ \mathrm{KL}(P \| Q) = \sum_{i}\sum_{j} P_{ij} \log \frac{P_{ij}}{Q_{ij}}$$

Three load-bearing facts:

- **Minimize, never zero.** A 2D map cannot honour every neighbourhood, so some deviation always survives; `KL = 0` is unattainable on real data.
- **`P` is frozen — it *is* the data.** The only thing that moves is `Q`, through gradient descent on the 2D coordinates `{y_i}`.
- **The asymmetry is the point.** The weights in the sum come from `P`, so the expensive mismatch is "data says near, map says far" — a pair that carries high weight in `P` but low probability under `Q`. The reverse ("data says far, map says near") is comparatively cheap because its `P`-weight is small.

The learner's own statement of the weight direction — "the distribution of the actual data supplies the weights" — is exactly this, and it is the check-back that sealed the mini.

## Why the low-dimensional kernel is a heavy-tailed Student-t (CP4 mini 3b, 2026-10-09)

Squeezing 10-D (or 784-D) into a plane crowds the *moderately* related pairs — the medium-distance band has more pairs to place than the plane has room for. Whether those pairs can be pushed apart cheaply is decided by the shape of `Q`'s kernel:

- **Gaussian `Q` (plain SNE):** `Q_{ij}` collapses toward 0 at distance, so `log(P_{ij}/Q_{ij})` blows up for every pair the map tries to separate — each escape is fined, and the crowded medium-distance pairs stay crowded.
- **Student-t `Q` (t-SNE's change):** the fat tail keeps `Q_{ij}` from collapsing, so the `P`-weighted log-ratio for a moderately related pair stays affordable: spreading the crowded band is cheap, while pairs with genuinely large `P_{ij}` still pay to be separated. Local structure is preserved and the crowding is relieved.

van der Maaten & Hinton's stated reason (JMLR 2008): "the use of a Student-t distribution … allows … **mismatched tails [to] compensate for mismatched dimensionalities**." The tail is chosen to suit embedding a high-dimensional volume in a plane, not for convenience.

*Cost is a log-ratio, not a product.* The cost of placing a pair far apart is `P_{ij}\log(P_{ij}/Q_{ij})` — a `P`-weighted **log-ratio** — not the product `P \times Q`. (Recorded slip of 2026-10-09: the conclusion was reached with the product reading as the reason; repaired in-session, and kept verbatim under `## My understanding` below.)

**Learner-computed worked example (3b re-walk, 2026-10-10).** The re-walk took one pair at a time: `P_{ij}` frozen from the data, `Q_{ij}` the steerable number, the fine `P_{ij} log(P_{ij}/Q_{ij})`. Agreement ⇒ `log(1) = 0`; a moderate disagreement (0.05 vs 0.001 ⇒ ratio 50 ⇒ `ln 50 ≈ 3.9`) ⇒ cost ≈ 0.05 × 3.9 ≈ 0.2 nats. The learner then computed the mismatch case himself: **P = 0.2, Q = 0.001 → `0.2 × log₂ 200 ≈ 0.2 × 7.64 ≈ 1.53 bits`** (his own log₂ route; the natural-log route gives ≈ 1.06 — a base-unit convention difference, not an error). The log-ratio mechanism now has a learner-owned number, and the 2026-10-09 pacing request that produced it is closed.

## Where the two kernels come from (kernel deep-dive, 2026-10-12)

The two sides of t-SNE are two shapes doing **two different jobs under one shared idea**: turn a *distance* into a *probability of being neighbours*. The idea is shared in the source's framing ("Near points get high probability. Far points get low probability"); the shapes are chosen separately, and **neither is forced** by the other.

| side | what it is | why that shape |
|---|---|---|
| **data side — `P`** | **Gaussian bells**, one per point, each with its own bandwidth `σ_i` | a bell makes "near ⇒ high probability" explicit and *tunable per point*: `σ_i` is binary-searched until `Per(P_i)` hits the user's knob (mini 2) |
| **map side — `Q`** | **Student-t** with one degree of freedom: `q_{ij} ∝ 1/(1 + d_{ij}²)`, normalised | a 2-D **Gaussian `Q` collapses `Q_{ij} → 0` at distance** and strangles the crowded band's escapes (mini 3b); the `1/(1+d²)` polynomial tail keeps `Q_{ij}` alive |

**The `σ_i` binary search, re-anchored.** One user-set target, per-point bell widths: a **dense** neighbourhood already has many companions, so the bell that realises the target is *narrow*; a **sparse** neighbourhood needs a *wider* bell to reach the same effective count. The sweep runs until each point's `Per(P_i) = 2^{H(P_i)}` equals the knob — the point-wise version of the mini-2 rule.

## The two tails: a widening gap, no "flip point" (2026-10-12)

Asked where the Gaussian and the Student-t hand over to each other, the answer taught and sealed is: **nowhere**.

- Near `d ≈ 0` the two curves are **twins** — both sit at their maximum and fall away with a quadratic drop (`exp(−d²/2σ²)` vs `1/(1+d²)`).
- The gap then **opens gradually and keeps widening**: the Gaussian dies **exponentially**, the Student-t decays only like **`1/d²`**.
- So the distance axis is not split half-and-half into "Gaussian territory" and "`t` territory" — the *ratio* between them grows monotonically toward "the Gaussian is dead, the `t` is not".

That is the mechanical content behind "the fat tail keeps `Q` up": at the distances where the crowd sits, a Gaussian `Q` is already ≈ 0 while the Student-t still assigns real probability.

## Why the crowd sits in the tail region — by construction (2026-10-12)

The chain, in order (every step is a fact banked earlier in this lesson):

1. **`P` is sharply peaked.** A point's `P_i` carries real weight on roughly *perplexity* pairs and ≈ 0 everywhere else (mini 2).
2. **Close range is scarce, and the big-`P` pairs claim it first.** A 2-D plane holds only so many near-neighbours, and the [[KL Divergence|KL]] asymmetry makes "data says near, map says far" the expensive mismatch — so the pairs carrying real `P` weight win the close positions.
3. **The mid-range crowd has nowhere else to go.** In high dimensions everything sits at middling distance (the [[Curse of Dimensionality|distance-concentration]] anchor from CP3), so there are far more *moderately* related pairs than there are close slots.
4. **They land exactly where the Gaussian `Q` is dead and the `t` is alive.** Pushed outward by the crowding, they occupy the band the Student-t keeps affordable.

So "the crowd sits in the tail region" is not an observation about real data — it is what the objective produces **by construction**, which is why the heavy tail (mini 3b) is the mechanism of relief rather than decoration.

## CP4 fully sealed (2026-10-12)

- **CP4 practice — one graded MCQ batch on the whole t-SNE chain: 4/4, all `sure`.** The knob 40 against a 24-point ceiling (`H = log₂24 ≈ 4.58` bits, so `σ_i` saturates and the target is unreachable); the big-`P`-tiny-`Q` pair as the *data-near / map-far* mismatch that actually costs; the Gaussian tail decaying too fast to keep the mid-range `Q` affordable; and no single valid global perplexity under heterogeneous densities.
- **Pause exit ticket: 3/3, all `sure`.** Gaussian on the data side / Student-t on the map side; close range claimed first so the crowd takes the leftover room; and bells that stop short ⇒ `P_{ij} ≈ 0` ⇒ nothing pins the inter-cluster gaps.

## Other flags from the source

- **Stochastic:** "Different runs produce different layouts."
- **Slow:** `O(n²)` pairwise by default; the source's table says "Slow (< 10k samples ideal)".
- **UMAP has the analogous knob:** `n_neighbors`, "similar to perplexity" — CP5.

## Open questions

- ~~Perplexity as `2^H` on the neighbour distribution~~ — **closed 2026-10-09 (CP4 mini 2)**: the same `2^H`, applied per point, with a ceiling of `n−1`.
- ~~The objective: how the mismatch between `P` and `Q` is scored, which direction the divergence runs, and why that asymmetry matters~~ — **closed 2026-10-09 (CP4 mini 3/3b)**: `min KL(P‖Q)`, `P` frozen, weights from `P`; the Student-t tail is what makes escaping the crowded band affordable.
- ~~The Rohit-vs-Distill contradiction~~ — **closed 2026-10-10 (CP4 mini 4)**: Rohit's blanket rule is the safe default; Distill's conditional is the fragile exception that only a deliberate tuning experiment on your own data can establish.
- **How much of the t-SNE fix is the objective and how much is redefining "neighbourhood" locally?** Raised on [[Curse of Dimensionality]] and still open; CP4–CP5.
- ~~The CP4 practice~~ — **closed 2026-10-12 (CP4 fully sealed)**: the graded MCQ batch passed **4/4** and the pause exit ticket passed **3/3**, every item `sure`, 0 hints (details in the section above).
- ~~Where the two kernels come from, how their tails compare, and where the crowding pushes the map's points~~ — **closed 2026-10-12 (kernel deep-dive)**: Gaussian bells with a per-point `σ_i` on the data side, `q_{ij} ∝ 1/(1+d²)` on the map side, the widening gap with no flip point, and the crowd-placement chain.
- **Still to come in this lesson:** UMAP's `n_neighbors` / `min_dist` dials (CP5), kernel PCA (CP6), the final cumulative quiz + Feynman explain-back. **The Scout digest for this lesson is 17 days old (past its 7-day TTL) — re-scout before CP5** (the UMAP source bodies are still unconsumed).

## Sources

- van der Maaten & Hinton, *Visualizing Data using t-SNE*, JMLR 2008: https://www.jmlr.org/papers/v9/vandermaaten08a.html
- Wattenberg, Viégas & Johnson, *How to Use t-SNE Effectively*, Distill 2016: https://distill.pub/2016/misread-tsne/
- scikit-learn — `TSNE`: https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html

## My understanding

> **status=learner-note** — the learner's words, verbatim from the 2026-10-09 session (CP4 minis 2, 3, 3b), never rewritten. The annotations around them are the source's and the tutor's.

**Perplexity — what the knob controls (mini 2):**

> "i think it will control how many true neighbors each point will keep."

**Perplexity — the ceiling check-back (20-point dataset, knob at 30):**

> "now attention has to be made on effectively 30 points yet there are 20 and i think attention on some points that dont even exist will confuse the model."

**The objective — what training is aiming at (mini 3):**

> "it is trying to bring the kl divergence to zero since bringing it to zero would mean there is no deviation between the two distributions"

*Missing piece (annotated, not rewritten):* the target is **minimize**, not zero. `KL = 0` is unattainable — a 2D map cannot honour every neighbourhood — so training drives the deviation as low as it can go, short of zero.

**The objective — which distribution supplies the weights (check-back):**

> "the distribution of the actual data supplies the weights. the mismatch that gets a big penalty is a high supplied weight(the data says a point is near) but the 2D map says the point is far(small probability)"

**Heavy tails — why spreading the crowded band is affordable (mini 3b) — flagged: right conclusion, flipped reason:**

> "I think it is cheap for the map to place moderately related pairs far apart. It is cheap because, if they are far away, we are multiplying the moderate weight by a low probability; hence, it is cheap to do so. Based on that, the map will then spread out the crowded medium-distance pairs."

*Repair note (2026-10-09, in-session):* the conclusion — spreading the moderately related pairs is cheap, and the map does spread them — is correct; the **reason** was flipped. The cost is `P_{ij}\log(P_{ij}/Q_{ij})`, a `P`-weighted **log-ratio**, not the product of the weight and a probability. Under a Gaussian `Q` that log-ratio blows up as `Q_{ij} → 0`; the Student-t fat tail keeps `Q_{ij}` up, which is what makes the escape cheap. The learner's own words are preserved above unchanged.

**Cluster sizes — where the apparent size comes from (mini 4, atom 1, 2026-10-10):**

> "the user owns the target. the knob is really about per point."

> "the 2d coordinates the otpimizer produced in cluster A are further apart than those in cluster B"

**Cluster distances — what the inter-cluster gap tracks (mini 4, atom 2, 2026-10-10):**

> "reading off those distances isnt about the data but about perplexity knob applied to the 2d neighbors the opimizer happended to arrange"

> "i think whats left is perplexity so i think its free to rearrange either way the knob moves. the objective doesnt guarantee the direction of motion"

**The heavy-tail cost, computed by the learner (3b re-walk, 2026-10-10):**

> "the fine is approx 1.529"

**Source framing:** the learner chose the log₂ route himself — `0.2 × log₂ 200 ≈ 0.2 × 7.64 ≈ 1.53` bits; the natural-log route for the same pair gives `0.2 × ln 200 ≈ 1.06` (nats). The difference is the base-unit convention (see [[Bits vs Nats]]), not a disagreement about the fine.

**Missing piece (annotated, not rewritten):** the ownership sentence is exact, and the sentence that follows it in the same atom is where the size question is actually settled — because one plot carries *one* user-set target, the knob cannot make a cluster bigger, so the size comes from the map-internal spread of the 2-D coordinates. The distance statement also carries a scope: "not about the data" is the *default untuned* reading; a perplexity deliberately tuned to the data's natural cluster structure makes inter-cluster distances *somewhat* meaningful (see the ⚠️ section above).

**The fine, the weights, and the misreading frame (CP4 practice + exit ticket, 2026-10-12):**

> "P_ij is the probability provided by the data and Q_ij is the probability provided by the model"

> "it weighs the punishment by the data"

> "for an arbitrary perplexity, distances mean little since there is a negligible fine and optimizer's 2d arrangement can make some clusters have more points which are closer toghether than others hence some may be smaller than others"

**Source framing:** the first two statements are the mini-3 split — a *data*-side `P` and a *model*-side `Q` — and the mini-3 asymmetry, where the weights in `Σ P_{ij} log(P_{ij}/Q_{ij})` come from the data. The sharpened phrasing from the same session's check-and-extend: **the fine only speaks for pairs that carry `P` weight; anything read across weightless territory is the optimizer's arrangement.**

*Missing piece (annotated, not rewritten):* "it weighs the punishment by the data" names the *source* of the weight but not its form — the weight multiplies a **log-ratio**, not a probability (the 2026-10-09 slip, repaired above). The third statement's "negligible fine" is the cross-cluster `P_{ij} ≈ 0` of mini 4, and its scope is an *arbitrary (untuned)* perplexity: a perplexity deliberately tuned to the data's natural cluster structure makes inter-cluster distances *somewhat* meaningful (see the ⚠️ section above).

## Field notes

- "non-neighbors can become neighbors in the flatten and i guess that doesnt work for the vice versa case" — the CP4 mini 1 elicitation landing, in the learner's own words.
- "flat 2D plane; neighbors stay neighbors" — the first prediction (right about the flatten, wrong about the neighbours), which set up the two guiding questions.
- Check-back confirmed the "why now": PCA's squash blurs the neighbourhood pattern; t-SNE's job is defending it, with failure modes of its own to be named before trusting any picture.
- **2026-10-09 pacing call:** the learner flagged the KL/heavy-tail chain (mini 3b) as loaded — "i feel we should unpack more… we should slow down there before moving ahead" — and asked to pause; mini 4 was deferred at his request and the heavy-tail cost picture is to be re-offered when it next comes up.
- **CP4 mini 4 (2026-10-10), cluster sizes:** elicitation "each cluster has its own perplexity knob… tuning perplexity would increase the cluster sizes" (knob instinct right, ownership muddled) → guiding question 1 (who owns the target; the mini-2 anchor: per-point `σ_i` binary-searched toward ONE user-set target) → "the user owns the target. the knob is really about per point." ✓ → his first state attempt ("each point in cluster A has higher perplexity than each point in cluster B") contradicted that ownership → guiding question 2 (one plot ⇒ one target, so where does the size come from?) → the 2-D coordinate spread, in his own words.
- **CP4 mini 4 (2026-10-10), cluster distances:** elicitation "tracking the KL objective" plus a directional bet that the gap grows with perplexity → guiding question 1 (the weightless pair: far-apart-in-data pairs get `P_ij ≈ 0`, so their fine is ≈ 0 under any separation) → "near zero, low fine" ✓ → guiding question 2 (what is left dictating the gap?) → "free to rearrange either way… the objective doesnt guarantee the direction of motion" ✓. The State-rung rounds were ungraded; the only graded items today were the warm-up batch and the re-walk micro-check, both with 0 hints.
- **2026-10-10 pacing closure:** the 2026-10-09 heavy-tail request was honored — the pair-level re-walk plus the learner's own computed fine (≈1.53 bits). No new pacing requests, and no `just_tell_me` / declined-generation events this session.
- **CP4 practice (2026-10-12; quiz-audit PASS, grade-audit agreed 4/4, all `sure`, 0 hints):** P1 ✓ the knob 40 vs the 24-point ceiling (`H = log₂24 ≈ 4.58` bits, `σ_i` saturates); P2 ✓ big `P` / tiny `Q` = data-near / map-far, the `P`-weighted mismatch; P3 ✓ the Gaussian tail decays too fast, the `t` keeps mid-range `Q` affordable; P4 ✓ no single valid global perplexity under heterogeneous densities (verify by tuning runs). One batch, two `Attempts.json` rows (`transfer-near` + `explain-back`); mastery 1.00.
- **Pause exit ticket (2026-10-12; grade-audit agreed 3/3, all `sure`, 0 hints):** X1 ✓ Gaussian data side / Student-t map side; X2 ✓ close range claimed first, the crowd pushed into the leftover room; X3 ✓ bells stopping short ⇒ `P_ij ≈ 0` ⇒ nothing pins the gaps. `discriminative`; mastery 1.00, `interval_index` 3, `next_review` 2026-11-11.
- **Kernel deep-dive tangent (2026-10-12, learner-initiated; fact-check PASS per turn):** the two kernels' origins (one shared idea, two jobs), the widening gap with no flip point, the crowd-in-the-tail-by-construction chain, and the `σ_i` binary-search re-anchor.
- **Bookkeeping note:** the two practice rows in `Attempts.json` are stamped `2026-10-11` while the exit-ticket row, the session and the handoff are stamped 2026-10-12 — surfaced in the log, not rewritten (evidence dates are the Tutor's; an audited `ops.py amend` is the sanctioned route).
- **Cosmetic client glitch:** the exit ticket first rendered as mixed Chinese/English on the learner's end; the same verified text was re-emitted cleanly — no content change, no re-verification.
