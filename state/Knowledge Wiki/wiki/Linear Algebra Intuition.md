<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Linear Algebra Intuition

> Every AI model is just matrix math wearing a fancy hat.

**Source:** [ai-engineering-from-scratch Phase 01 — Linear Algebra Intuition](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/01-linear-algebra-intuition/docs/en.md)
**Ingested:** 2026-06-27

## Core Concepts

### Vectors Are Points (and Directions)

A vector is a list of numbers representing coordinates in space. In AI, vectors represent everything — words (768-number embedding vectors), images (millions of pixel values), users (preference vectors).

- Magnitude: $\\sqrt{x_1^2 + x_2^2 + \\dots + x_n^2}$
- A vector points from the origin to its coordinates

### Matrices Are Transformations

A matrix transforms one vector into another — it can rotate, scale, stretch, or project. In AI, matrices ARE the model:

- Neural network weights → matrices that transform input into output
- Attention scores → matrices that decide what to focus on
- Embeddings → matrices that map words to vectors

### Dot Product (Similarity Measure)

$$a \\cdot b = a_1 \\times b_1 + a_2 \\times b_2 + \\dots + a_n \\times b_n$$

- Same direction: $a \\cdot b &gt; 0$ (similar)
- Perpendicular: $a \\cdot b = 0$ (unrelated)
- Opposite direction: $a \\cdot b &lt; 0$ (dissimilar)

This is how search engines, recommendation systems, and RAG work — find vectors with high dot products (or cosine similarity, the normalized dot product).

### Linear Independence

Vectors are linearly independent if no vector in the set can be written as a combination (scalar multiples + sums) of the others. If they're dependent, the space they span collapses to fewer dimensions.

**AI relevance:** Feature matrices should have linearly independent columns. Perfectly correlated features cause multicollinearity — the weight matrix becomes unstable, small input changes produce wild output swings, and normal equations become singular.

### Basis and Rank

A **basis** is a minimal set of linearly independent vectors that span the entire space. The number of basis vectors is the dimension. The standard basis for 3D is ${\[1,0,0\], \[0,1,0\], \[0,0,1\]}$.

**Rank** = number of linearly independent columns = number of linearly independent rows.

| Situation | What it means for ML |
| --- | --- |
| Full rank | Unique least-squares solution exists. Model is well-conditioned. |
| Rank deficient | Features are redundant. Infinitely many weight solutions. Regularization needed. |
| Rank 1 | All data lies on a line. Every column is a scaled copy of one vector. |
| Near rank-deficient | Matrix is ill-conditioned. Tiny input noise → large output changes. Use SVD truncation or ridge regression. |

### Projection

Projecting vector $a$ onto vector $b$ gives the component of $a$ in the direction of $b$:

$$\\text{proj}\_b(a) = \\frac{a \\cdot b}{b \\cdot b} \\cdot b$$

The residual $(a - \\text{proj}\_b(a))$ is perpendicular to $b$. This orthogonal decomposition is the foundation of least-squares fitting.

**AI applications:** Linear regression (solution IS a projection onto column space), PCA (project onto directions of max variance), Attention in transformers (projections of queries onto keys).

### Gram-Schmidt Process

Converts any set of independent vectors into an orthonormal basis (every vector length 1, every pair perpendicular):

1. Normalize the first vector
2. Subtract its projection onto the first vector, then normalize
3. Subtract projections onto all previous vectors, then normalize
4. Repeat

### QR Decomposition

QR decomposition factors a matrix into $Q$ (orthonormal basis from Gram-Schmidt) and $R$ (upper triangular matrix of projection coefficients). Used in solving linear systems (more stable than Gaussian elimination), eigenvalue computation (QR algorithm), and least-squares regression.

## AI Connections

| Concept | Where it shows up |
| --- | --- |
| Dot product | Attention scores in transformers, cosine similarity in RAG |
| Matrix multiply | Every neural network layer |
| Linear independence | Feature selection, avoiding multicollinearity |
| Rank | LoRA (low-rank adaptation), solvability |
| Projection | Linear regression, PCA |
| Gram-Schmidt / QR | Numerical solvers, eigenvalue computation |
| Orthonormal basis | Whitening transforms, stable computation |

**LoRA:** Fine-tunes LLMs by decomposing weight updates into low-rank matrices. Instead of updating a 4096×4096 matrix (16M params), LoRA updates two matrices of size 4096×16 and 16×4096 (131K params). The rank-16 constraint assumes the weight update lives in a 16-dimensional subspace.
## Sources

- https://en.wikipedia.org/wiki/Linear_algebra
- https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/01-linear-algebra-intuition/docs/en.md
