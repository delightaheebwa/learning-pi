# Review — Bits vs Nats — 2026-11-04

- **Track/Source:** aiefs — Rohit P1 L09 + PyTorch CrossEntropyLoss (Python)
- **Type:** memory (Active Concepts) / `concept` (Attempts.json — drift surfaced, not fixed) · **Q type:** `discriminative`
- **Why this slot:** scheduled due review — `Attempts.json` `next_review` 2026-10-24 on the 2026-11-04 session date; the row also carries the open Perplexity-adjacent history (the 2026-09-24 nats-base-on-bits slip).
- **Question:** the verbatim prompt text was **not carried in the handoff envelope** — recorded as a handoff gap, not reconstructed. The envelope carried the item type, the learner's verbatim answer and the graded gap quoted under *Why*.
- **Learner answer (verbatim):** "cross entropy is lower for team B because the model's prediction that team B got was closer to the data than that of team A. so the operation to be done to lower the cross entropy is simply tune the model's predictions to more closely align with reality."
- **Verdict:** **FAIL — confidence `hunch`, 0 hints, miss_class `cue` (grade-audit agreed).**
- **Why:** the item's target was the log base as a **unit** (3.32 bits = 2.30 nats, factor 1/ln 2); the answer addressed a different question — why cross-entropy is lower, and model tuning as the lever — so the base-conversion step never appeared. Graded gap, verbatim: "missed log-base-as-unit: 3.32 bits = 2.30 nats, factor 1/ln2; settling operation is base conversion not model tuning".
- **Surfaced drift (not fixed):** this row is `memory` here and in the queue digest but `concept` in `Attempts.json`, so the attempt took the concept ladder (+14d → 2026-11-18) where the memory ladder gives +3d → 2026-11-07. Same class of drift surfaced at the 2026-10-05 review; correcting the stored type is an ingest-path decision, not this write.
- **Attempts.json:** one attempt recorded 2026-11-04 — `fail` (`discriminative`, `hunch`, hints 0). Net state: mastery **0.50** advisory, `interval_index` 3 → **2**, `consecutive_correct` 2 → **0**, `consecutive_wrong` 0 → **1**, `last_reviewed` 2026-09-24 → **2026-11-04**, `next_review` 2026-10-24 → **2026-11-18** (concept ladder, +14d), Feynman flag unchanged (`—`; the envelope carried no explain-back result for this item).
- **Mistakes ledger:** **one new row** dated 2026-11-04 — `structural` / `[miss: cue]` / `active` / retries 0 / next retry 2026-11-18. No pre-existing Bits vs Nats ledger row existed to patch.
- **Active Concepts:** row synced — `last_reviewed` 2026-09-24 → **2026-11-04**; `next_review` 2026-10-24 → **2026-11-18**; `Last Q Type` definitional → **discriminative**; mastery 0.50 advisory noted.
- **Advisory mastery:** **0.50** — Feynman: —.
- **Carry-forward:** base-as-unit drill — the 3.32 bits / 2.30 nats pair and the question "which operation settles it: base conversion, not model tuning".
