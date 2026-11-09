<!-- provenance: status=verified | source=https://aclanthology.org/2022.sustainlp-1.11/ ; https://en.wiktionary.org/wiki/Appendix:Luganda_noun_classes ; https://linguistics.berkeley.edu/~hyman/Luganda_Word_Paper.pdf | verified-by=fact-check-agent | date=2026-10-26 -->

# African Language NLP

**Source:** Marconi Lab DL Course, Day 4

## The Core Challenge

Many African languages — including Luganda and the wider Bantu family — are **agglutinative**: they build words from many morphemes. "omulwadde" ("sick person") = class-1 person prefix **omu-** + the stem of **-lwala** ("to be sick") in its stative/perfect form. Word-level tokenization produces enormous vocabularies because each morpheme combination is a new word; studies report Luganda needing ~1.7–3.4× as many tokens as English with general-purpose tokenizers.

## Solutions

- **Subword tokenization** (BPE, SentencePiece) splits into meaningful chunks — usually the best balance for agglutinative languages
- **Character-level models** avoid the vocabulary explosion entirely (tiny vocab, but longer sequences)
- **Multilingual models** (mBERT, XLM-R, AfroLM) pre-trained on related languages (AfroLM covers 23 African languages and beats mBERT/XLM-R-base on NER, classification and sentiment)

## Lab NLP Projects

| Project | Architecture | Key Consideration |
|---|---|---|
| Luganda text classification | BiLSTM + embeddings | Character or subword tokens |
| Swahili sentiment analysis | BiLSTM + FastText embeddings | Pre-trained available |
| English→Luganda translation | Seq2Seq with attention | Transformers better |
| Clinical notes extraction | BiLSTM-CRF | NER for medical terms |

## Practical Advice

If pre-trained embeddings don't exist for your target language: train from scratch on available data, or use a multilingual model that has seen related languages. Don't abandon the project — the challenge is data, not architecture.

## Sources

- Wiktionary, "Appendix:Luganda noun classes" (class I `(o)mu-`; `-lwala` → `omulwadde`): https://en.wiktionary.org/wiki/Appendix:Luganda_noun_classes
- Hyman, "The word in Luganda" (rich agglutinative morphology, Narrow Bantu): https://linguistics.berkeley.edu/~hyman/Luganda_Word_Paper.pdf
- Dossou et al., "AfroLM: A Self-Active Learning-based Multilingual Pretrained Language Model for 23 African Languages" (SustaiNLP 2022): https://aclanthology.org/2022.sustainlp-1.11/ · https://arxiv.org/abs/2211.03263
- Luganda tokenizer-fertility measurements (1.7× vs English; 3.1–3.4 tokens/word for LLaMA-3/Gemma): https://huggingface.co/datasets/CraneAILabs/luganda-tokenizer-evaluation
- fastText pre-trained vectors, 157 languages incl. Swahili: https://fasttext.cc/docs/en/crawl-vectors.html
