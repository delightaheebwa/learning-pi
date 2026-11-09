# Session — Dimensionality Reduction (P1 L10, probe + CP1 mini 1, paused) — 2026-09-26

New lesson from a fresh Scout digest (fetched 2026-09-25, first-fetch baseline, no drift check possible — no prior hash; no failed refs). Paused after CP1 mini 1 per the pause protocol.

## Prior (step 0 hypothesis → probe outcome)

| Strand | Hypothesis | Probe outcome |
|---|---|---|
| Eigenvalues & eigenvectors | expand (neutral; touched via Momentum/Saddle rows) | **solid** — Q1 pass sure |
| Variance & covariance | expand (wiki-exposed only) | **unstable** — Q3 pass, Q4 orthogonality slip |
| Projection / change of basis | expand | **solid** — Q5 pass sure |
| Perplexity | reframe (fuzzy; name collision ahead) | **recovering** — Q6 pass sure; Q7 elicit vague-but-warm |
| KL divergence | skip-fast (solid, 10 consecutive) | **solid** — Q8 pass sure |
| PMF vs PDF | reframe (failed 09-24 review) | **unstable** — Q9 fail sure (label slip), Q10 mechanism intact |
| Curse of dimensionality | new | **unknown** — Q2 "I don't know" |

## Flow

1. **Probe** (10 items, quiz-audit gated, withheld feedback): 7/9 — details in lesson file. Q4 slip ("after centering the features are orthogonal") repaired in-session by the learner's own elicit prediction (cm/inches off-diagonal stays large ≠ zero). Q9 regression: PMF picked for exact continuous heights, but Q10 stated the integrate-over-intervals mechanism correctly — label slip under pressure, not structural.
2. **CP1 mini 1** (elicit → consolidate, fact-check 5/5): centering ≠ decorrelation; covariance entries as centered dot products; PCA's goal = diagonalize (new basis, not feature editing); Shlens two-goals framing (redundancy + variance ranking) matched to the learner's own "distinct information" phrasing.
3. **Exit ticket** (quiz-audit PASS_WITH_FLAGS lows-only; grade-audit agreed 3/3): E1 B, E2 A, E3 own-words pass ("all centering does is ensure the center is the data's center; pca finds the unique directions that together tell the whole story").

## Position

- **Paused at CP1 mini 2/2** — resume: where the new directions come from ($Av=\lambda v$ on the covariance), then CP1 practice → CP2 (5-step recipe, Python).
- Attempts this session: Eigenvalues & Eigenvectors pass · Variance & Covariance fail→pass · Perplexity pass · KL Divergence pass · PMF vs PDF fail.

## Handoff notes for Clerk

- Mistakes: (1) **Variance & Covariance** — structural slip "features become orthogonal after centering" (probe Q4, hunch; repaired in-session via learner's own elicit prediction; exit ticket 3/3 — candidate for review-flow confirmation). (2) **PMF vs PDF** — regression recurrence (probe Q9, sure; PDF/PMF label inverted while the integrate-over-intervals mechanism stated correctly in Q10) — existing row/mistake thread, needs review-flow retest.
- Scout digest may be swept by TTL before resume (gitignored, 7-day TTL) — lesson file carries source hashes + raw-file paths; re-fetch only if drift is suspected.
- No wiki pages written (Tutor does not write wiki); concepts for CP1 live under the existing Variance & Covariance row.
