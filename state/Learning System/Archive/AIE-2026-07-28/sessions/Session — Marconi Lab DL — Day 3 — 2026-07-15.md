# Session — Marconi Lab DL — Day 3 — 2026-07-15

**Date:** 2026-07-15
**Topic:** Marconi Lab Deep Learning Course — Day 3: Advanced Training Techniques & Sequence Models
**Action:** Ingest

## Concepts Added

| Concept | Status | Next Review | Wiki Page |
|---|---|---|---|
| Vanishing & Exploding Gradients | developing | 2026-07-18 | [[Vanishing & Exploding Gradients]] |
| Optimizers (SGD, Adam, AdamW) | developing | 2026-07-19 | [[Optimizers (SGD, Adam, AdamW)]] |
| Regularization Techniques | developing | 2026-07-20 | [[Regularization Techniques]] |
| Recurrent Neural Networks (RNNs) | developing | 2026-07-18 | [[Recurrent Neural Networks (RNNs)]] |
| LSTM (Long Short-Term Memory) | developing | 2026-07-19 | [[LSTM (Long Short-Term Memory)]] |
| Multi-Input & Multi-Modal Models | developing | 2026-07-20 | [[Multi-Input & Multi-Modal Models]] |

## Source

Marconi Lab Deep Learning Course, Day 3 — HTML lesson file (`day-3-advanced-training-and-rnns.html`)

## Key Topics Covered

1. **Why Deep Networks Fail to Train** — vanishing gradients (sigmoid/tanh → zero gradient at early layers), exploding gradients (compounded large weights → NaN loss)
2. **Standard Training Toolkit** — ReLU activation, Batch Normalization, Kaiming/Xavier weight initialization, gradient clipping (clip_grad_norm_)
3. **Optimizers** — SGD, SGD+Momentum, Adam (default), AdamW (preferred for Transformers)
4. **Regularization** — Dropout, Weight Decay (L2), Early Stopping (patience pattern), Data Augmentation
5. **Recurrent Neural Networks** — sequence processing, hidden state, vanishing gradients through time
6. **LSTM** — input/forget/output gates, cell state, batch_first=True, GRU comparison
7. **Multi-Input Multi-Modal Models** — separate feature extraction pathways per modality → concatenate → classify

## Lab Projects Referenced

- Climate forecasting: LSTM on 30 days weather → next day's rainfall
- Ecological monitoring: LSTM/GRU on daily sensor readings → vegetation health
- Patient monitoring: LSTM + multi-modal on vitals + patient data → deterioration risk
- Crop growth: LSTM on weather + soil + satellite NDVI → yield prediction
- Multi-modal diagnosis: CNN on Pap smear image + linear net on patient tabular data → cervical cancer diagnosis

## Open Questions

- None currently

## Mastery Effect

- **Concepts added:** 6
- **Track:** aie
- **Next reviews start:** 2026-07-18
