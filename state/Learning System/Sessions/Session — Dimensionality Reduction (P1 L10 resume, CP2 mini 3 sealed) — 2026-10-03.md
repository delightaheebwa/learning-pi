# Session — Dimensionality Reduction (P1 L10 resume, CP2 mini 3 sealed) — 2026-10-03

**Type:** teaching (partial `/pause` handoff) · **Track:** AIEFS (AI Engineering from Scratch) · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP)
**Position:** paused at Checkpoint 2/6, mini 3/4 — CP1 fully sealed 2026-09-30; CP2 minis 1–3 sealed (1–2 on 2026-10-02, mini 3 today); next: CP2's single practice (re-shaped per the new no-code-in-chat preference), then CP3.

## Session Info

- **Date:** 2026-10-03
- **Topic:** CP2 mini 3 — assemble the full `MyPCA` class from scratch; race it against sklearn on a seeded synthetic cloud; sign-flip story sealed end to end
- **Prerequisites Reviewed:** CP2 mini 2 code pieces (eigh layout, slicing, projection) — warm-up recall
- **New Concepts Introduced:** implementation-vs-library equivalence (up to sign); variance-nonnegativity (PSD) reasoning

## What We Covered

- **Warm-up (verifier-agreed 3/3):** W1 D sure (eigh ascending, columns) · W2 B sure (`vecs[:, order[:k]]`, `Xp = Xc @ V`) · W3 pass-with-hunch — shape detector restated exactly; n=d edge flagged (both shapes d×d ⇒ inspect contents), isomorphic re-check owed. PCA 0.72, E&E 1.00.
- **Race elicitation:** learner predicted "answers will match" + "sklearn faster" — both half right; the sign-only axis flip was the third candidate, elicited from their own banked `C(-u)=λ(-u)` identity. Learner corrected their own "all of them" to: eigenvalue ranking sign-proof; axis + signed coordinates flip as a pair.
- **Class assembly:** taught line-by-line (per new preference, not chat-coded). Check-back (a)–(d): (a) ✗ — "np.cov by default treats columns as features" (default is rows-as-variables) → repaired in-turn; (b) ✓ d×k columns=directions; (c) ✓ both silent-failure consumers named; (d) ✓ compare magnitudes/variances, skip signed coordinates.
- **Race:** viz first (projected-variance curve; twin peaks 180° apart = sign freedom as geometry; heights fixed under tilt — viz-audit PASS, figure-value disclosure made). Then the real race (seed=3, n=200, cov [[4,2],[2,1.5]], k=1; verifier reproduced): explained 4.98024987 both arms; components exact sign flips; signed gap 13.2; magnitude gap 8.9e-16. Verdict: **tie up to sign**.
- **Learner-initiated pokes (both sealed):** (1) why 13.2 isn't a worry — signed diff = −2·skPC_i, so the gap is 2× the biggest coordinate = cloud's size, a label mirror, not information loss; caveat banked: restate sign-sensitive thresholds as |score|. (2) why variance can't be negative — sum of squared deviations; generalized to $u^\top C u$ ⇒ PSD ⇒ eigenvalues ≥ 0; learner's own consolidation: "a mere sign flip doesnt matter because of the square."
- **Exit ticket (grade-audit agreed 3/3, all sure):** X1 C · X2 B · X3 A — the (a) repair is confirmed stuck. PCA mastery 1.00.
- **New durable learner preference:** **no code written in chat** — code with conceptual insight is taught/walked by the Tutor; learners reason in prose; from-memory builds happen in the learner's own environment and arrive as artifacts/prose. Recorded in Learning Record + lesson resume pointer. CP2 practice re-shaped to match.

## Concepts Status After Session

| Concept | Previous Status | New Status | Mastery Type | Notes |
|---------|----------------|------------|--------------|-------|
| PCA (Dimensionality Reduction) | developing (mastery 0.50, recipe + code sealed) | **recipe + code fully sealed incl. race equivalence** (mini 3/4) | provisional → strong | mastery 1.00; implement-vs-library equivalence understood "up to sign"; practice (from-memory build) still pending |
| Eigenvalues & Eigenvectors | stable, definitional (1.00) | stable — touched only via the sign-invariance mapping | true | no new work needed |
| Variance & Covariance | warm (0.65) | reinforced — variance-nonnegativity + PSD reasoning sealed in learner's own words | provisional | no new attempts logged (reasoning came through PCA strand) |

