<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Transfer Learning for Text

**Source:** Marconi Lab DL Course, Day 4

## What It Is

Same idea as transfer learning for images: use pre-trained word embeddings (GloVe, FastText) to initialize the `nn.Embedding` layer instead of random vectors.

## Available Pre-trained Embeddings

- **GloVe:** trained on web text, good general-purpose English embeddings
- **FastText:** handles subword information — especially good for morphologically rich languages. Supports Swahili but may be limited for Luganda, Runyankole, Acholi

## How to Load Them

```python
def load_pretrained_embeddings(embedding_layer, path, vocab):
    pretrained = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            pretrained[parts[0]] = torch.tensor([float(x) for x in parts[1:]])

    with torch.no_grad():
        for word, idx in vocab.items():
            if word in pretrained:
                embedding_layer.weight[idx] = pretrained[word]

    embedding_layer.weight.requires_grad = False  # freeze, like image transfer
```

## The African Language Gap

Pre-trained embeddings exist for Swahili (FastText) but are limited for Luganda, Runyankole, Acholi. For these, either train embeddings from scratch on available corpora, or use multilingual models (mBERT, XLM-R, AfroLM) that cover related languages.

## Sources

- GloVe project: https://nlp.stanford.edu/projects/glove/
- FastText: https://fasttext.cc/
- Hugging Face — Transformers (mBERT/XLM-R): https://huggingface.co/docs/transformers
