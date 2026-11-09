# Session — Dimensionality Reduction (P1 L10 resume, CP2 sealed) — 2026-10-05

**Type:** teach (resume, `/pause` handoff written) · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Position after pause:** in-progress, paused at **Checkpoint 2/6 — CP2 fully sealed** (CP1 sealed 2026-09-30; CP2 minis 1–2 sealed 2026-10-02; mini 3 sealed 2026-10-03; checkpoint practice completed today as a paper walk). Resume **CP3 mini 1** (choosing k).

## What happened

- **Warm-up (quiz-audit PASS cycle 3; grade-audit agreed):** W1 fail — the 13.2 signed race gap filed under "float noise"; W2 pass D sure (`rowvar=True` default); W3 pass ("sum of squared deviations hence can never be negative").
- **W1 repair (diagnose-first):** learner self-located — B owned the 8.9e-16 magnitude gap, 13.2 is the signed gap = 2× biggest |coordinate| (mirror, not error). Isomorphic micro-check (biggest |coord| 10 ⇒ gap 20) ✓. Fact-check PASS 3/3.
- **Learner directive (durable):** the from-memory code write is **off the books entirely** — no code in chat AND none in their own environment as a learning-system task ("i will do that in my own time but not as part of the learning system"). CP2's practice re-shaped into a **paper walk** (quiz-audit PASS cycle 2 after a P4 answer-leak fix: P4 originally named the top eigenvector (1,1)/√2, leaking P2's axis).
- **Paper walk** (X rows (1,0),(5,2),(3,4), k=1; grade-audit agreed): P1 fail (mean + centered rows ✓, handed the 3×2 centered matrix as "C") · P2 fail (stalled) · P3 fail (Xc n×d ✓, Xp claimed d×k) · P4 pass.
- **Repairs:** hint re-anchored to the learner's own 09-30 exit-ticket words (entry = centered dot product ÷ (n−1)) → learner computed [[8/3,4/3],[4/3,8/3]] — dot products right, **÷n instead of ÷(n−1)** → C = [[4,2],[2,4]]; detector: denominator = one less than the rows summed (centering ate a degree of freedom). Fraction micro-check (12÷3) answered 2 → confession "any number of the minor diagonal is the variance" (off-diagonal/variance relapse) + kept fraction 1 − λ2/λ1 = 2/3 (top λ treated as the pie) → both repaired (diagonal = self-dots; pie = Σλ = trace ⇒ 6/8 = 3/4); micro-checks [[5,1],[1,3]] ✓ and (9,3 ⇒ 3/4) ✓. P3 self-repaired from one locating question: "rows hold data points, hence nxk" — which also sealed the owed **n==d edge** (shapes collide ⇒ check contents).
- **Pause exit ticket (quiz-audit PASS; grade-audit agreed 3/3, all `sure`):** X1 A (n−1) · X2 5/6 · X3 "check the contents it can hold".
- **Attempts (ops.py):** 16 PCA attempts today (fail W1; pass W2, W3, micro-check-20; fail P1/P2/P3; pass P4; fail C-÷n; fail MC-12÷3; pass P2-λ, P2-axis; fail kept-fraction; pass both micro-checks; pass P3-repair; pass exit ticket ×3) → **PCA mastery 1.00, interval_index 3, next_review 2026-11-04**.

## Handoff

- Lesson file updated (Status/Resume from + today's section): `Lessons/Lesson — Dimensionality Reduction — 2026-09-26.md`.
- Learning Record: `Learning Records/Learning Record — PCA CP2 Practice Repairs — 2026-10-05.md`.
- `Core/Pending Ingest.json`: partial, resume CP3 mini 1, mistakes[] carries 3 rows.
- CP3 elicitation question was posed (λ 4.59/0.16 kept-fraction prediction) but parked when the learner pivoted to the CP2 practice — re-elicit at CP3 open.
- Aged Scout digest (kept per partial-close rule) is now past TTL — re-scout before teaching CP3+ material that needs fresh sources (t-SNE/UMAP bodies still unconsumed).
