# Session — Dimensionality Reduction (P1 L10 resume, CP2 minis 1–2 sealed) — 2026-10-02

**Type:** teaching (partial `/pause` handoff) · **Track:** AIEFS (AI Engineering from Scratch) · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP)
**Position:** paused at Checkpoint 2/6, mini 2/4 — CP1 fully sealed 2026-09-30; CP2 minis 1–2 sealed today; CP2 mini 3 (assemble the full PCA class + compare vs sklearn) not started.

## Session Info

- **Date:** 2026-10-02
- **Topic:** CP2 — the 5-step from-scratch PCA recipe (recipe overview + why each step exists; the NumPy code piece by piece)
- **Prerequisites Reviewed:** Variance & Covariance, Eigenvalues & Eigenvectors (CP1 material — warm-up recall)
- **New Concepts Introduced:** PCA (Dimensionality Reduction) — the recipe itself

## What We Covered

- **Warm-up (graded, verifier-agreed):** W2 pass — λ=0 ⇒ pure line through the origin, PCA drops the empty axis with zero loss. W1 fail first pass ("variances **for each feature**"; rejected "correlation" as "more computation steps") → self-located repair pass: variance is measured **along the new perpendicular eigenvector directions**, and correlation needs the **square-root/std-dev normalization**.
- **CP2 mini 1 — recipe overview (sealed):** canonical 5 steps **center → covariance → eigenvectors → sort by λ → project** and the why of each. Learner's prediction had center-first right and "describe C in the eigenbasis" as the last move; fixes folded in: the **eigenvectors** (not the λ's) are the axes; **sort by λ** (the step their prediction skipped) makes "top-k" defined; **projection rewrites the data points**, not C (C-diagonalization is the sibling result).
- **CP2 mini 2 — the code (sealed in three pieces):**
  - **Cov call:** learner predicted `np.cov(X.T)` + transpose-again + "n×d" shape → guided to $d\times d$ and symmetric-no-op; consolidated `C = np.cov(Xc, rowvar=False)` (or `np.cov(Xc.T)`), $n$ only inside entries via $1/(n-1)$.
  - **eigh line:** learner got ascending `0, 10`, column-2 = big axis, top-1 = last eigenvector (2×1); generalization fixed to $d\times k$ (not $d\times d/2$); idiom `vals, vecs = np.linalg.eigh(C)` → `order = vals.argsort()[::-1]` → `V = vecs[:, order[:k]]`; keep `vals[order[:k]]` for CP3.
  - **Projection + sign:** toy projections $\sqrt5$ and $-\sqrt5$ (notation repair: minus **outside** the radical — detector: a real projection can only carry a sign); sign reflection invariance ($C(-u)=10(-u)$; sklearn `svd_flip` cosmetic); `Xp = Xc @ V` ($n\times k$) — learner confirmed.
- **Pause exit ticket (quiz-audit PASS cycle 2; grade-audit agreed):** X1 **B** ✓ (recipe order) · X2 **C** ✓ (`rowvar=False`) · X3 ✗ fail — `vals.argsort()[:, :-1]` instead of `[::-1]`, "`vecs` is n×d" (it is $d\times d$), "rows of vecs are the projected points" (points live in `Xc`/`Xp`; rows are component slots). Locate stalled ("I'm not sure") → repair told directly, sealed with the **shape detector** (shape has $n$ ⇒ points possible; all-$d$ ⇒ directions only).

## Concepts Status After Session

| Concept | Previous Status | New Status | Mastery Type | Notes |
|---------|----------------|------------|--------------|-------|
| Variance & Covariance | definitional (CP1 sealed 2026-10-01; X3 label slip reverted row to active) | warm-up repaired, definitional | provisional | pass→fail→pass today (mastery 0.65, interval 3); eigenbasis diagonal = λ's = variance along each eigenvector direction now intact |
| Eigenvalues & Eigenvectors | definitional (mastery 1.00 since 2026-10-01) | stable, definitional | true | warm-up λ=0 recall clean; no new work |
| PCA (Dimensionality Reduction) | not a row yet (new today) | developing — recipe-level, code sealed through projection | pending | recipe + code through `Xp = Xc @ V` sealed; full-class assembly + sklearn compare and the from-memory practice remain (CP2 mini 3 + practice) |

