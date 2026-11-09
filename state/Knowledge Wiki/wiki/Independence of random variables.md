<!-- provenance: status=verified | source=https://en.wikipedia.org/wiki/Independence_(probability_theory) | verified-by=fact-check-agent | date=2026-10-26 -->

# Independence of random variables

Two random variables $X$ and $Y$ are **independent** when knowing the value of one gives you **no information** about the other.

This is not the same as "they can't occur together." Independence means the variables don't influence each other, not that they're mutually exclusive.

## Intuitive example

Flipping a coin ($X$) and rolling a die ($Y$): these are independent events that certainly *can* occur together. You can flip heads and roll a 3 at the same time. Independence just means the coin flip doesn't influence what the die shows.

If being tall ($X$) and being good at basketball ($Y$) were independent, then knowing someone is tall would tell you nothing about whether they're good at basketball.

## Equivalent definitions

When $X$ and $Y$ are independent, all three of these are true:

1. **Conditional equals marginal**:

   ```latex
   P(Y = y_j \mid X = x_i) = P(Y = y_j)
   ```

   Knowing $X$ doesn't change the probability of $Y$.

2. **Symmetric condition**:

   ```latex
   P(X = x_i \mid Y = y_j) = P(X = x_i)
   ```

   Knowing $Y$ doesn't change the probability of $X$.

3. **Joint factorizes**:

   ```latex
   P(X = x_i, Y = y_j) = P(X = x_i) \cdot P(Y = y_j)
   ```

   The joint probability is the product of the marginals.

## Common misconception

Independence does **not** mean:

- The variables can't occur together (that's mutual exclusivity)
- $P(Y \\mid X) = 0$ (that would mean they're incompatible)

It means the conditional probability equals the marginal probability — conditioning has no effect.

## Derivation from conditional probability

The independence test isn't an arbitrary formula — it's a direct algebraic consequence of the definition. Starting from the definition (conditional equals marginal):

```latex
P(Y = y_j \mid X = x_i) = P(Y = y_j)
```

Substitute the conditional probability formula $P(Y \\mid X) = \\frac{P(X, Y)}{P(X)}$:

```latex
\frac{P(X = x_i, Y = y_j)}{P(X = x_i)} = P(Y = y_j)
```

Multiply both sides by $P(X = x_i)$:

```latex
P(X = x_i, Y = y_j) = P(X = x_i) \cdot P(Y = y_j)
```

This is the factorization condition. It's not a separate idea — it's what independence *means* expressed in terms of joint and marginal probabilities.

**Symmetry**: The same derivation works in the other direction. Starting from $P(X \\mid Y) = P(X)$, you reach the identical factorization. The condition is symmetric, as it should be — independence between $X$ and $Y$ doesn't have a direction.

**Contingency table interpretation**: In a two-way table, conditioning on $X$ means dividing the cell count by the column total $c_i$. Conditioning on $Y$ means dividing by the row total $r_j$. If $X$ and $Y$ are independent, these conditional probabilities equal the corresponding marginals:

```latex
\frac{n_{ij}}{c_i} = \frac{r_j}{N} \quad \text{and} \quad \frac{n_{ij}}{r_j} = \frac{c_i}{N}
```

## Theoretical vs statistical independence

### Theoretical independence

In pure probability theory, independence is **binary and exact**. Two variables either satisfy $P(X, Y) = P(X) \\cdot P(Y)$ for every combination, or they don't. There's no "partially independent" — no gray area, no p-value, no "probably." The equation holds perfectly or it fails.

This definition applies to the **true underlying probability distribution**, which you almost never know in practice.

### Statistical independence testing

In practice, you work with **sample data**, not the true distribution. Even if two variables are truly independent in the population, random sampling variation means your observed frequencies will almost never satisfy the factorization condition exactly. The question becomes: is the deviation real, or just noise?

The **chi-square test of independence** answers this by asking:

> If the variables were truly independent, how likely is it that random chance alone would produce a deviation as large as (or larger than) what I observed?

You compare **observed frequencies** (your data) against **expected frequencies** (what you'd see under independence: $E\_{ij} = \\frac{r_j \\cdot c_i}{N}$). The chi-square statistic aggregates the squared differences across all cells. The **p-value** tells you how surprising your observed deviation is under the null hypothesis of independence.

| p-value | Interpretation |
| --- | --- |
| Small (&lt; 0.05) | The deviation is unlikely under independence — you **reject** the null and conclude the variables are dependent |
| Large (≥ 0.05) | The deviation could easily arise from random sampling — you **do not have sufficient evidence** to reject independence |

Crucially, a large p-value does **not** prove independence. It means your data don't provide strong enough evidence to conclude dependence. Absence of evidence ≠ evidence of absence.

### The key insight

Theoretical independence lives in the world of true probability distributions (usually unknown). Statistical testing lives in the world of finite samples and uncertainty. The p-value framework bridges the gap — it lets you distinguish between real dependence in the population and noise from sampling variation.

## In practice

Independence dramatically simplifies probability calculations. If variables are independent, the joint distribution factors cleanly, and you only need to reason about each variable separately.

## Related pages

- [[Joint, marginal, and conditional probabilities]]
- [[Probability mass and density functions]]
- [[Probability foundations]]
- [[Covariance and correlation]]

## Sources
- Wikipedia, "Independence (probability theory)": https://en.wikipedia.org/wiki/Independence_(probability_theory)
- Wikipedia, "Pearson's chi-squared test": https://en.wikipedia.org/wiki/Pearson%27s_chi-squared_test