# Review — API Key Security

**Date:** 2026-06-25
**Concept:** API Key Security
**Status:** Developing (kept interval)

## Retrieval Performance

**Question:** Explain the universal API pattern and the difference between using an SDK vs raw HTTP. When would you prefer one over the other?

**Result:** Close — missed the API key as a distinct component of the universal pattern (said it's just a URL). SDK vs raw HTTP comparison was correct.

## Correction

Universal API pattern = **endpoint + API key + request + response**. The key is the auth piece that identifies you — without it, you're just making a generic URL call.

## Next Review: 2026-06-28
