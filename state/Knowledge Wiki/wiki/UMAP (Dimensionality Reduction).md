<!-- provenance: status=verified | source=Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap.md (umap-learn docs) + 2026-10-13 - dimensionality-reduction - umap-params.md (Basic UMAP Parameters) + 2026-10-13 - dimensionality-reduction - umap-paper.md (McInnes & Healy 2018, ArXiv 1802.03426, Definition 11 / Algorithm 5) + 2026-10-13 - dimensionality-reduction - umap-faq.md + 2026-10-13 - dimensionality-reduction - rohit.md (Rohit P1 L10; §3.2 graph layout + negative sampling, §4.3 hyper-parameters, and the Weaknesses section for the Laplacian/spectral-init concession) + Kobak & Linderman 2019, "UMAP does not preserve global structure any better than t-SNE when using the same initialization" (bioRxiv; cited as [29] in umap-paper) | verified-by=fact-check-agent | date=2026-10-26 | learner-note block: the "## My understanding" section is the learner's verbatim note (learner-note; fourteen statements as of 2026-10-19 — two from 2026-10-13, three appended 2026-10-14, three appended 2026-10-16, three appended 2026-10-17, three appended 2026-10-19, nothing overwritten) -->

# UMAP (Dimensionality Reduction)

> **Type:** concept · **Track:** AIEFS · **Source:** umap-learn documentation (umap-learn.readthedocs.io) + McInnes & Healy, *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction* (ArXiv 1802.03426, 2018) + the umap-learn FAQ + Rohit P1 L10 (Dimensionality Reduction) · **Lang:** Python (`umap-learn`)
> **Insight:** UMAP assumes the data lies **uniformly on a locally connected Riemannian manifold with a locally constant metric**; from those assumptions it models the manifold as a *fuzzy topological structure* built patch by patch, and the embedding is the low-dimensional arrangement whose fuzzy structure best matches.
> Related: [[t-SNE (Dimensionality Reduction)]], [[Curse of Dimensionality]], [[PCA (Dimensionality Reduction)]], [[Perplexity]]

## The three assumptions (the docs, verbatim)

The umap-learn docs open with "The algorithm is founded on three assumptions about the data":

1. "The data is uniformly distributed on Riemannian manifold;"
2. "The Riemannian metric is locally constant (or can be approximated as such);"
3. "The manifold is locally connected."

and then: "From these assumptions it is possible to model the manifold with a fuzzy topological structure. The embedding is found by searching for a low dimensional projection of the data that has the closest possible equivalent fuzzy topological structure."

The name spells the recipe out: **U**niform **M**anifold **A**pproximation and **P**rojection. The docs also file it as a technique "that can be used for visualisation similarly to t-SNE, but also for general non-linear dimension reduction" — a wider remit than t-SNE's visualization-first pitch.

**Where the uniformity assumption comes from (paper).** Uniform spread on its own manifold is not something real data supplies, and the paper says as much: for theoretical reasons it is *beneficial* to assume it, and even without the assumption results "are only valid in the limit of infinite data", while "in practice, finite real world data is rarely so nicely behaved." The move is to *choose* a metric instead of inheriting the ambient one — assuming "the manifold has a Riemannian metric not inherited from the ambient space, we can find a metric such that the data is approximately uniformly distributed with regard to that metric." Uniformity is then a consequence of the metric choice, not a claim about the data as given.

## Manifold = a local property, not a dimension count

A manifold is defined by what a **small enough patch** looks like, not by the size of the whole object or by how folded it is:

- a straight line is a perfectly good 1-D manifold and a flat plane a 2-D one — degenerate cases where the surface is flat everywhere;
- an unrolled, flat sheet counts as a manifold too, so *folding* is not what makes something a manifold (the Swiss roll is a manifold because of its local structure, not because it is rolled);
- the defining property is that every sufficiently small patch looks like ordinary flat space (locally Euclidean) — and "locally constant metric" is the same statement in metric language.

That is why the local-connectivity and local-metric assumptions are the load-bearing ones: they only have to hold *patch by patch*.

## The mechanism: patches → glue → match

The paper's high-level construction: "UMAP uses local manifold approximations and patches together their local fuzzy simplicial set representations to construct a topological representation of the high dimensional data", and then "optimizes the layout of the data representation in the low dimensional space, to minimize the cross-entropy between the two topological representations." Read as three moves:

1. **Patch.** Each point's neighbourhood is a small connected patch of the manifold. Inside a patch the metric is (approximately) constant, so distances there are honest and the patch can be summarised locally.
2. **Glue.** Patches share neighbours, so their fuzzy representations overlap and merge into **one** global fuzzy structure for the whole data set. This is what *locally connected* buys: without connections there is nothing to sew.
3. **Match.** Build the same kind of fuzzy structure for a candidate low-dimensional layout, and score the mismatch; the embedding is the layout "that has the closest possible equivalent fuzzy topological structure."

"Manifold learning" is therefore a local-to-global construction: learn the surface patch by patch, then glue. Rohit's L10 says the same thing in one line — UMAP "builds a weighted graph in high-dimensional space (the 'fuzzy topological representation') and then finds a low-dimensional layout that preserves this graph as well as possible."

## Stitching needs continuity, not distinctness

Two patches are glued **where they share** — the overlap *is* the stitching. Two patches with zero overlap cannot be sewn honestly, which is exactly the **locally connected** assumption. What breaks at the extreme is the next section.

