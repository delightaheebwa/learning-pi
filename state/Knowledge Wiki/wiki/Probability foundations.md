<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Probability foundations

This page is a beginner-friendly verbal overview of the probability ideas in `raw/sources/2026-05-16 - probability-foundations-pmf-pdf-bayes-covariance-gaussian.md`.

## Plausibility and probability

A useful philosophical way to read probability is through the Cox-Jaynes view: if you represent degrees of plausibility with real numbers and require them to behave consistently, the rules that result are essentially the usual rules of probability. That means probability is not just a bag of formulas; it is a coherent way to represent and update belief under uncertainty.

## The big picture

Probability is the language we use to talk about uncertainty with numbers. A random variable turns an uncertain outcome into a number, and a probability distribution tells you how that number is spread across the possible values. Once you have that setup, you can summarize it, combine probabilities, update beliefs, and build machine-learning models from it.

## 1. Random variables and distributions

A random variable is just a way to assign numbers to uncertain outcomes. The distribution tells you which values are likely and which values are rare.

If you want a plain-English version:

- the random variable is the thing you are measuring
- the distribution is the pattern of possibilities around it

## 2. PMFs and PDFs

There are two main ways to describe probabilities depending on whether the variable is discrete or continuous.

- A **PMF** assigns probability mass to discrete states, and all the masses add up to 1.
- A **PDF** is the continuous analogue: probabilities come from areas under the curve over intervals, computed by integration.
- For a continuous variable, the probability of one exact point is effectively zero, so only ranges matter.

## 3. Basic probability rules

The sum rule and product rule are the basic tools for working with probabilities.

- The **sum rule** lets you get a marginal distribution from a joint distribution by summing or integrating out the other variables.
- The **product rule** lets you factor a joint distribution into a marginal and a conditional.
- These rules are the bookkeeping layer underneath almost everything else.

## 4. Bayes' rule

Bayes' rule says that the posterior probability of a hypothesis given data is proportional to the likelihood times the prior.

In words:

- **prior** = what you believed before seeing the data
- **likelihood** = how well the data fit the hypothesis
- **posterior** = your updated belief after seeing the data

That is the core update rule for Bayesian reasoning.

## 5. Summary statistics and independence

A whole distribution can be compressed into a few numbers.

- The **mean** tells you the center.
- The **variance** tells you how spread out the values are.
- **Independence** means one variable does not tell you anything about another, which makes probability much easier to work with.

## 6. Covariance and correlation

Covariance measures how two random variables vary together.

- Positive covariance means they tend to move in the same direction.
- Negative covariance means they tend to move in opposite directions.
- Correlation is the scaled version of covariance, so it always lies between −1 and 1.

## 7. Important example distributions

The mind map highlights a few especially useful distributions:

- **Bernoulli**: binary outcomes like 0/1, success/failure
- **Gaussian**: bell-shaped continuous values
- **Beta**: values between 0 and 1, often used for probabilities

These are important because they show up everywhere and often make calculations manageable. Bernoulli and Beta are a classic Bayesian pair.

## 8. Gaussian distributions and conjugacy

The Gaussian distribution is especially useful because it belongs to the exponential family and behaves nicely under many transformations.

- Sums of Gaussian variables are still Gaussian.
- Linear transformations of Gaussian variables are still Gaussian.
- If you pair a Gaussian prior with a Gaussian likelihood, the posterior stays Gaussian.

That last point is called **conjugacy**, and it gives closed-form Bayesian updates.

## 9. Why this matters for machine learning

All of this is groundwork for later ML ideas such as regression, dimensionality reduction, and density estimation.

Real-world ML is never perfect because:

- data are noisy
- labels can be wrong
- the world is complicated and partly unpredictable
- models are only approximations of the true data-generating process

So the story is:

1. turn uncertainty into numbers
2. describe the numbers with distributions
3. combine and update probabilities
4. compress distributions with summaries
5. use the resulting tools to build models

That is the core message of the mind map.

## Related pages

- [[Probability mass and density functions]]
- [[Bayes rule]]
- [[Covariance and correlation]]
- [[Gaussian distribution]]
- [[Gradient descent]]
- [[Hessian matrix]]
- [[Jacobian matrix]]
- [[Total differential]]
- [[Cox-Jaynes view]]
- [[Random variable]]

## Sources

- https://en.wikipedia.org/wiki/Probability
- Cox, R. T. "Probability, Frequency and Reasonable Expectation" — https://bayes.wustl.edu/etj/articles/probability.pdf
