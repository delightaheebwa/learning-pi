<!-- provenance: status=verified | source=https://www.deeplearningbook.org/contents/mlp.html ; https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html | verified-by=fact-check-agent | date=2026-10-26 -->

# Activation Functions

Without activations, stacking linear layers collapses into one big linear function — no matter how deep. Activation functions introduce **non-linearity**, the source of neural networks' representational power.

## Common Functions

| Function | Output Range | Use Case |
|----------|-------------|----------|
| **ReLU** | `[0, ∞)` | Hidden layers — default for CNNs/MLPs |
| **Sigmoid** | `(0, 1)` | Binary output (disease probability) |
| **Softmax** | `(0, 1)`, sums to 1 | Multi-class output (which disease?) |

- ReLU is a standard hidden-layer default for CNNs/MLPs; transformer blocks typically use GELU or SwiGLU instead, so "default across almost all architectures" overstates it
- Sigmoid squashes to a probability for binary decisions
- Softmax converts logits to a probability distribution over C classes
- **Critical:** Do NOT put softmax in `forward()` when using `nn.CrossEntropyLoss()` — it takes **logits** and applies `log_softmax` + NLL internally (equivalent to softmax followed by NLL)

## Source
- **Lesson:** Marconi Lab DL — Day 1: Tensors, Neural Networks & the Training Loop
- **Date learned:** 2026-07-14
- **Further reading:** [Goodfellow §6.3 "Hidden Units"](https://www.deeplearningbook.org/contents/mlp.html)

## Sources

- Goodfellow, Bengio & Courville, *Deep Learning*, ch. 6: https://www.deeplearningbook.org/contents/mlp.html
- PyTorch `nn.CrossEntropyLoss` (input = unnormalized logits; combines `log_softmax` and `nll_loss`): https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
- PyTorch source (`loss.py` docstring confirms logits input): https://github.com/pytorch/pytorch/blob/main/torch/nn/modules/loss.py

## Connections
- Prerequisites: PyTorch Model Building