## Demonstrations of Understanding

- **Concept:** sign-invariance split (eigenvalue ranking untouched; axis + signed coordinates flip together)
  - **Your confidence before evaluation:** built from "all of them" prediction, corrected on paper with the reflection identity
  - **Your explanation:** "eigenvalue ranking is what remains untouched. the pair that flip sign are the signed projected coordinates and the axis direction"
  - **Assistant evaluated:** Pass (highest Bloom: Analyze)
  - **Mastery type:** true_mastery
- **Concept:** race-readout interpretation (13.2 vs 8.9e-16)
  - **Your confidence before evaluation:** asked to elaborate — then sealed the distinction (13.2 = 2× biggest coordinate = cloud size/label mirror; 8.9e-16 = real-information difference)
  - **Your explanation:** exit ticket X1 C sure + the unprompted "13.2 is the size of the biggest label, not the size of a discrepancy" reading
  - **Assistant evaluated:** Pass (exit ticket X1)
  - **Mastery type:** provisional_mastery
- **Concept:** variance ≥ 0 (squared deviations), extended to PSD
  - **Your confidence before evaluation:** unsure ("why can variance never be negative")
  - **Your explanation:** "all its doing is summing squared deviations and a mere sign flip doesnt matter because of the square"
  - **Assistant evaluated:** Pass (exit ticket X2 B sure)
  - **Mastery type:** provisional_mastery

## Open Questions

- [ ] Carried: curse of dimensionality still rowless (probe Q2 "I don't know"; surfaces at CP3); round-cloud degenerate case (equal λ's) pocketed for CP3.
- [ ] W3 n=d edge: both shapes d×d ⇒ inspect array contents not just shape — isomorphic re-check owed (fold into CP2 practice).

## Gaps & Misconceptions

- [ ] (a) slip (reversed np.cov default) — failed in-session, repaired same turn, exit ticket X3 locked it. Watch for recurrence in the CP2 practice; Mistakes row only if it recurs.
- [ ] No new structural mistakes today. `[::-1]`/`[:-1]` collision re-checked clean via (c).

## Next Steps

- [ ] CP2 practice (re-shaped): learner writes the class from memory **in their own environment**, reports in prose/artifact; Tutor audits with the seeded race + line-by-line rubric (no chat-coding).
- [ ] CP3: choosing k (explained-variance ratio, elbow, reconstruction error = sum of dropped λ's); curse of dimensionality surfaces here; round-cloud degenerate case.
- [ ] CP4 t-SNE, CP5 UMAP, CP6 kernel PCA + method-choice map, final quiz + Feynman.

## Verification summary (this session)

- quiz-audit: warm-up (PASS) · race elicitation fact-check (PASS) · exit ticket cycle 1 ISSUES (correct = longest 3/3; positions 2,2,0) → cycle 2 PASS.
- grade-audit: warm-up W1/W2 pass + W3 pass (agrees) · line-by-line a fail / b/c/d pass (agrees) · exit ticket X1/X2/X3 pass (agrees).
- fact-check: race-prediction turn (3/3 after 1 ISSUES fix on sign-vs-magnitude wording) · race-results turn (4/4, verifier reproduced all numbers in /tmp/raceenv) · 13.2 elaboration (2 ISSUES → corrected re-dispatch PASS: 2×-coordinate arithmetic + reconstruction-invariance fix) · variance-nonnegativity (2/2 PASS) · hint turn (sign-reflection method-only, 2/2 PASS).
- viz + viz-audit: race figure PASS (first dispatch).
- Attempts logged (ops.py): PCA pass→fail→pass×3 (0.72 → 0.45 → 0.65 → 0.90 → 1.00) · E&E pass (1.00).

## Assistant's Summary

CP2 mini 3 is sealed: the learner audited the assembled class line-by-line (one slip on the np.cov default, repaired and exit-ticket-locked), then read a real seeded race against sklearn correctly — tie up to sign — and produced the session's best Bloom moment by mapping sign-invariance themselves from the reflection identity. Two learner-initiated pokes (13.2 unpacking, variance-nonnegativity) both sealed in their own words. A durable workflow preference landed: no code written in chat (code is taught, not typed by the learner). Attempts honest in ops.py; handoff written with partial:true, resume pointer = CP2 practice (re-shaped). Position: CP2 3/4 minis sealed; CP3 next after the practice.