## ⚠️ The random-k-NN pull-together failure mode ("How UMAP can go wrong")

The FAQ's own failure page: if a point is maximally far from every other point (it shares no feature with anything under the chosen distance function), then "UMAPs assumption of all points lying on a connected manifold can lead us astray":

- "From this points perspective all other points are equally valid nearest neighbours so its k-nearest neighbour query will return a random selection of neighbours all at this maximal distance."
- The local kernel says a point should be maximally similar to its nearest neighbour — and here all `k` candidates sit at that same maximal distance, so "they will all be considered maximally similar".
- The optimizer then tries "to pull all these randomly selected points together". Add enough such points and the whole embedding is dragged into one blob, destroying the structure the map was meant to show.

The guard is `disconnection_distance`: it will "cut any edge with a distance greater than the value passed in". It defaults to `None`, which resolves to "the maximal value for any of our supported bounded metrics and otherwise set to `np.inf`". Cutting those edges disconnects the manifold, so the orphan point starts where it was initialised and is pushed away from everything else. When vertices do end up disconnected the library throws a warning, and `umap.utils.disconnected_vertices()` lists them (usable as a filter before retraining or plotting).

## The two dials

UMAP's two load-bearing knobs act on **different sides of the pipeline** — and the 2026-10-14 pause exit ticket showed that separation is not yet automatic: `n_neighbors` shapes the *input* graph, `min_dist` shapes only the *output* layout.

### `n_neighbors` — the INPUT-side dial (a hard integer)

The docs: `n_neighbors` "controls how UMAP balances local versus global structure in the data. It does this by constraining the size of the local neighborhood UMAP will look at when attempting to learn the manifold structure of the data. This means that low values of `n_neighbors` will force UMAP to concentrate on very local structure (potentially to the detriment of the big picture), while large values will push UMAP to look at larger neighborhoods of each point when estimating the manifold structure of the data, losing fine detail structure for the sake of getting the broader of the data." Default **15**; the docs sweep 2 → 200 on an 800-point colour cube.

- **A hard integer, one fixed list length for the whole run** — not a per-point soft count. That is the exact contrast with [[t-SNE (Dimensionality Reduction)|perplexity]]: perplexity is an *effective* number of neighbours (`Per(P_i) = 2^{H(P_i)}`) against **one user-set target shared by every point** (a non-integer such as 23.7 is legal on that knob), and what varies per point is the bell width `σ_i`, binary-searched until *that* point's `Per(P_i)` equals the target — while `n_neighbors` is a literal k handed to a k-NN query. Rohit's L10 files the knob as "how many neighbors define local structure (similar to perplexity). Higher values preserve more global structure" — the same *role*, a different *object*.
- **Why k carries the whole local↔global balance by itself:** each point gets a local chart of its k neighbours, and the charts are glued where they overlap. Small k ⇒ charts barely overlap ⇒ UMAP "merely glues together small chains" and, "due to the narrow/local view, fails to see how those connect together. It also leaves many different components (and even singleton points)" — "from a fine detail point of view the data is very disconnected and scattered throughout the space". Large k ⇒ charts overlap nearly everywhere ⇒ the map coheres, "but at the loss of some of the finer local structure (individual colors are no longer necessarily immediately near their closest color match)". There is **no separate global module** in the construction; nothing else gets to say what "global" means, so k is the only thing holding that end of the trade.
- **The anchor sweep (docs, k = 2 / 20 / 200):** at `n_neighbors=2` the "narrow/local view" fails to see how the chains connect; by `20` "we have a fairly good overall view of the data showing how the various colors interelate to each other over the whole dataset"; at `200` "the overall structure (blues, greens, and reds; high luminance versus low) is well captured, but at the loss of some of the finer local structure". The docs call this "the local/global tradeoff provided by `n_neighbors`".
- **The paper's version of the same dial:** n is "the local scale at which to approximate the manifold as roughly flat, with the manifold estimation averaging over the n neighbors. Manifold features that occur at a smaller scale than within the n nearest-neighbors of points will be lost"; smaller n "ensure[s] detailed manifold structure is accurately captured (at a loss of the 'big picture' view of the manifold)", larger n captures "large scale manifold structures, but at a loss of fine detail structure which will get averaged out in the local approximations", and "With smaller n values the manifold tends to be broken into many small connected components".
- **What the k neighbours normalise to:** the local kernel's cardinality is fixed, not just its list length — the paper sets `Σ_j exp(−max(0, d(x_i, x_j) − ρ_i)/σ_i) = log₂(k)`, with `ρ_i` the distance to the nearest neighbour (which "ensures that x_i connects to at least one other data point with an edge of weight 1; this is equivalent to the resulting fuzzy simplicial set being locally connected at x_i") and `σ_i` found by binary search (Algorithm 3). So k is also the patch's *membership mass*, fixed at `log₂(k)`.

### `min_dist` — the OUTPUT-side dial (the packing floor)

The docs: `min_dist` "controls how tightly UMAP is allowed to pack points together. It, quite literally, provides the minimum distance apart that points are allowed to be in the low dimensional representation." Default **0.1**; the docs sweep 0.0 → 0.99.

