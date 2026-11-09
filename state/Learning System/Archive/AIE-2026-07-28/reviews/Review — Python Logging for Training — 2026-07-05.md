# Review — Python Logging for Training
**Date:** 2026-07-05
**Track:** AI Engineering (aie)
**Interval:** 3d → 3d (kept)

## Result: ❌ Key details wrong — Kept at 3d

**Prompt:** What makes Python's logging module better than print() for training runs? Give me the key features and a minimal config that writes both to console and a file.

**Response:**
- Logging gives more detail than print() ✅
- Severity levels (error, etc.) ✅
- Console via console.log ❌ (should be StreamHandler())
- File via log() ❌ (should be FileHandler())

**Evaluation:** Understands the *why* but the *how* (handler names, basicConfig syntax) was still off. Keeping current interval.

**Next review:** 2026-07-08
