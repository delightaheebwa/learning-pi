# Review — aie Track — 2026-07-23

5 concepts reviewed.

| Concept | Status | Next Review |
|---|---|---|
| Gradient Checking | developing → developing | 2026-07-30 |
| Neural Network Training Loop | developing → developing | 2026-07-30 |
| Micrograd Architecture | developing → developing | 2026-07-26 |
| Numerical vs Analytical Derivatives | developing → developing | 2026-08-06 |
| Gradient Descent from Scratch | developing → developing | 2026-07-26 |

**Notes:**
- Gradient Checking: nailed formula (central difference), clarified relative error threshold
- Neural Network Training Loop: update first, zero after — correct
- Micrograd Architecture: forgot Layer class in the chain; corrected: MLP → Layer → Neuron → Value
- Numerical vs Analytical: swapped speed tradeoff; corrected: analytical is fast (autodiff), numerical is slow (O(n²))
- Gradient Descent from Scratch: update formula was slightly off; correct: `param.data -= lr * param.grad`
