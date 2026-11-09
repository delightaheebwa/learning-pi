<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Word Embeddings (nn.Embedding)

**Source:** Marconi Lab DL Course, Day 4

## What It Is

A learnable lookup table that maps each word ID to a dense vector (e.g., 100 numbers). Similar words end up with similar vectors after training.

## The Problem It Solves

Integer IDs (1, 2, 3…) are meaningless to a neural network — ID 5 is not "more than" ID 3. Embeddings give words a meaningful representational space.

```python
embedding = nn.Embedding(vocab_size=5000, embedding_dim=100)
word_ids = torch.tensor([[1, 2, 3, 0, 0]])  # batch, padded
vectors = embedding(word_ids)                 # shape: [1, 5, 100]
```

## How Embeddings Learn

Initialized randomly. During training, backpropagation updates them so words appearing in similar contexts end up close together. "omusujja" (fever) and "omulwadde" (patient) drift close because they co-occur in medical texts.

## Key Facts

- `num_embeddings` = vocabulary size (rows in lookup table)
- `embedding_dim` = vector size per word (typical: 100-300)
- `padding_idx=0` zeroes out gradient for `<PAD>` tokens
- Backprop updates these vectors like any other parameter

## Sources
- https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html
