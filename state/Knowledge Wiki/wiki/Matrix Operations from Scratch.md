<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Matrix Operations from Scratch

> Every neural network is just matrix multiplication with extra steps.

**Source:** [ai-engineering-from-scratch Phase 01 — Vectors, Matrices & Operations](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/02-vectors-matrices-operations/docs/en.md)
**Ingested:** 2026-06-30

## Core Concepts

### Vectors and Matrices as Data Structures

A **vector** is an ordered list of numbers. In AI: data points, features, embeddings.
A **matrix** is a 2D grid (rows × columns). In AI: weight matrices transform input vectors into output vectors.

A layer with 784 inputs and 128 outputs → 128×784 weight matrix.

### Shape Rules (The Golden Rule of Matrix Multiplication)

Matrix multiplication: **(m×n) @ (n×p) = (m×p)** — the inner dimensions MUST match.

```
(128×784) @ (784×1) = (128×1)
 weights     input     output
```

A shape mismatch error in PyTorch? This is the reason.

### Operations Map

| Operation | What it does | Neural network use |
|-----------|-------------|-------------------|
| Addition | Element-wise combine | Adding bias to output |
| Scalar multiply | Scale every element | Learning rate × gradients |
| Matrix multiply | Transform vectors | Layer forward pass |
| Transpose | Flip rows and columns | Backpropagation |
| Determinant | Single number summary | Checking invertibility |
| Inverse | Undo a transformation | Solving linear systems |
| Identity | Do-nothing matrix | Initialization, residual connections |

### Element-wise vs Matrix Multiplication

**Element-wise (`*`):** multiply matching positions. Both matrices must be same shape.
```
|1 2| * |5 6| = |5  12|
|3 4|   |7 8|   |21 32|
```

**Matrix multiplication (`@`):** dot products of rows × columns. Inner dimensions must match.
```
|1 2| @ |5 6| = |1·5+2·7  1·6+2·8| = |19 22|
|3 4|   |7 8|   |3·5+4·7  3·6+4·8|   |43 50|
```

Different operations, different rules, different results.

### Broadcasting

When shapes don't match for an element-wise operation, broadcasting stretches the smaller array to fit by repeating along missing dimensions:

```
|1 2 3|          |10 20 30|     |11 22 33|
|4 5 6|    +     |10 20 30|  =  |14 25 36|
    ↑              ↑
 2×3 matrix     broadcast 1D vector (stretched across rows)
```

Every modern framework (NumPy, PyTorch, TensorFlow) does this automatically.

### Dense Layer Forward Pass

`output = relu(W @ x + b)` — the single dense layer:
1. **W @ x**: weight matrix × input vector (linear transformation)
2. **+ b**: bias added via broadcasting
3. **relu**: activation (clamp negatives to zero)

Every dense layer in every neural network does exactly this.

### Key Implementation Details

- **Determinant** (2×2): `ad - bc`. Zero → singular matrix (crushes dimension, no inverse)
- **Inverse** (2×2): `1/det × [[d, -b], [-c, a]]`. Only exists when det ≠ 0
- **Identity matrix**: 1s on diagonal, 0s elsewhere. Matrix equivalent of ×1
- **NumPy equivalents**: `np.array`, `A @ B` (matmul), `A.T` (transpose), `np.linalg.det`, `np.linalg.inv`, `np.eye` (identity), `np.maximum(0, x)` (ReLU)

### AI Connections

| Concept | Where it shows up |
|---------|------------------|
| Matrix multiply | Every NN layer forward pass |
| Broadcasting | Bias addition, batch norm |
| Transpose | Backpropagation (gradient flow) |
| Determinant/Inverse | Solvability, normal equations |
| Identity | Residual connections (ResNets), init |
| Element-wise | Activations, loss computation |

## Related

- [[Linear Algebra Intuition]] — theoretical foundation for these operations
- [[AI Engineering - Dev Environment Stack]] — NumPy environment setup