- **Output side, by the paper's own definition:** min-dist is "a hyperparameter directly affecting the output, as it controls the fuzzy simplicial set construction from the low dimensional representation. It acts in lieu of the distance to the nearest neighbor used to ensure local connectivity. In essence this determines how closely points can be packed together in the low dimensional representation" — and the paper calls it "an essentially aesthetic parameter, governing the appearance of the embedding".
- **The anchor sweep (docs, 0.0 → 0.99):** at `min_dist=0.0` "UMAP manages to find small connected components, clumps and strings in the data, and emphasises these features in the resulting embedding"; as the value rises "these structures are pushed apart into softer more general features, providing a better overarching view of the data at the loss of the more detailed topological structure". Low values give "clumpier embeddings" — useful "if you are interested in clustering, or in finer topological structure".
- **It never touches the graph.** The charts, their overlaps and any disconnected vertices are all settled on the input side, before the low-dimensional packing begins, so **a fragmented graph stays fragmented whatever `min_dist` is set to.** Fragmentation is a connectivity (`n_neighbors`) story, not a spacing story.
- **The floor arrives as a force curve, not a wall.** The paper defines the target membership `Ψ` piecewise — `1` if `‖x − y‖₂ ≤ min-dist`, otherwise `exp(−(‖x − y‖₂ − min-dist))` — and then fits a smooth, differentiable approximation `Φ(x, y) = (1 + a‖x − y‖₂^{2b})⁻¹`, "where a and b are chosen by non-linear least squares fitting against the curve Ψ"; Algorithm 5 then descends on `log Φ` ("Fit Φ from Ψ defined by min-dist"). Same shape as t-SNE's low-D side: a well that packs points down to the floor, with repulsion that fires below it.
- **⚠️ Sources disagree on how hard the floor is.** The docs are literal — "quite literally, provides the minimum distance apart that points are allowed to be" — while the paper's own optimisation only *penalises* sub-floor placements, because what is fitted is a smooth curve approximating a piecewise rule. **Resolution (taught 2026-10-14):** the practical reading is *the optimizer strongly resists packing points closer than `min_dist`*, and the mechanism is *a gradient penalty, not a hard constraint*. The two readings agree on the observable behaviour (0.0 ⇒ clumps and strings; larger values ⇒ structures spread "into softer more general features") and disagree only on the language of enforcement.

**The knob-crossing failure mode (2026-10-14 exit ticket).** The two dials are easy to swap under pressure: item X3 placed `min_dist` on the *input* side of the pipeline, and item X1 gave only the gain half of the `n_neighbors` trade. The separator is one sentence — *`min_dist` never touches the graph*: if the question is about charts, neighbours, connectivity or components, the dial is `n_neighbors`; if it is about packing, spacing or the look of the picture, it is `min_dist`.

## Global structure: goal, not guarantee

Rohit's L10 headline states the advantage flatly, the paper hedges it, and the FAQ frames it as a goal with a documented way to break it. The two mechanisms below are why relative cluster positions carry signal at all; the ⚠️ block is why the claim stops at "arguably". (Taught and landed 2026-10-16, CP5 mini 4 — the graded exit ticket was not run.)

**Mechanism 1 — negative sampling puts push-back everywhere, not just along edges.** The fuzzy graph only ever encodes *local* neighbourhoods. Global information enters through the objective: the cross-entropy splits into the `µ(a) log ν(a)` term (handled by "sampl[ing] 1-simplices with probability `µ(a)`") and the term "(1 − µ(a)) log(1 − ν(a)) [which] requires negative sampling – rather than computing this over all potential simplices we randomly sample potential 1-simplices and assume them to be a negative example (i.e. with membership strength 0)". Those negatives are drawn from the vertex distribution `P(x_i) = Σ_{a : d₀(a)=xᵢ}(1 − µ(a)) / Σ_{b : d₀(b)≠xᵢ}(1 − µ(b))`, "which can be reasonably approximated by a uniform distribution for sufficiently large data sets". In force language: "whenever an attractive force is applied to an edge, one of that edge's vertices is repulsed by a sampling of other vertices" (through the same fitted `Φ`). So the repulsion is sampled **across the whole embedding** and decays with distance rather than switching off at the edge boundary — drifting clusters meet push-back from everything else. A global constraint carried by a purely local graph.

**Mechanism 2 — the symmetric union lets connectedness leak global information.** Each point's local graph is directed; the combined graph is built with the probabilistic t-conorm union. With `A` the weighted adjacency matrix of the merged directed graph, the undirected UMAP graph's adjacency is

`B = A + Aᵀ − A∘Aᵀ`  (∘ = the Hadamard / pointwise product)

Read as probabilities: "If one interprets the value of `A_ij` as the probability that the directed edge from `x_i` to `x_j` exists, then `B_ij` is the probability that at least one of the two directed edges (from `x_i` to `x_j` and from `x_j` to `x_i`) exists." An edge therefore survives if **either** direction voted for it, so overlapping charts pull on one another transitively — a chain of charts transmits pull **indirectly**. Connectedness itself is a global signal; this is the half of the mechanism the learner's own glue prior already had.

**Why t-SNE's gaps are weaker.** In t-SNE, cross-cluster pairs carry `P_ij ≈ 0`, so rearranging the gaps barely moves the objective — inter-cluster distances end up largely decided by starting position and drift. (Taught honestly in-session: ≈ 0, **not** exactly 0 — the probability bookkeeping still couples positions weakly.) The paper makes the same contrast structurally: "the objective function derived for UMAP (cross-entropy) is significantly different from that of t-SNE (KL-divergence), in how it penalizes failures to preserve non-local and global structure".

