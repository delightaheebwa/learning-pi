# Review — Cross-Entropy from NLL — 2026-09-23

- **Track/Source:** aiefs — Rohit P1 L06 + P1 L09 + Olah + PyTorch CrossEntropyLoss (Python)
- **Type:** concept · Q type: computational (prior: discriminative)
- **Why this slot:** due mistake (2026-09-11 row, `review`, retry 1 — the −log sign / CE-vs-KL structural error; a second correct graduates it)
- **Question:** Work on paper, reply with just the final number in bits: truth Q = (0.6, 0.4), your model says P = (0.5, 0.5). Compute the lesson's H(P,Q) — truth-weighted cross-entropy, log base 2. (quiz-audit cycle 2 fixed the letter-order ambiguity in the stem)
- **Expected:** −Σ Q log₂ P = 1.000 bits exactly.
- **Learner answer:** "1 bit"
- **Verdict:** ✅ pass (grade-audit agreed) — exact; no sign flip; the 09-11 structural error did not recur.
- **Attempts.json:** mastery 1.00, interval_index 3, consecutive_correct 6, next_review 2026-10-23
- **Mistakes ledger:** 2026-09-11 row → `graduated` (retries 2)
- **Note:** paper accommodation works — final-number-only math validates the formula without typing LaTeX.
