# Probability foundations: PMF, PDF, Bayes, covariance, Gaussian, and modeling limits

## Source

User note:

> A PMF assigns probabilities to the discrete states of a random variable and these probabilities sum to 1; this is what we use for discrete or categorical variables. A PDF is the analogous object for continuous variables: probabilities are given by areas under the density curve over intervals, computed via integration, and the probability at an exact point is effectively zero, so only ranges matter. The sum rule lets us obtain marginal distributions from a joint distribution by summing or integrating over the other variables, while the product rule lets us factor a joint distribution into a marginal and a conditional. Bayes’ rule states that the posterior probability of a hypothesis given data is proportional to the likelihood of the data under that hypothesis times the prior probability of the hypothesis. Covariance measures how two random variables vary together, and correlation is the scaled version of covariance that is always between −1 and 1. The Gaussian distribution belongs to the exponential family and has convenient closure properties under sums and linear transformations, which makes it very useful in probabilistic modeling. Conjugate Gaussian priors and likelihoods keep the posterior Gaussian, giving closed‑form Bayesian updates. In realistic ML problems we rarely achieve perfect performance because data are noisy and sometimes mislabeled, the world is complex and partly unpredictable, and our models are only imperfect approximations of the true data‑generating process.

## Extracted ideas

- PMFs describe discrete probability mass and must sum to 1.
- PDFs describe continuous density; probabilities come from interval areas, not exact points.
- Marginalization comes from summing or integrating out variables from a joint distribution.
- Product rules factor a joint into marginal and conditional parts.
- Bayes' rule turns likelihood and prior into a posterior.
- Covariance measures co-variation; correlation rescales it to a fixed range.
- Gaussian distributions are especially useful because of closure and conjugacy.
- Real ML models are limited by noise, label errors, and model mismatch.