**⚠️ Sources disagree on the strength of the claim — three sources, three strengths.**

- **Rohit (L10, the headline):** a flat advantage — "Better global structure. The relative positions of clusters in the output tend to be more meaningful than in t-SNE"; his comparison table files UMAP under "Local + some global structure".
- **The paper (abstract + weaknesses):** hedged — UMAP "is competitive with t-SNE for visualization quality, and arguably preserves more of the global structure with superior run time performance"; and "while we believe that UMAP can capture more global structure than these other techniques, it remains true that if global structure is of primary interest then UMAP may not be the best choice for dimension reduction" (MDS for full distance-matrix preservation, PHATE for a local+long-scale hybrid).
- **The FAQ (a goal, plus a way to break it):** "One of UMAPs goals is to have distance between clusters of points be meaningful … This means that clusters can end up spread out with a fair amount of space between them", and the clustering pitch — "by preserving more global structure and creating meaningful separation between connected components of the manifold on which the data lies, UMAP offers more meaningful clusters" — sits in the same FAQ as the failure mode that destroys it (see `## ⚠️ The random-k-NN pull-together failure mode` above): "Add a sufficiently large number of these points and our entire space gets pulled together destroying any of the structure we had hoped to identify."

**Resolution taught 2026-10-16 — a graduated claim, not a flat advantage.** Global structure is a *design goal*: normally visible, and breakable by the documented outlier collapse that `disconnection_distance` mitigates (it cuts those edges, disconnecting the manifold so the orphans are pushed away). Practical rule: **trust relative arrangement more than t-SNE's, never as a certificate** — "arguably", never "guaranteed". (Graded exit ticket sealed 3/3 on 2026-10-17: E1 graduated claim, E2 whole-embedding repulsion vs t-SNE $P_{ij} \approx 0$, E3 own-words + `disconnection_distance` check.)

**The wrinkle that keeps it "arguably" — the initialization.** By default UMAP does not start from noise (the paper allows random initialization, but spectral layout is what is used in practice): "since the symmetric Laplacian of the graph G is a discrete approximation of the Laplace-Beltrami operator of the manifold, we can use a spectral layout to initialize the embedding. This provides both faster convergence and greater stability within the algorithm" (Algorithm 4 runs standard spectral methods on the symmetric normalized Laplacian). The paper's weaknesses section then concedes the consequence: "a significant contributor to UMAP's relative global structure preservation is derived from the Laplacian Eigenmaps initialization (which, in turn, followed from the theoretical foundations). This was noted in, for example, [29]. The authors of that paper demonstrate that t-SNE, with similar initialization, can perform equivalently to UMAP in a particular measure of global structure preservation." Reference [29] is **Kobak & Linderman 2019**, *UMAP does not preserve global structure any better than t-SNE when using the same initialization*. The paper's own counterweight sits in the same paragraph: "the objective function derived for UMAP (cross-entropy) is significantly different from that of t-SNE (KL-divergence), in how it penalizes failures to preserve non-local and global structure, and is also a significant contributor." So the honest reading is *initialization + objective together* — and the paper's future-work section adds that the field is "hampered by the lack clear objective measures, or even definitions, of global structure preservation".

## Contrast with t-SNE

t-SNE states **no** data assumptions: it matches pairwise neighbour probabilities non-parametrically (see [[t-SNE (Dimensionality Reduction)]]). UMAP's three assumptions are what let it claim more — Rohit's L10 headline is "UMAP: faster, better global structure", and his comparison table files UMAP under "Local + some global structure", while the FAQ frames global structure as a goal the failure mode above can break rather than a guarantee. **The ⚠️ Rohit-vs-paper-vs-FAQ disagreement was resolved on 2026-10-16 as a graduated claim** — see `## Global structure: goal, not guarantee` above.

## The pipeline: PCA → UMAP → HDBSCAN

For high-dimensional real-world data (e.g. 300+ features or gene expression / embeddings), standard practice is the three-stage ladder: **PCA (~50 dims) → UMAP (~10–20 dims) → HDBSCAN**. These numbers are practical defaults rather than mathematical laws; for smaller datasets UMAP can run directly on raw features.

Each stage does what the other cannot:

### 1. Why PCA first (~50 dims): denoise neighbor distances

UMAP's first stage is constructing a k-nearest-neighbour graph in ambient space. At high dimensions (300+), the [[Curse of Dimensionality]] kicks in: pairwise distances **concentrate** (the max/min ratio collapses from ~1.8 at $d=10$ to ~1.02 at $d=1000$). When all points appear nearly equidistant:
- "Nearest" carries little contrast over "farthest", making graph edges noisy and arbitrary.
- Computing exact or approximate k-NN in 300+ dimensions is computationally expensive.

PCA preserves the orthogonal directions of maximal variance, stripping out low-variance noise directions. This **denoises the neighbor distances** before the k-NN graph is built and makes graph construction vastly cheaper.

**The contrast:** PCA is linear and **cannot unfold curved manifolds** (it produces flattened, overlapping shadows). UMAP is non-linear and unfolds manifolds, but **cannot repair noisy input distances**. PCA fixes the metric noise so UMAP can unfold the geometry.

### 2. Why UMAP to intermediate dimensions (~10–20 dims)

When the downstream task is clustering rather than human visualization, squashing directly to 2D is counterproductive. Embedding into ~10–20 dimensions preserves more manifold topology and geometric degrees of freedom while eliminating ambient redundancy, giving the clusterer cleaner separation without the extreme crowding penalties of 2D projection.

