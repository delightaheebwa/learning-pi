# Review — Naive Bayes — 2026-09-24

- **Track/Source:** aiefs — Phase 1 L07 notes
- **Type:** concept · **Q type:** discriminative
- **Why this slot:** due review; the Naive Bayes misconception row was due 2026-09-23.
- **Question:** State the conditional-independence assumption, explain why correlated features can make scores overconfident, and distinguish ranking from calibrated probabilities using spam.
- **Learner answer:** "the conditional independence assumption is that it assumes all the probabilites are independent of each other. correlated features make it over confident because the posterior grows with larger confidence numbers. reliable class ranking is what naive bayes does whereby above a certain confidence, an email can be classified as spam and below as not spam but for calibrated probabilites, it demands more specificity and exactness which naive bayes stuglles with given its conditional independence assumption"
- **Verdict:** FAIL — grade-audit agreed. The answer used unconditional independence, misstated the duplicate-evidence multiplication mechanism, and confused ranking with thresholded confidence and calibration.
- **Attempts.json:** mastery 0.19, interval_index 0, next_review 2026-09-28, Feynman: fail
- **Mistakes ledger:** Naive Bayes row remains `active`, retries 0, next retry 2026-09-28.
- **Repair target:** features are independent conditional on the class; correlated features are nevertheless multiplied as independent evidence, which can overconcentrate the posterior; ranking can be useful while probabilities are poorly calibrated.
