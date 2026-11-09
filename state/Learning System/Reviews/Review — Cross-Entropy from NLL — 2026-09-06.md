# Review — Cross-Entropy from NLL — 2026-09-06

- **Concept:** Cross-Entropy from NLL
- **Type:** concept
- **Track:** AIEFS
- **Question type:** discriminative (alternated from definitional)
- **Question:** Which statement about CE loss is TRUE? (A–D)
- **Answer given:** C (fixed penalty)
- **Correct answer:** B (reduces to −log(ŷ_correct) for one-hot; gradient is softmax(z) − y)
- **Result:** FAIL
- **Error type:** structural — thought CE applies fixed penalty; inverted the −log mechanism (said it "keeps values small" when it actually amplifies small probabilities into large penalties)
- **Feynman:** FAIL — "measures bad confidence" (vague), "−log keeps values small" (inverted mechanism)
- **Mastery:** 0.00 (advisory)
- **Next review:** 2026-09-09
