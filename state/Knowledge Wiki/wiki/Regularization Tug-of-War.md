<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Regularization Tug-of-War

The total loss is a compromise between two competing forces:

```text
Total Loss = Data Loss (NLL) + Regularization Loss
```

**Data Loss (NLL):** Pulls weights UP. Wants sharp, confident distributions that fit the training data exactly. Alone → overfitting.

**Regularization Loss:** Pulls weights DOWN (toward zero). Wants flat, uniform distributions. Alone → W = 0 → uniform 1/27 distribution → NLL = -ln(1/27) ≈ **3.295**.

**The dial:** Regularization strength `c` controls which side wins:
- `c = 0`: Data loss dominates — overconfident, overfits
- `c = ∞`: Regularization dominates — W = 0 → uniform distribution → NLL = 3.295
- `c = optimal`: Balanced — ~2.47 for the bigram names dataset

**Key numbers for the bigram case:**
| c | W values | Distribution | NLL |
|---|---|---|---|
| 0 | Large | Sharp/peaked | → 0 on training data |
| Optimal | Moderate | Smooth | ~2.47 |
| ∞ | All zeros | Uniform (1/27) | ~3.295 |

Related: [[L2 Regularization as Smoothing]] | [[Negative Log-Likelihood (NLL)]] | [[Add-1 Smoothing]]

Part of: Socratic tutoring session on regularization and loss functions (Gemini)

## Sources (verified)

- https://github.com/karpathy/makemore