### 3. Why HDBSCAN last (and why K-Means is a poor choice)

Clustering directly on a 2-D UMAP visualization using K-Means is a dual error:

1. **Geometry — UMAP does not preserve density:**
   The umap-learn FAQ notes that UMAP "does not preserve density well" and "will contract connected components of the manifold together". The distances between clusters and the apparent densities of clumps in a UMAP plot are distorted by the non-linear optimization. Cluster boundaries drawn directly off a 2-D plot are artifacts of projection rather than features of the underlying distribution.
2. **Clusterer assumptions — forced assignment vs density estimation:**
   - **K-Means** assumes spherical, equal-variance clusters and **must assign every point** to a cluster center. In noisy real-world data, it is forced to label background noise and bridge outliers as legitimate cluster members.
   - **HDBSCAN** (Hierarchical Density-Based Spatial Clustering of Applications with Noise) re-estimates density directly on the ~10–20-D representation, handles arbitrary non-spherical cluster shapes of varying densities, and explicitly leaves background noise points **unlabeled** (`label = -1`).

**The stage-role detector:**
- **Building the graph:** k-NN (k-nearest neighbours — UMAP's stage 1).
- **Assigning cluster labels:** K-Means / HDBSCAN (downstream clustering).

## Feature scaling: center-only vs standardize (CP5 mini 5b)

The umap-learn FAQ addresses feature scaling directly ("Should I standardize my data?"):

1. **The mechanical distinction:**
   - **Centering** shifts the mean of each feature to 0 by subtracting $\mu_j$, leaving relative distances, spreads, and variances unchanged.
   - **Standardizing** (z-scoring) centers each feature and additionally divides by its standard deviation $\sigma_j$, scaling every feature to unit variance ($\sigma = 1$).

2. **The decision rule:**
   - **Standardize** when features are **independent measurements on incomparable scales or units** (e.g. clinical blood pressure in mmHg vs age in years vs weight in kg). Without standardization, the feature with the largest numerical variance dominates Euclidean distance in ambient space, distorting nearest-neighbor selection and destroying true k-NN graph connectivity.
   - **Center-only (do not standardize)** when features **share a meaningful geometric relationship or common coordinate system** (e.g. latitude and longitude, physical 2-D/3-D spatial measurements). Rescaling axes with unequal variances in geometric coordinates distorts genuine aspect ratios (e.g. squishing an elongated geographic island into an artificial sphere).

## Queued for this concept

Still to come in L10's CP6:

- **CP5 mini 4 — the global-structure claim**: **SEALED 2026-10-17** (exit ticket 3/3: E1 graduated claim, E2 whole-embedding negative sampling, E3 own-words + `disconnection_distance` check).
- **CP5 mini 5a — the pipeline (PCA → UMAP → HDBSCAN)**: **SEALED 2026-10-17** (PCA denoises k-NN graph distances; UMAP density distortion; HDBSCAN leaves noise unlabeled vs K-Means forced assignment).
- **CP5 mini 5b — center-only vs standardize**: **SEALED 2026-10-19** (mechanics: mean shift vs unit variance; decision rule: standardize for independent features on incomparable scales, center-only for shared coordinate geometries).
- **CP5 Practice (4-item batch)**: **SEALED 2026-10-19 (4/4)** (P1 `n_neighbors` vs `min_dist` clean under retrieval; P2 global structure & outlier collapse; P3 PCA→UMAP→HDBSCAN pipeline rationale with KNN/K-Means detector verified; P4 scaling application across domains).
- **Checkpoint 5 (UMAP) is FULLY SEALED.**
- **CP6** — kernel PCA (RBF) and the "high variance = important" contradiction (Rohit's definition vs Shlens's assumption that can fail), the method-choice map, then the final cumulative quiz + Feynman explain-back.

## Open questions

- How much of the "global structure" claim survives the failure mode above, and under what tuning? — **answered as far as the sources go (2026-10-16):** it is a graduated claim — normally visible, breakable by the outlier collapse that `disconnection_distance` mitigates; the paper's "arguably" is partly attributable to the Laplacian/spectral initialization (Kobak & Linderman 2019), with the cross-entropy-vs-KL objective as the paper's own counterweight. Still unmeasured: the relative weight of those two contributors — the paper itself says the field lacks agreed measures, even definitions, of global-structure preservation.
- How the local connectivity of each patch is chosen in code, and what it changes — **partly answered 2026-10-14:** `ρ_i` is the distance to the nearest neighbour (so each point connects to at least one other with weight 1, i.e. local connectivity at that point) and `σ_i` is binary-searched until the patch's memberships sum to `log₂(k)` (paper Algorithms 2–3). Still unread: the `local_connectivity` / spectral-initialisation corner cases in code.

## Sources

- umap-learn documentation: https://umap-learn.readthedocs.io/
- McInnes, Healy & Melville, *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*, ArXiv 1802.03426: https://arxiv.org/abs/1802.03426
- UMAP FAQ: https://umap-learn.readthedocs.io/en/latest/faq.html
- Basic UMAP Parameters: https://umap-learn.readthedocs.io/en/latest/parameters.html
- Kobak & Linderman 2019, *UMAP does not preserve global structure any better than t-SNE when using the same initialization*: https://www.biorxiv.org/content/10.1101/2019.12.19.877522v1

## My understanding

> **status=learner-note** — the learner's words, verbatim from the 2026-10-13 session (CP5 mini 1), never rewritten. The annotations around them are the tutor's and the source's.

**The elicitation prior (before the mini was taught):**

> "i think for data to lie on a manifold it means it lies in an area of the plot whereby there are many folds(like our swiss roll example). i think the assumption you have to make is that each layer of the fold is a plane"

**Source framing (annotation, not a rewrite):** the second sentence is the idea — "each layer of the fold is a plane" is local flatness — and the session carried it forward as the patch picture. The first sentence's *frame* is what slipped: folding is not what makes something a manifold (an unrolled flat sheet is one too), and a manifold is defined by its local structure, not by being an area with folds.

**The State-rung statements (both partial, both corrected in the same turn):**

> "1. A manifold is simply whatever shape is of dimension 2D or higher. 2. There must be no sharing of points hence there must be distinct neighborhoods."

**Annotations (not rewrites):** (1) a manifold is not a dimension count — a straight line is a 1-D manifold and a flat plane a 2-D one; what defines it is that every sufficiently small patch looks like ordinary flat space. (2) stitching runs on **sharing, not distinctness** — patches are glued where they overlap, and the failure the docs name is the opposite extreme: a point whose nearest neighbours are all maximally far gets a *random* set of k-NN, all treated as maximally similar, which the optimizer then drags together.

### 2026-10-14 — CP5 minis 2–3 (`n_neighbors` and `min_dist`)

> **status=learner-note** — three more of the learner's statements, verbatim from the 2026-10-14 session, **appended** (nothing from 2026-10-13 was altered). The annotations around them are the tutor's and the source's.

**The State-rung statement — the leaf analogy (`n_neighbors`):**

> "small patch chain produces a map that's like zooming into a leaf and seeing the fine detail of things like the stomata but you don't see how all that fine detail comes together to form the overall leaf structure while the big patch chain is like zooming out and seeing that same leaf from afar... you see the overall leaf structure but you can't see the fine detail that brings it together."

**Source framing (annotation, not a rewrite):** accepted as-is — both ends of the trade are right, and the "small patch chain" is the docs' own picture (at k = 2 UMAP "merely glues together small chains"). The session *extended* it rather than correcting it: k is each point's chart size, the charts' **overlap** is what glues the map, and there is no separate global module — which is why one number moves the picture from stomata-resolved to leaf-resolved.

**The State-rung statement — the box-packer analogy (`min_dist`):**

> "min_dist is the guy that tells you how tightly to pack those set of items in that box. the higher it is, then you are to pack the items with more spacing between them while the lower it is, then you are to pack the items with less spacing."

**Source framing (annotation, not a rewrite):** direction correct at both ends, and it uses the docs' own verb ("how tightly UMAP is allowed to pack points together"). One refinement taught in-session: the floor is **permissive, not a veto** — points may pack down *to* it, and sub-floor placements are strongly **penalized** by the fitted attraction/repulsion curve (paper Definition 11 / Algorithm 5), not forbidden outright — and raising the value reshapes the whole curve, so the entire picture softens, not just the tightest pairs.

**The closing statement — the trigger:**

> "it kicks in when two points try to go lower than the floor in terms of distance between them."

**Source framing:** complete and correct, and checkable against the paper: what fires on sub-floor pairs is repulsion through the fitted `Φ`, not a hard wall (the ⚠️ disagreement above).

### 2026-10-16 — CP5 mini 4 (the global-structure claim)

> **status=learner-note** — three more of the learner's statements, verbatim from the 2026-10-16 session, **appended** (nothing from 2026-10-13 or 2026-10-14 was altered). The annotations around them are the tutor's and the source's.

**The elicitation prior (before the mini was taught):**

> "the global structure comes from the gluing together of the charts. i think what stops it is the 'glue'(the overlap between neighborhoods/charts)."

**Source framing (annotation, not a rewrite):** the first sentence is the right half of the mechanism, and it is now **mechanism 2** on this page — the glue *is* the channel (a symmetric union keeps an edge if either direction voted, so overlapping charts pull on one another transitively). The second sentence is not a defect in gluing but the honest limit of the claim: what breaks global structure is a **break** — a point with no real neighbours (the random-k-NN pull-together failure) and, as the paper concedes, a layout whose relative positions were largely set by the spectral initialization.

**The guiding-question answer (which pool does the repulsion sample from):**

> "i didnt quite understand the question but i think it should sample from edges which are disconnected."

**Source framing (annotation, not a rewrite):** right *place* — sampling is what makes the repulsion affordable — but the pool is wider than disconnected edges: negatives are sampled across the whole embedding ("we randomly sample potential 1-simplices"), approximated by a uniform vertex distribution at scale. Edges are scarce, so most sampled pairs are non-edges — which is exactly why the push-apart pressure reaches far past the graph.

**The isomorphic micro-check (fixing fragmentation — also the second clean pass on the knob-crossing repair):**

> "they should reach for n_neighbors. raising it will change the number of points deemed as neigbors for each point. raising it increases the neighbors hence there is more overlap between neighborhoods and less seperate clumps."

**Source framing:** complete and correct — fragmentation is a chart-coverage story, so the input-side dial is the one to reach for, and widening each patch's overlap merges the components. Paired with the self-location from the same session (*"it acts on stage 2 ... it can only move them around by making them further or nearer"*), this is the second firing of the knob-crossing slip repaired **by the learner** rather than by a told answer.

### 2026-10-17 — CP5 mini 4 exit ticket + mini 5a (the pipeline: PCA → UMAP → HDBSCAN)

> **status=learner-note** — three more of the learner's statements, verbatim from the 2026-10-17 session, **appended** (nothing from earlier sessions was altered). The annotations around them are the tutor's and the source's.

**CP5 mini 4 exit ticket E3 (own-words push-pull + outlier blob collapse):**

> "it means that UMAP tries to make the global structure as honest as possible by pushing apart random sampled points that are not neighbors and pull together those that are but this breaks if points are maximally apart from each other which makes the otpimizer then consider them all neighbors and hence pull them togehter causing a collapse into a blob. what i would check is the disconnection_distance before trusting the cluster-to-cluster arrangement on a UMAP plot."

**Source framing (annotation, not a rewrite):** accepted as-is — both halves of the push/pull balance and the failure mode captured faithfully. Tutor sharpening: `disconnection_distance` *cuts* the dangerous edges; the practical check is *setting it* and screening for disconnected vertices (`umap.utils.disconnected_vertices()`), not merely checking its presence.

**Mini 5a elicitation prior (the why of PCA first and clustering after):**

> "I think it first reduces the number of dimensions to the ones that actually matter(explain most of the data). I think feeding UMAP 300 dimensions would make it harder to make neighbors plot." / "i think because some clusters may have overlap hence we may not have distinct clusters which is needed for final clustering."

**Source framing (annotation, not a rewrite):** right-shaped on both halves. Source framing adds the causal depth: UMAP's first stage is constructing the k-NN graph in the ambient space where 300+ dimensions causes distance concentration (max/min distance ratio ~1.8 at $d=10$ collapses to ~1.02 at $d=1000$), so distances are noisy and graph-building is expensive. On the clustering side: UMAP does not preserve density well and contracts components, so boundaries found on a 2-D plot are artifacts.

**Mini 5a sealing line (why clustering directly on 2-D with K-Means fails):**

> "it would be a mistake because the plot itself doesnt preserve density well hence noise will be within each cluster and KNN simply groups those clusters with their noise"

**Source framing (annotation, not a rewrite):** right density instinct ("doesn't preserve density well"), with two sharpenings taught in-session:
1. **Stage-role naming slip (KNN vs K-Means):** wrote "KNN" (the graph-building stage) where "K-Means" (the clustering algorithm) belongs. The detector: *assigning cluster labels = K-Means / HDBSCAN; building the graph = KNN*.
2. **Double mistake completed:** (a) Geometry — the 2-D plot's density is distorted and contracts connected components, so boundaries read off the plot are artifacts; (b) Forced assignment — K-Means must assign *every* point to a cluster and assumes round, equal clusters, obliging it to label noise as clusters; HDBSCAN re-estimates density on the intermediate ~10–20-D embedding and leaves noise unlabeled.

### 2026-10-19 — CP5 mini 5b (feature scaling) + CP5 practice + pause exit ticket X1

> **status=learner-note** — three more of the learner's statements, verbatim from the 2026-10-19 session, **appended** (nothing from earlier sessions was altered). The annotations around them are the tutor's and the source's.

**Mini 5b P2 elicitation prior (the why of standardization and when it hurts):**

> "1. if no standardization, i think the knn distances will be too big since features have wildly different values since they arent on the same scale but if there is then the knn distances be less since they are on the same sclae / 2. i think it would be a bad idea if their values dont vary wildy from each other. another time it would be a bad idea i think is when you actually want to see the relationship between two features in their own units e.g see relationship between people's weight(kg) and thier height(meters)."

**Source framing (annotation, not a rewrite):** direction correct on both parts. Socratic follow-up sharpened: (1) it is relative dominance across features, not the absolute size of distance, that matters — when features are on wildly different scales (e.g. kg vs mm), the large-unit feature dominates the distance calculation, drowning out the other features and destroying genuine nearest neighbors; (2) when features share a coordinate system (e.g. latitude and longitude of an island), standardizing destroys the aspect ratio and distorts an elongated shape into a sphere.

**Mini 5b Socratic guiding responses (confirming the physical intuition):**

> "1. i see so that means kilogram's contribution is deemed more weighty than that of mm. it also means we lose some \"true neighbors\" since some neighobors are just too far away due to different scales. / 2. it would make it the island spherical in shape which doesnt really reflect the true geometry of the island."

**Source framing (annotation, not a rewrite):** accepted as-is — accurately articulates both the feature dominance problem and the geometric distortion of true shape.

**Pause exit ticket X1 (core difference & when to choose which):**

> "the core difference is that centering centers the data around the mean while standaradizing does that and also puts features on the same scale. i would choose centering only when dealing with features that are essentially independent while for standardizaing i would choose for when dealing with features that have meaningful relationship"

**Source framing (annotation, not a rewrite):** the mechanical distinction is correct (centering shifts mean to 0 without changing scale; standardizing rescales to unit variance). The application rule was inverted under retrieval pressure: the UMAP FAQ rule prescribes standardizing for independent features on incomparable scales, and centering-only when features share a meaningful geometric relationship. Logged as an active structural mistake for retrieval drill on next warm-up.

## Field notes

- **The 2026-10-19 session:** CP5 mini 5b taught and sealed (elicitation prior right-shaped, Socratic reflections confirmed feature dominance and spherical distortion of shared coordinates; FAQ decision rule established). CP5 practice batch run and sealed 4/4, all `sure`, 0 hints (P1 n_neighbors vs min_dist clean pass ✓, P2 global structure / negative sampling repulsion vs outlier collapse ✓, P3 PCA→UMAP→HDBSCAN pipeline rationale with KNN/K-Means detector verified ✓, P4 scaling decision application across domains ✓). Checkpoint 5 (UMAP) fully SEALED. Pause exit ticket X1 completed (mechanical difference correct, application rule inverted: logged as active structural mistake row). Five attempts logged in Attempts.json: 4 passes (applied ×3, discriminative ×1) · 1 fail (free-recall) → mastery 0.60 advisory, interval_index 2, consecutive_correct 0, consecutive_wrong 1, next_review 2026-11-02, Last Q Type free-recall. Next: Checkpoint 6/6 (Kernel PCA with RBF kernel, high-variance assumption vs Shlens ferris wheel, method-choice map).
- **The 2026-10-17 session:** CP5 mini 4 exit ticket run and sealed 3/3, all `sure`, 0 hints (E1 graduated claim ✓, E2 whole-embedding repulsion sampling ✓, E3 own-words + `disconnection_distance` check ✓). CP5 mini 5a taught and sealed (elicitation right-shaped on both halves, 0 guiding questions; check-and-extend idea turn landed; sealing line caught the KNN/K-Means stage-role naming slip, repaired via the stage-role detector and logged as a structural Mistakes row; confirmed "makes sense" → mini 5a SEALED). Mini 5b opened (P2 probe delivered, learner paused before answering). Three passes logged in `Attempts.json` → mastery 0.90 advisory, `interval_index` 3, `next_review` 2026-11-16, `last_q_type` free-recall.
- **The 2026-10-16 session:** warm-up W1 ✓ (`n_neighbors` 2→50: coherence gained, fine local detail lost) · **W2 ✗** (`min_dist` presented as "forcing points farther apart breaks the connections" — the knob-crossing slip firing a second time, tagged `sure`; a calibration flag) → diagnose-first repair **self-located** → isomorphic micro-check ✓; then the **CP5 mini 4 idea turn landed** (global structure as a graduated claim; the ⚠️ Rohit-vs-paper-vs-FAQ contradiction resolved) with the **graded exit ticket not run** (the learner paused at the check-back).
- **The "elaborate more and simply" request was a pacing call, not an opt-out** — honored with a corrected re-delivery (the first draft failed fact-check on four overstatements: t-SNE "exactly 0", absolute drift-free phrasing, a "usually succeeds" success rate, and a single far point collapsing the whole map; the corrected draft passed and the learner's response was "makes sense"). Guiding budget: 1 of 2 spent.
- Learner rule still standing (2026-10-05): practices are paper walks or graded MCQ batches; no code writes as a learning-system task.
- "Learn the surface patch by patch, then glue" is the working one-liner for manifold learning as taught here.
- The 2026-10-13 exit ticket (3/3, all `sure`) landed the three load-bearing pieces: local flatness as the definition, patch → glue → match as the mechanism, and the random-k-NN pull-together failure with `disconnection_distance` as the guard.
- Two guiding questions were spent on the mini (UMAP had no independence evidence on record); both State-rung attempts were generations the learner made himself.
- Standing learner rule (2026-10-05): practices are paper walks or graded MCQ batches; no code writes as a learning-system task.
- The 2026-10-14 warm-up re-passed the mini-1 material 3/3, all `sure`, 0 hints (local flatness as the definition; patch → glue → match; the random maximally-similar k-NN pull-together ahead of `disconnection_distance`).
- The two dials were taught and sealed on 2026-10-14 (CP5 minis 2–3): `n_neighbors` with the leaf analogy, `min_dist` with the box-packer analogy and the closing trigger statement; two tie-downs passed 2/2 (0.0 removes the output-side floor; fragmentation is charts failing to overlap, not spacing).
- Two guiding questions were spent on mini 2 (still no independence evidence on record); mini 3 ran elicitation → tie-downs → idea → check-and-extend, with the learner generating both analogies himself.
- **Exit ticket 1/3, all `sure`, 0 hints** — X1 ✗ gains-only `n_neighbors` trade (the asked half omitted), X2 ✓ (charts stop overlapping ⇒ components and singletons float), X3 ✗ `min_dist` placed on the input side. Both fails are the **knob-crossing slip** firing twice in one batch; the learner banked the repair for a later warm-up, so the self-attribution is unelicited and the ledger row stays `active`.
- The ⚠️ docs-vs-paper reading of the floor was surfaced in-session and resolved to *strong resistance / gradient penalty* (see `## The two dials`).

## Open questions (carried by the lesson)

- Checkpoint 5 (UMAP) is fully sealed; resume at Checkpoint 6/6 (Kernel PCA with an RBF kernel, the "high variance = important" contradiction, and the method-choice map), then the final cumulative quiz + Feynman explain-back.
- The 2026-10-14 knob-crossing mistake row advanced (P1 passed clean under retrieval pressure).
- The 2026-10-17 KNN/K-Means stage-role slip advanced (P3 passed clean under retrieval pressure).
- The 2026-10-19 feature scaling application rule inversion (X1 pause exit ticket): active in Mistakes ledger, awaiting retrieval drill on next warm-up.
