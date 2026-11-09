# Review — Curse of dimensionality — 2026-10-10

- **Track/Source:** aiefs — Rohit P1 L10 + Scout synthesis
- **Type:** concept · **Q type:** discriminative (MCQ) + the mandatory Feynman explain-back
- **Why this slot:** due review (Attempts.json `next_review` 2026-10-10, no prior graded attempts — `interval_index` 0) — one of the three scheduled reviews in the deterministic queue (digest `review-01a126e4-8923-7272-af26-c75a307b5737-aiefs.json`, used verbatim). Question type per the digest: `discriminative`.
- **Question 1 (discriminative MCQ):** as `d` grows, what happens to pairwise distances? **(A)** distances become more alike — the relative contrast collapses toward 1.
- **Learner answer:** "A"
- **Verdict:** **PASS** — graded mechanically with `ops.py grade-mcq --key A --answers A`; grade-audit agreed. Why: A is the concentration effect — nearest and farthest neighbours become nearly equidistant.
- **Question 2 — Feynman explain-back (mandatory beat for a `concept` row, P1.1):** explain the curse of dimensionality in your own words, with an example. Learner: distances become the same length as features grow; kNN depends on distance **rankings**, so neighbourhoods lose meaning; concrete example — 3 distinct clusters merge into 1 at high `d`. → **PASS**, **`feynman_pass`** (grade-audit agreed).
- **Repair note (not a fail):** kNN is a classifier/regressor, not clustering — the distance-ranking mechanism wrecks both.
- **Attempts.json:** two attempts recorded 2026-10-10 — `pass` (discriminative, `sure`, hints 0) then `pass` (explain-back, `sure`, hints 0, Feynman pass). Net state: mastery **0.80** advisory, `interval_index` 0 → **3** (two consecutive passes), `next_review` 2026-10-10 → **2026-11-09** (concept +30d), `consecutive_correct` **2**, Feynman **pass**.
- **Mistakes ledger:** none — a `pass` never opens a row; the concept has no open row.
- **Active Concepts:** row synced — `last_reviewed` 2026-10-07 → **2026-10-10**; `next_review` 2026-10-10 → **2026-11-09**; `Last Q Type` definitional → **discriminative**; mastery noted.
- **Advisory mastery:** **0.80** — Feynman: `pass`.
- **Carry-forward:** the concentration reading now holds on both a discriminative item and an own-words explain-back; the kNN-≠-clustering distinction is the one wording to keep clean.