## Demonstrations of Understanding

- **Concept:** PCA recipe (5 steps)
  - **Your confidence before evaluation:** confident
  - **Your explanation:** exit ticket X1 = B (center → covariance → eigenvectors → sort by λ → project)
  - **Assistant evaluated:** Pass (grade-audit agreed)
  - **Mastery type:** provisional_mastery
- **Concept:** `np.cov` idiom (features-as-variables, d×d)
  - **Your confidence before evaluation:** confident
  - **Your explanation:** exit ticket X2 = C (`np.cov(Xc, rowvar=False)`)
  - **Assistant evaluated:** Pass (grade-audit agreed)
  - **Mastery type:** provisional_mastery
- **Concept:** eigh output handling (sort + slice + sign)
  - **Your confidence before evaluation:** uncertain
  - **Your explanation:** X3 — got the second line + d×k + sign-invariance; slipped on `[:, :-1]` vs `[::-1]`, called `vecs` n×d, and mapped its rows to data points
  - **Assistant evaluated:** Needs review (fail, grade-audit agreed) — repaired with the shape detector; sealed
  - **Mastery type:** pending_mastery

## Open Questions

- [ ] None raised today. Carried: `Curse of dimensionality` still rowless (probe Q2 "I don't know" — expected to surface at CP2–CP3); round-cloud degenerate case (equal λ's) pocketed for CP3.

## Gaps & Misconceptions

- [ ] Data-layout ↔ eigenvector-layout mapping confusion: claimed `vecs` is n×d and its rows are projected points (`vecs` is $d\times d$; rows are component slots; points live only in `Xc`/`Xp`) — Mistakes row candidate (structural), in the handoff `mistakes[]`.
- [ ] `[::-1]` (reversal) vs `[:-1]` (selection/drop) collision — sharpened in-session; watch for it in the CP2 practice.

## Next Steps

- [ ] CP2 mini 3: assemble the full PCA class from scratch on synthetic data; compare vs sklearn.
- [ ] CP2 practice (checkpoint's single practice): write the class from memory.
- [ ] Then CP3 (choosing k), CP4 (t-SNE), CP5 (UMAP), CP6 (kernel PCA + method-choice map), final quiz + Feynman.

## Verification summary (this session)

- quiz-audit: warm-up batch (PASS) · recipe-overview elicitation (PASS after 2× 503 provider failures → fallback model `deepseek-v4.1-flash`) · `np.cov` elicitation (PASS) · eigh elicitation (PASS) · projection/sign elicitation (PASS) · exit ticket (cycle 1 ISSUES — X2 had two numerically-correct options; fixed to exactly-one-correct → cycle 2 PASS).
- grade-audit: warm-up W1 fail / W2 pass (agrees:true) · W1 repair pass (agrees:true) · exit ticket X1 pass / X2 pass / X3 fail (agrees:true) .
- fact-check: recipe-overview consolidation 4/4 PASS (draft initially emitted once without the tag — re-verified with corrected toy `vecs` column labels after verifier ISSUES) · `np.cov` guiding question (PASS) · `np.cov` consolidation (PASS) · eigh/slicing consolidation (PASS) · projection/sign consolidation (PASS) · X3 seal (PASS after ISSUES → corrected draft).

## Assistant's Summary

CP2 is two-thirds taught: the learner can now recite and justify the 5-step recipe, write the cov/eigh/sort/slice/project lines, and reason about eigenvector sign ambiguity — verified by a verifier-agreed exit ticket on X1/X2. The one new frailty is the eigh-output layout mapping (a Mistakes row candidate, structural). Attempts logged via ops.py for all three concepts; handoff written with `partial:true` and resume pointer **CP2 mini 3**; Scout digest kept; lesson stays `in-progress`.
