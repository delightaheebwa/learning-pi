<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Optimizers (SGD, Adam, AdamW)

The optimizer decides *how* to update weights after computing gradients. Different optimizers behave very differently.

| Optimizer | How It Works | When to Use | Typical LR |
|-----------|-------------|-------------|-----------|
| **SGD** | `weight -= lr × gradient` — simplest. | Maximum control or well-tuned schedules | 0.01–0.1 |
| **SGD + Momentum** | Builds velocity in consistent directions (like a ball rolling downhill) | Better than plain SGD. Good for CNNs. | 0.01, momentum=0.9 |
| **Adam** | Adaptive learning rate per parameter. Combines momentum + RMSprop. | **The default choice.** Works well out of the box. | 0.001 |
| **AdamW** | Adam with *decoupled* weight decay. Better regularization. | Transformers, modern architectures. Preferred over Adam. | 0.001, weight_decay=0.01 |

## Practical Rule

Start with **Adam** (lr=0.001) — it works for most problems without tuning. Switch to **SGD with momentum** (lr=0.01, momentum=0.9) when you need the *best final accuracy* and can afford more tuning (its noise lands in flat minima that generalize better). Use **AdamW** for transformers. Always schedule runs longer than a few epochs.

> Superseded 2026-09-10 (Rohit P1 L08): the old rule below — "only switch to SGD to reproduce papers" — understated SGD+M, which is the go-to for best final accuracy, not just paper reproduction.

~~Only switch to SGD if you need to reproduce a paper's results (classic CNN papers use SGD+momentum).~~ See [[Optimizer Selection (Rohit heuristic)]].

## Sources

- **Lesson:** Marconi Lab DL — Day 3: Advanced Training & Sequence Models
- **Date learned:** 2026-07-15
- **Further reading:** [PyTorch Optimizers Docs](https://pytorch.org/docs/stable/optim.html)
- Adam paper (Kingma & Ba, 2014): https://arxiv.org/abs/1412.6980
- AdamW paper (Loshchilov & Hutter, 2017): https://arxiv.org/abs/1711.05101

## Connections

- Prerequisites: Training Loop Pattern, Gradient Descent
- Leads to: Regularization Techniques
