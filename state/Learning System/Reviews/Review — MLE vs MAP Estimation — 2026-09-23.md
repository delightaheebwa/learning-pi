# Review — MLE vs MAP Estimation — 2026-09-23

- **Track/Source:** aiefs — Rohit P1 L07 + lesson 2026-09-05 (Python)
- **Type:** concept · Q type: definitional
- **Why this slot:** due review (next_review 2026-09-22) + TWO active mistake rows (2026-09-14, 2026-09-19, retries 0) targeting exactly this item
- **Question:** The posterior is proportional to likelihood × prior, so MAP maximizes likelihood × prior. Which prior yields an L2 penalty and which yields an L1 — and what feature of each log-density produces that shape?
- **Expected:** Gaussian → L2 (log-prior ∝ −θ², squared); Laplace → L1 (log-prior ∝ −|θ|, absolute).
- **Learner answer:** "gaussian yields an L2 penalty while laplace yields an L1 penalty. for L2 the mean squared gives that shape while for L1, the absolute mean produces that shape."
- **Verdict:** ✅ pass (grade-audit agreed) — mapping right AND, for the first time, the rationale's core feature (squared vs absolute) correct.
- **Attempts.json:** mastery 0.56, interval_index 1, next_review 2026-09-30, Feynman: fail
- **Mistakes ledger:** both rows → `review` (retries 0 → 1, next retry 2026-09-30); a second consecutive correct graduates them.
- **Feynman:** ❌ fail — the explain-back reused the A/B slip ("yesterday's posterior becomes today's prior" = sequential updating, not MAP-vs-MLE). Grade-audit agreed. Repair delivered same session: MAP when data is scarce/noisy or genuine prior knowledge exists (3 heads/3 flips: MLE θ=1.0, MAP under Beta(2,2) = posterior **mode** 4/5 = 0.8 — note 5/7 ≈ 0.71 is the posterior *mean*, an error in my own earlier message, corrected); prior-as-belief ⇒ penalty = −log p(θ), so the shape follows the log-density (Gaussian → squared, Laplace → absolute). Fact-check PASS (6/6 claims).
