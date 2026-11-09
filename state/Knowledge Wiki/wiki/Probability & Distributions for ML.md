<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Probability & Distributions for ML

> **Source:** AI Engineering from Scratch, Phase 1, Lesson 06 — Probability & Distributions
> **Prerequisites:** Linear algebra, calculus, gradients
> **Connections:** Every ML model outputs probability distributions; every loss function measures distribution distance

---

## The Three Axioms of Probability

Everything in probability follows from 3 rules over a **sample space** $S$ (all possible outcomes):

1. $P(A) \geq 0$ — probabilities are never negative
2. $P(S) = 1$ — something always happens
3. $P(A \cup B) = P(A) + P(B)$ when $A \cap B = \varnothing$ — add probabilities for mutually exclusive events

These three axioms generate Bayes' theorem, expectations, distributions, and the Central Limit Theorem.

---

## Conditional Probability & Bayes' Theorem

$P(A \mid B) = P(A \cap B) / P(B)$ — the probability of $A$ given $B$ happened.

**Bayes' theorem** inverts the condition:

$$P(A \mid B) = \frac{P(B \mid A) \cdot P(A)}{P(B)}$$

This is how models go from "how likely is this image given the class" (likelihood) to "how likely is this class given the image" (posterior). Bayesian ML is built on this.

---

## PMF vs PDF

| | PMF (Discrete) | PDF (Continuous) |
|---|---|---|
| Values | Exact probabilities per outcome | Density (integrate over interval) |
| Sum/Integral | Sums to 1 | Integrates to 1 |
| Can exceed 1? | No | Yes (it's a density) |
| ML example | Softmax output (classification) | VAE latent space |

---

## Common Distributions & ML Roles

| Distribution | Formula | ML Use |
|---|---|---|
| **Bernoulli** | $P(1)=p, P(0)=1-p$ | Binary classification (sigmoid) |
| **Categorical** | $P(i)=p_i, \sum p_i=1$ | Multi-class classification (softmax) |
| **Uniform** | $f(x) = 1/(b-a)$ | Random init, Monte Carlo |
| **Normal (Gaussian)** | $f(x)=\frac{1}{\sigma\sqrt{2\pi}}e^{-(x-\mu)^2/2\sigma^2}$ | Weight init, gradient noise, VAE, diffusion |
| **Poisson** | $P(k)=\lambda^k e^{-\lambda}/k!$ | Event counts (hospital admissions, click rates) |

**68-95-99.7 rule:** 68% within $1\sigma$, 95% within $2\sigma$, 99.7% within $3\sigma$ of a normal.

---

## Expected Value & Variance

**Expected value** = probability-weighted average:

- Discrete: $\mathbb{E}[X] = \sum x_i P(X=x_i)$
- Continuous: $\mathbb{E}[X] = \int x f(x) dx$

The loss function is an expected value — average loss over the data distribution.

**Variance** = spread around the mean:

$\text{Var}(X) = \mathbb{E}[(X - \mathbb{E}[X])^2] = \mathbb{E}[X^2] - (\mathbb{E}[X])^2$

High variance in gradients = noisy, unstable training.

---

## Joint & Marginal Distributions

$P(X, Y)$ describes two variables together. **Marginalization** recovers one variable:

$P(X = x) = \sum_y P(X = x, Y = y)$

Independence: $P(A \mid B) = P(A)$ iff $P(A \cap B) = P(A) \cdot P(B)$.

---

## Central Limit Theorem

**The most important result in statistics:** The sum/average of many independent random variables converges to a normal distribution, **regardless** of the source distribution.

- 1 die → uniform; avg of 30 dice → near-perfect bell curve
- Works for any starting distribution (exponential, Bernoulli, etc.)

**Why it matters in ML:**
- Measurement errors are approximately normal
- Gradient noise in SGD is approximately normal
- Weight init uses normal distributions (Kaiming, Xavier)
- Normal = maximum entropy distribution for given mean/variance

---

## Log Probabilities & Numerical Stability

Multiplying many small probabilities **underflows to zero** after ~30 terms in float32:

$\log P(\text{sequence}) = \log P(w_1) + \log P(w_2) + \cdots$

- Turns multiplications into additions (stable)
- Log probabilities are always ≤ 0 (more negative = less likely)
- **Cross-entropy loss = negative log probability of the correct class**
- Language models on 50K+ token vocabularies cannot function without log-space

---

## Softmax & Cross-Entropy

**Softmax** converts raw logits to probabilities:

$\text{softmax}(z_i) = e^{z_i} / \sum_j e^{z_j}$

**Numerical stability trick:** subtract max logit before exponentiating. $\exp(1000)$ overflows to inf; $\exp(z_i - \max(z))$ keeps all exponents ≤ 0.

**Cross-entropy** measures distance between distributions:

$H(p, q) = -\sum_i p_i \log(q_i)$

With one-hot labels, this collapses to $\text{Loss} = -\log(q_{\text{correct}})$ — the negative log-likelihood of the correct class.

---

## Implementation (Pure Python)

Key functions from scratch (no NumPy): `softmax`, `log_softmax`, `cross_entropy_loss`, `normal_pdf`, `bernoulli_pmf`, `categorical_pmf`, `expected_value`, `variance`, `sample_bernoulli`, `sample_normal_box_muller`.

See `Knowledge Wiki/wiki/Probability foundations` and `Knowledge Wiki/wiki/Probability mass and density functions` for additional details.

---

## See Also

- [[Probability foundations]] — beginner-friendly verbal overview
- [[Probability mass and density functions]] — detailed PMF/PDF
- [[Probability Mass Function (PMF)]]
- [[Bernoulli Distribution]]
- [[Categorical Distribution]]
- [[Bayes rule]]
- [[Gaussian distribution]]
- [[Joint, marginal, and conditional probabilities]]
- [[Cumulative distribution function]]

## Sources

- https://en.wikipedia.org/wiki/Probability
- https://en.wikipedia.org/wiki/Central_limit_theorem
