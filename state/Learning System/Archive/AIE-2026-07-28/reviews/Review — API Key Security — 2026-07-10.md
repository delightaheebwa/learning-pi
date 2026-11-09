# Review — API Key Security — 2026-07-10

**Concept:** API Key Security  
**Date:** 2026-07-10  
**Result:** Advanced (7d → 14d)

**Question:** Where do you store API keys and why? One sentence.

**Response:** In an `.env` file, added to `.gitignore` so they aren't pushed to GitHub — prevents misuse at the developer's expense.

**Evaluation:** Fully correct. Solid on the `.env` + `.gitignore` pattern and the rationale (sensitive credentials, GitHub exposure, cost/security risk).

**New Interval:** 14d — next review 2026-07-24
