<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# LSTM (Long Short-Term Memory)

**LSTM** networks solve the vanishing gradient problem of basic RNNs with **gates** — learned mechanisms that decide what to *remember* and what to *forget*. LSTMs are the workhorse of sequence modeling.

## Architecture

```python
class WeatherLSTM(nn.Module):
    """Predict tomorrow's rainfall from the past 30 days of weather data."""
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,    # features per timestep (temp, humidity, pressure…)
            hidden_size=hidden_size,  # LSTM memory size
            num_layers=num_layers,    # stack multiple LSTMs
            batch_first=True          # input: [batch, seq_len, features]
        )
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # x shape: [batch, 30 days, 5 weather features]
        lstm_out, (hidden, cell) = self.lstm(x)
        last_output = lstm_out[:, -1, :]  # [batch, hidden_size]
        return self.fc(last_output)       # [batch, 1] — predicted rainfall
```

## LSTM vs GRU

| | LSTM | GRU (Gated Recurrent Unit) |
|---|------|---------------------------|
| Gates | 3 (input, forget, output) | 2 (reset, update) — simpler |
| Parameters | More | ~25% fewer |
| When to use | Default choice for sequences | Smaller datasets, faster training |
| PyTorch | `nn.LSTM(...)` | `nn.GRU(...)` — identical API |

**batch_first=True** is critical — without it, LSTM expects `[seq_len, batch, features]`, which is awkward with DataLoader's `[batch, seq_len, features]` output.

## Sources

- **Lesson:** Marconi Lab DL — Day 3: Advanced Training & Sequence Models
- **Date learned:** 2026-07-15
- **Further reading:** [Understanding LSTM Networks](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) (Colah's blog)
- https://pytorch.org/docs/stable/generated/torch.nn.LSTM.html
- https://pytorch.org/docs/stable/generated/torch.nn.GRU.html

## Connections

- Prerequisites: Recurrent Neural Networks (RNNs)
- Relates to: Multi-Input / Multi-Modal Models
