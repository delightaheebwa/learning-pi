# Learning Record — PCA anomaly detection, the round cloud, and the elbow position — 2026-10-07

**Date:** 2026-10-07 · **Lesson:** Phase 1 L10 — Dimensionality Reduction (CP3 minis 4–5 + CP3 practice) · **Type:** concept
**Highest Bloom demonstrated:** Evaluate (judged a teammate's PCA proposal on isotropic data; judged which rule — elbow vs threshold — answers which question; located the tutor's own error)

## What was learned

- **PCA as anomaly detector (CP3 mini 4):** a point's reconstruction error is *per-sample*, not global: $\text{error}_i = \lVert x_i - \hat{x}_i \rVert^2 = \sum_{\text{dropped axes}} (\text{coordinate})^2$ — the squared distance from the point across the kept subspace. Train PCA on normal data, keep top-$k$, flag points whose own error crosses a threshold (Rohit: "samples with high reconstruction error are outliers that do not fit the learned subspace"). Geometry locked: a huge coordinate on a **kept** direction survives projection (the reconstruction lands far *along* the subspace, still inside it — small error); a huge coordinate on a **dropped** direction is what's thrown away — that's the error. **Along the subspace = normal; across the subspace = suspect.** Limitation banked: extreme along-subspace points (far out on the line) get no flag — the detector sees subspace-relative geometry only.
- **The round cloud / isotropic degenerate case (CP3 mini 5):** equal eigenvalues ($\lambda I$) ⇒ every direction is an eigenvector, the λ ranking is a total tie, PCA's axes are arbitrary (3B1B anchor: a matrix that scales everything equally has one eigenvalue but *every* vector is an eigenvector). Flat scree = no elbow anywhere; keep-95% can't even drop one bar. **PCA's compression power needs unequal spread — shape, not size.**
- **Curse of dimensionality (surface + tangent):** distance concentration = pairwise distances become *more alike* (Rohit's max/min ratio ~1.8 at d=10 → ~1.02 at d=1000) — contrast lost, not magnitude. PCA never shrinks the cloud: the trace pie $\Sigma\lambda$ is fixed under rotation; PCA only *redistributes* the fixed total into as few directions as the data allows. The "nothing to cut" verdict comes from equal $\lambda$'s; distance similarity travels with the high-dimensional regime but blocks the cut through the equal spread. Micro-check sealed: λ=(99,1) compresses at 1% loss; λ=(50,50) (same total) loses 50%.
- **Elbow convention (re-anchored in the Pt2 repair):** the elbow sits at the first bar whose *incoming drop* is small; you keep the bars **before** it (mini-2 anchor: "falling slows down at 35" → keep $k=3$ of 100,80,40,35,…). On the practice scree 50, 24, 4, 2: elbow = $k=3$ (kept 78/80, error 2); the 95% threshold rule also picks $k=3$ (78 ≥ 76) — the two rules *agree* here; the elbow-vs-threshold disagreement is a real phenomenon but lives on other screes (mini-3's).
- **Scree etymology:** scree = the rock pile at a cliff's base (Cattell 1966) — cliff = structure, rubble = noise tail, elbow = where they meet.

## Misconception corrected + tutor error logged

- **Learner slip (Pt2):** steering by bar *heights* ("elbow at 24", "slows down after 4") instead of bar *positions*. **Detector:** on a scree, $k$ is the position you choose; heights are the λ menu; walk the *drops* — the elbow is where the drops themselves shrink. The learner's bend-locating instinct was ultimately right; the interim confusion was driven by the tutor's mis-steer.
- **Tutor error (corrected openly in-session):** the tutor said "35 was the third bar" and steered the elbow to $k=2$ on the practice scree — refuted by the fact-check receipt (35 is the fourth bar; keep the bars before the flat zone ⇒ $k=3$). Retracted to the learner verbatim: "your bend-locating instinct was right; the confusion was mine." The "elbow and threshold disagree by one component on this scree" line was also retracted (they agree here).

## Annotated learner quotes (own words to reuse)

- "i'd expect it to be big since in terms of reconstruction, the cloud falls short by a lot" (mini-4 elicit).
- "i would conclude it is an anomaly/outlier. its error comes from the fact that it is far off from the learned subspace." (Pt3 pass).
- "PCA lives and dies on whether the spread is irregular or not. in this case it is regular spread hence no 'minor directions' for PCA to chop off." (Pt4 pass — Evaluate level).
- "PCA just cuts a slice of the cake but doesnt make the cake as a whole smaller." / "since distances are getting less and less…" (curse synthesis — shape-vs-size framing, then repaired).
- "the scree is a bunch of bars of equal height of 100." (round-cloud read).

## Evidence

- Warm-up 3/3 (grade-audit agreed, all sure) · CP3 practice Pt1/Pt3/Pt4 pass, Pt2 fail→fail→pass with grade-audit receipts agreeing at every step; final micro-check pass (39/40, error 2) · fact-check PASS on every consolidation (mini 4, mini 5, curse tangent + micro-check, elbow re-anchor, scree etymology) · quiz-audit PASS on the elicitation batches and the practice batch (first cycle).
