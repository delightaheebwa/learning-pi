# Review — Adam (adaptive moments) — 2026-10-10

- **Track/Source:** aiefs — Rohit P1 L08 + Kingma & Ba 2015 + Ruder + handwritten notes 2026-09-08 (Python)
- **Type:** procedure · **Q type:** definitional (free recall; priority-1 mistake retry)
- **Why this slot:** priority-1 due mistake — the 2026-09-26 and 2026-10-03 ledger rows (both `active`, retries 0, next retry 2026-10-10) carried the concept into the deterministic queue (digest `review-01a126e4-8923-7272-af26-c75a307b5737-aiefs.json`, used verbatim). Question type per the digest: `definitional`.
- **Question (definitional, free recall):** name Adam's two running averages and say what the bias-correction hats are for.
- **Learner answer (verbatim):** "average gradient and average velocity. the bias correction step is there to solve the cold start probelm in Adam training whereby early in the training process it takes timid steps. bias correction tweaks the gradients to mitigate this."
- **Verdict:** **FAIL** — grade-audit agreed. Why: the second running average was misnamed "average velocity" — v̂ is the mean of the **squared** gradients (RMSProp heritage); velocity is the momentum term m. The cold-start intuition was right in spirit (zero-initialised moments ⇒ timid early steps) but the hats were said to "tweak the gradients" rather than correct the moment estimates (÷ (1−β₁ᵗ) / (1−β₂ᵗ)).
- **Feynman explain-back:** none (`feynman: none` — `procedure` rows are exempt, P1.1). The Attempts.json Feynman flag is unchanged: — (none offered).
- **Repair (in-turn):** m̂ = mean of g, v̂ = mean of g², and the hats are the bias correction for the zero start.
- **Attempts.json:** one attempt recorded 2026-10-10 — `fail` (definitional, `sure`, hints 0). Net state: mastery **0.35** advisory, `interval_index` 1 → **0**, `next_review` 2026-10-10 → **2026-10-13** (procedure +3d), `consecutive_correct` 1 → 0, `consecutive_wrong` **1**, Feynman — unchanged.
- **Mistakes ledger:** **no new row** — both existing rows (2026-09-26, 2026-10-03) are patched in place (same concept, same item thread — the m̂/v̂ names-and-roles half; no duplicate row). Both stay `active`, retries 0, next retry realigned to **2026-10-13** (Attempts.json).
- **Active Concepts:** row synced — `last_reviewed` 2026-10-03 → **2026-10-10**; `next_review` 2026-10-10 → **2026-10-13**; `Last Q Type` discriminative → **definitional**; mastery noted.
- **Advisory mastery:** **0.35** — Feynman: — (procedure, exempt).
- **Carry-forward:** the open half is the *names and roles* of the two averages: m̂ = mean gradient (direction), v̂ = mean squared gradient (scale), adaptive step ∝ m̂/√v̂, hats = the (1−βᵗ) zero-init correction.
