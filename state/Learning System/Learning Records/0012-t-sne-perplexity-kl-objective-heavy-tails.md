# Learning Record 0012 — t-SNE perplexity + KL(P‖Q) objective + heavy tails — 2026-10-09

**Date:** 2026-10-09 · **Lesson:** Phase 1 L10 Dimensionality Reduction (CP4 minis 2 + 3/3b) · **Source(s):** Rohit P1 L10 (`Knowledge Wiki/raw/sources/2026-09-25 - dimensionality-reduction - rohit.md`); Wattenberg et al., *How to Use t-SNE Effectively* (Distill); van der Maaten & Hinton 2008 (JMLR, verified in-session via fact-check fetches).

## What was learned

- **Perplexity (CP4 mini 2, Bloom: Apply):** the name collision resolves — t-SNE's perplexity is the SAME banked $2^H$ applied to each point's neighbor distribution: $\mathrm{Per}(P_i) = 2^{H(P_i)}$, with $\sigma_i$ tuned per point until the distribution's perplexity equals the knob. It is an **effective** neighbor count (a soft number — 23.7 is possible), not a hard cutoff: "i think it will control how many true neighbors each point will keep" (learner's words). Low = very local attention, high = broader patterns; typical 5–50.
- **Perplexity ceiling (Bloom: Analyze):** on $n$ points, $P_i$ lives on the other $n-1$ points; the most spread-out it can be is uniform, giving $H = \log_2(n-1)$ and a ceiling $\mathrm{Per} = n-1$ (20 points → ceiling 19). A knob above that is an unreachable target — the precise break behind Distill's guardrail "the perplexity really should be smaller than the number of points."
- **KL(P‖Q) objective (CP4 mini 3, Bloom: Apply):** t-SNE **minimizes** $\mathrm{KL}(P\|Q)$ — never zeroes it (a 2D map cannot honor every neighborhood, so deviation always survives). $P$ is frozen (it IS the data); $Q$ is the only moving part (gradient descent on the 2D coordinates). The asymmetry is load-bearing: the weights in $\sum_i P_i \log \frac{P_i}{Q_i}$ come from $P$, so "data says near, map says far" is the expensive mismatch — "the distribution of the actual data supplies the weights" (learner's words).
- **Heavy-tail t justification (CP4 mini 3b, Bloom: Analyze):** squeezing 10D room into 2D crowds the medium-distance pairs; a Gaussian $Q$ would fine every escape ($Q_i \to 0$ at distance ⇒ $\log \frac{P_i}{Q_i}$ blows up); the Student-t's fat tail keeps $Q_i$ from collapsing, so spreading moderately-related pairs is cheap and the map relieves crowding without tearing strong neighborhoods apart — "mismatched tails compensate for mismatched dimensionalities" (JMLR). Learner reached the right conclusion (spread the crowd) with a flipped reason (product $P\times Q$ instead of the log-ratio) — repaired in-session.

## Evidence

- Warm-up (CP4 mini 1 recall): grade-audit-agreed 3/3, all sure — false neighbors, shrink-or-preserve guarantee, goal + pairwise-probability mechanism in own words.
- Mini 2: E1 prediction (hunch) → no guiding question needed; check-back (perplexity=30 on 20 points) answered from the learner's own $2^H$; fact-check PASS 6/6.
- Mini 3: E2 prediction → check-back on which distribution supplies the weights answered exactly; fact-check PASS 5/5.
- Mini 3b: E3 prediction (partial) → 1 guiding question → right conclusion, wrong reason → repaired to the log-ratio mechanism; fact-check PASS 6/6.
- Pause exit ticket: grade-audit-agreed 3/3, all sure (valid-perplexity choice under the ceiling · what moves in gradient descent · why Gaussian Q makes spreading expensive).
- Highest Bloom demonstrated: **Analyze** (the ceiling derivation from his own $2^H$; the flipped-reason repair).

## Learning notes

- The learner self-monitors pacing: he explicitly asked to slow down and "unpack more" on the heavy-tail chain rather than push into mini 4 — honored by deferring mini 4 to next session.
- Recurring shape: he reaches correct conclusions with occasionally-flipped mechanisms (cost product vs log-ratio); the repair that works is naming the actual form of the quantity (log-ratio, not product) beside his own words.
- Feynman-rubric explain-back not run (mid-checkpoint pause, not lesson end). Dependency: 0 opt-out events.
