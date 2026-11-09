<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Recurrent Neural Networks (RNNs)

All models so far process one fixed-size input → one output. RNNs handle **sequences**: time-series, text, audio, video. They process one element at a time, maintaining a **hidden state** that carries information from previous steps.

## The Problem with Basic RNNs

Basic RNNs suffer from vanishing gradients **through time** — information from 20+ steps ago is essentially lost. This makes them useless for long sequences (e.g., predicting rainfall from 365 days of data).

## Where RNNs Are Used (Marconi Lab)

- **Climate:** Predict rainfall from 30 years of daily temperature, humidity, pressure sequences
- **Ecology:** Model forest growth or animal migration from time-series sensor data
- **Health:** Predict patient deterioration from ICU vital sign streams
- **Multi-modal:** Combine ultrasound images + patient vitals in one model

## Sources

- **Lesson:** Marconi Lab DL — Day 3: Advanced Training & Sequence Models
- **Date learned:** 2026-07-15
- **Further reading:** [PyTorch RNN Tutorial](https://pytorch.org/tutorials/intermediate/char_rnn_classification_tutorial.html)
- https://pytorch.org/tutorials/intermediate/char_rnn_classification_tutorial.html
- https://colah.github.io/posts/2015-08-Understanding-LSTMs/

## Connections

- Prerequisites: Training Loop Pattern
- Leads to: LSTM (Long Short-Term Memory)
