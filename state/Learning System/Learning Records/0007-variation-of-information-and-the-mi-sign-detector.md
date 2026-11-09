# Learning Record 0007 — Variation of Information, and the MI sign detector

- **Date:** 2026-09-21
- **Lesson:** Information Theory (Phase 1 L09) — CP5 practice (fresh joint) + CP5.5 (V(X,Y) consolidation)
- **Concepts:** Mutual Information (reinforced), Variation of Information (new)

## What was learned

1. **First-ever I(X;Y) computation on a fresh joint** [[0.35,0.15],[0.15,0.35]]: 0.119 bits, reached via both the entropy-difference route (H(X)+H(Y)−H(X,Y) = 2 − 1.8813) and the KL/ratio route (Σ p·log2(p/p·p), diagonal ratios 1.4 = costs, off-diagonal 0.6 = rebates, truth-weighted, costs beat rebates).
2. **Variation of information** V(X,Y) = H(X,Y) − I(X;Y) = H(X|Y) + H(Y|X) = H(X) + H(Y) − 2I: the two Venn wings — what the variables *don't* tell each other. V = 0 iff mutual determinism; V = H(X)+H(Y) iff independent. External angle: Meilă (2003 COLT / 2007) — VI is a true metric (triangle inequality) used to compare clusterings.
3. **Why VI is a metric and MI isn't:** MI fails axiom 1 spectacularly (MI(X,X) = H(X) ≠ 0 — an "anti-distance"); *arithmetic* flips of MI (pure functions f(I)) all die at axiom 1 too, since d(X,X) = f(H(X)) can't vanish for every entropy value; VI works because it is the *geometric* complement of the overlap inside the union — its H(X)+H(Y) offsets cancel identically at d(X,X), and Meilă's triangle-inequality theorem applies to it. Practical payoff: a metric keeps "close" transitive enough to reason with (bounds through a reference; the B=(X,Y) counterexample shows raw similarity is intransitive: I(A;B)=1, I(B;C)=1, I(A;C)=0).

## Corrected misconception (same session)

**MI sign/ordering slip (application error):** on the fresh-joint practice the learner answered −0.119 bits (sure) — magnitude exactly right, sign flipped via the H(X,Y) − H(X) − H(Y) ordering. The nonnegativity theorem (Gibbs' inequality, exit-ticketed 3/3 on 09-18) was known in isolation but not used to reject an impossible sign. Corrected same session with the "theorem as built-in error detector" framing; internalized by exit ticket E3 the same day (correctly rejected a reported −0.3 bits as impossible).

## Evidence — highest Bloom level demonstrated

- **Evaluate:** E3 — diagnosing a classmate's impossible I(X;Y) = −0.3 bits report from the nonnegativity theorem alone, no work shown.
- **Apply:** fresh-joint I computation via two routes; V computed two ways (1.7626 bits both); V from marginals-only data (3, 0.8 → 1.4 bits); independence MCQ (2 bits).
- **Understand:** V in own words ("what X and Y don't tell each other — their secrecy level"; 0 at coupling, max at independence).

## State

- Attempts: Mutual Information fail → pass (interval_index 1, next_review 2026-09-28); Variation of Information pass ×2 (interval_index 3, next_review 2026-10-21); KL Divergence pass (interval_index 3).
- Lesson paused after CP5.5; CP6 next. No Feynman yet for CP5/CP5.5 (comes at lesson end).
