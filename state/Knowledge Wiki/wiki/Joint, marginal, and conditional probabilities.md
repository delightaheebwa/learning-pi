<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Joint, marginal, and conditional probabilities

When working with two (or more) random variables, three types of probability describe different aspects of their relationship. Example 6.2 from MML illustrates them with a probability table of two discrete variables $X$ and $Y$.

## Joint probability

The **joint probability** $P(X = x_i, Y = y_j)$ is the probability that both events occur together:

```latex
P(X = x_i, Y = y_j) = \frac{n_{ij}}{N}
```

where $n\_{ij}$ is the count in cell $(i, j)$ and $N$ is the grand total.

## Marginal probability

The **marginal probability** of one variable is obtained by summing (or integrating) out the other variable — "marginalizing it out."

For $Y$: sum across the **row**:

```latex
P(Y = y_j) = \frac{r_j}{N} = \frac{\sum_{i=1}^m n_{ij}}{N}
```

For $X$: sum down the **column**:

```latex
P(X = x_i) = \frac{c_i}{N} = \frac{\sum_{j=1}^n n_{ij}}{N}
```

where $r_j$ is the row sum (total for $Y = y_j$) and $c_i$ is the column sum (total for $X = x_i$).

**Memory aid**: rows go with $Y$, columns go with $X$. To marginalize out $X$, sum across the row. To marginalize out $Y$, sum down the column.

## Conditional probability

The **conditional probability** $P(Y = y_j \\mid X = x_i)$ answers: "Given that $X = x_i$ has occurred, what's the probability of $Y = y_j$?"

```latex
P(Y = y_j \mid X = x_i) = \frac{n_{ij}}{c_i}
```

Key insight: you divide by $c_i$ (the column total), not $N$ (the grand total). The conditioning on $X = x_i$ **restricts the universe** to only the cases in that column.

## Row/column symmetry in conditioning

The direction of conditioning determines what you divide by:

| Conditioning on... | Formula | Divide by... |
| --- | --- | --- |
| $X$ (given column) | $P(Y = y_j \\mid X = x_i) = \\frac{n\_{ij}}{c_i}$ | Column total $c_i$ |
| $Y$ (given row) | $P(X = x_i \\mid Y = y_j) = \\frac{n\_{ij}}{r_j}$ | Row total $r_j$ |

**Memory aid**: you restrict the universe to the row or column you're conditioning on. If you're told "$X = x_i$", you look only at that column — so you divide by the column total. If you're told "$Y = y_j$", you look only at that row — so you divide by the row total.

Note that these two conditional probabilities are generally **not** equal: $P(Y \\mid X) \\neq P(X \\mid Y)$. They coincide only in special cases, and when they both equal their respective marginals, the variables are [[Independence of random variables|independent]].

## From discrete to continuous

The same ideas work for continuous variables, with sums replaced by integrals:

- **Marginal**: $f_X(x) = \\int f\_{X,Y}(x, y) , dy$
- **Conditional**: $f\_{Y \\mid X}(y \\mid x) = \\frac{f\_{X,Y}(x, y)}{f_X(x)}$

## Relationship to probability rules

Marginalization is the **sum rule** in action. The conditional probability formula is the **product rule** rearranged:

```latex
P(X, Y) = P(Y \mid X) \, P(X) \quad \text{so} \quad P(Y \mid X) = \frac{P(X, Y)}{P(X)}
```

## Related pages

- [[Probability mass and density functions]]
- [[Independence of random variables]]
- [[Bayes rule]]
- [[Probability foundations]]
- [[Cumulative distribution function]]
## Sources

- https://en.wikipedia.org/wiki/Marginal_distribution
- https://en.wikipedia.org/wiki/Conditional_probability
