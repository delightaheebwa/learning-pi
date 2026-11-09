# 2026-05-22 — Independence test derivation and practical testing

## Source type
User notes (text)

## Raw content

The formula n_ij / c_i is for P(Y=y_j | X=x_i) — conditioning on X. Here:

- When you condition on X (a column), divide by the column total c_i
- When you condition on Y (a row), divide by the row total r_j

### Deriving the Test

Now substitute the independence condition into the conditional probability formula:

P(X=Café, Y=Pass) / P(X=Café) = P(Y=Pass)

Multiply both sides by P(X=Café):

P(X=Café, Y=Pass) = P(X=Café) · P(Y=Pass)

This is the independence test. The joint probability must equal the product of the marginals. The formula isn't arbitrary — it's a direct algebraic consequence of saying "learning one variable doesn't change the probability of the other".

### Theoretical Independence

This is the strict mathematical definition: two variables are independent if and only if P(X=x_i, Y=y_j) = P(X=x_i) · P(Y=y_j) for every possible combination. It's binary — the equation either holds exactly or it doesn't. No middle ground exists in the mathematical framework.

### Statistical Independence Testing

In practice, you're working with sample data, not the true underlying probability distribution. Even if two variables are truly independent in the population, random sampling variation means your observed frequencies will almost never match the expected frequencies perfectly.

Statistical tests like the chi-square test of independence address this by asking: "If the variables were truly independent, how likely is it that random chance alone would produce a deviation as large as (or larger than) what I observed?". The p-value quantifies this probability.

- Small p-value (typically < 0.05): The observed deviation is unlikely under independence, so you reject the null hypothesis and conclude the variables are dependent
- Large p-value: The deviation could easily arise from random sampling, so you don't have sufficient evidence to reject independence

### The Key Insight

Theoretical independence is about the true probability distribution (which you usually don't know), while statistical testing is about making decisions under uncertainty from limited sample data. The p-value framework lets you distinguish between "real dependence" and "noise from sampling".
