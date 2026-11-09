# Review — Information Content (Surprise) — 2026-10-11

- **Track/Source:** aiefs — Rohit P1 L09 + Olah (Python)
- **Type:** concept · **Q type:** definitional + transfer-far (MCQ) + the mandatory Feynman explain-back
- **Why this slot:** due review (Attempts.json `next_review` 2026-10-11) — the only due item in the deterministic queue (digest `review-01a12c35-01a3-7351-afbb-c44b5722fe3b-aiefs.json`, used verbatim; `due_mistakes` 0, `due_reviews` 1, `warnings: []`). Question type per the digest: `definitional`. Prereq check: no recorded prerequisite edge → not blocked.
- **Question 1 (definitional):** what is the information content (surprise) of an event x with probability p(x)? Write the formula and explain what the minus sign is doing there.
- **Learner answer:** "−log_2(p(x)). the minus sign is to cancel out the current negative sign since surprise can't be negative."
- **Verdict:** **PASS** (grade-audit agreed). Why: I(x) = −log₂ p(x) with the minus flipping the sign — raw log p ≤ 0 for p ∈ (0,1], so −log p ≥ 0 (large for rare events).
- **Question 2 (transfer-far, MCQ):** E1 p=0.5, E2 p=0.01, log base 2 — how much surprise does E2 carry (rounded), and which event carries more? (A) ~6.6 bits and E2 carries more · (B) ~6.6 bits and E1 carries more · (C) ~1 bit and E2 carries more · (D) ~0.01 bits and E2 carries more.
- **Learner answer:** "A"
- **Verdict:** **PASS** — graded mechanically with `ops.py grade-mcq --key A --answers A`; grade-audit agreed. Why: −log₂ 0.01 ≈ 6.64 bits, and the rarer event E2 carries more surprise.
- **Question 3 — Feynman explain-back (mandatory beat for a `concept` row, P1.1):** learner: "information content refers to how much you are "surprised" when you see the real probability of an event happening. minus log is to cancel out the negative sign since surprise cant be negative. surprise differs from probability in that we apply log base 2 to probability e.g for the outcome of a football game, if surprise = 0, it means the event is deterministic/the team was always going to win the game no matter what hence you arent "surprised" when it occurs." → **PASS**, **`feynman_pass`** (grade-audit agreed).
- **Reviewer note (not a fail):** a minor wording imprecision — surprise attaches to the event *occurring*, not to "seeing the probability"; the football example (certainty ⇒ surprise 0) carried the rubric.
- **Attempts.json:** three attempts recorded 2026-10-11 — `pass` (definitional, hints 0), `pass` (transfer-far, hints 0) then `pass` (explain-back, hints 0, Feynman pass). No confidence tag on any item. Net state: mastery **1.00** advisory, `interval_index` 3 (already at the concept cap, so the 30d ladder holds) → `next_review` 2026-10-11 → **2026-11-10**, `consecutive_correct` **5**, Feynman **pass**.
- **Mistakes ledger:** none — no `fail` this session; the concept has no open row (never failed).
- **Active Concepts:** row synced — `last_reviewed` 2026-09-11 → **2026-10-11**; `next_review` 2026-10-11 → **2026-11-10**; `Last Q Type` discriminative → **transfer-far**.
- **Advisory mastery:** **1.00** — Feynman: `pass`.
- **Carry-forward:** all three halves hold under retrieval — the formula + minus-sign rationale, the rare-event magnitude on fresh numbers, and the own-words explain-back; the only wording to keep clean is that surprise belongs to the event occurring.
