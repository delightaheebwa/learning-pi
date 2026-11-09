<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Text Tokenization

**Source:** Marconi Lab DL Course, Day 4

## What It Is

The first step in making text understandable to machines: splitting text into tokens (words, subwords, or characters) and mapping each to an integer ID.

## Three Levels

- **Word-level:** `text.split()` → simple, but produces huge vocabularies for agglutinative languages
- **Subword-level** (BPE, SentencePiece): splits into meaningful chunks like "omu"+"lwadde" — best balance for morphologically rich languages
- **Character-level:** tiny vocabulary (~50-200 chars), can generate any word, but sequences are ~6× longer

## Vocabulary Building

- Each unique token gets an integer ID
- `<PAD>` (0) = padding to make sequences same length for batching
- `<UNK>` = unknown words not seen during training
- Sequences must be padded to equal length using `pad_sequence` with `padding_value=0`

## Key Code

```python
tokens = text.lower().split()
vocab = {word: i+1 for i, word in enumerate(set(tokens))}
ids = [vocab.get(token, vocab['<UNK>']) for token in tokens]
padded = pad_sequence([torch.tensor(ids)], batch_first=True, padding_value=0)
```

## Why It Matters for African Languages

Luganda is **agglutinative** — "omulwadde" = "omu" (person) + "lwadde" (sick). Word-level tokenization explodes the vocabulary. Subword or character-level is usually better.

## Sources

- PyTorch docs — `pad_sequence`: https://pytorch.org/docs/stable/generated/torch.nn.utils.rnn.pad_sequence.html
- Hugging Face — Tokenizers: https://huggingface.co/docs/tokenizers/en/index
