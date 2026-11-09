<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# BiLSTM Text Classifier

**Source:** Marconi Lab DL Course, Day 4

## What It Is

An LSTM trained on text: feed word embeddings through a bidirectional LSTM, take the last hidden state, and classify.

## Architecture

```
Input text → Embedding → BiLSTM → Concatenate last hidden states → Dropout → FC → Class logits
```

```python
class LugandaTextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=2,
                           batch_first=True, bidirectional=True, dropout=0.3)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)  # ×2 for bidirectional
        self.dropout = nn.Dropout(0.5)
```

## Bidirectional = Two LSTMs

One reads left→right, another reads right→left. The concatenated output captures context from both sides — critical for classification where the whole sentence is available. Final state: `torch.cat((hidden[-2], hidden[-1]), dim=1)`.

## Lab Applications

- Classify SMS health alerts (malaria outbreak vs vaccination reminder)
- Categorize radio transcripts (agricultural advisory vs health education)
- Sort social media posts (crop disease report vs market prices)

## Sources

- PyTorch `nn.LSTM` (bidirectional): https://pytorch.org/docs/stable/generated/torch.nn.LSTM.html
- PyTorch sequence models tutorial: https://pytorch.org/tutorials/beginner/nlp/sequence_models_tutorial.html
