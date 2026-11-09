# Lesson — Bayes' Theorem & Statistical Thinking — 2026-09-05

- **Track:** aiefs · Phase 1, Lesson 07 (Rohit) · Python
- **Source:** Rohit P1 L07 `docs/en.md` + Further Reading (3Blue1Brown, Stanford CS229, Think Bayes, scikit-learn)
- **Status:** done (taught 2026-09-02, re-activated 2026-09-05)

## Arc

base rate fallacy → Bayes' theorem derivation → Naive Bayes + Laplace smoothing → MLE vs MAP → conjugate priors (Beta-Binomial) → sequential Bayesian updating → Bayesian A/B testing.

## Key results

- Base-rate concept climbed from 2 misconceptions (likelihood-heavy "99%", prior-heavy "10%") to a clean, self-checked counting-table computation (P(A|defective) = 4/7; P(child|card) = 4/22).
- Feynman explain-back passed; "prior" named as the forgotten term behind the base-rate fallacy.
- Build: from-scratch Naive Bayes (log-space + Laplace smoothing), mapped to sklearn `MultinomialNB` + `CountVectorizer`.
- MLE vs MAP = regularization connection (Gaussian prior = L2; Laplace prior = L1).

## Evidence

- Probe: Q1 fail → re-probe fail → guided factory (method solid, 1 units slip) → cardholder (clean table, showed intermediate 18/4/22).
- End-of-lesson quiz: 4/6 solid (Q1, Q3, Q4, Q5), 2 corrected via re-probe (Q1 base-rate re-probe; Q6 early-stopping rationale).
- Free recall: both solid (NB miscalibration vs ranking; Laplace denominator normalization).
