# Review — Conditional Independence — 2026-11-08

- **Track/Source:** aiefs — Phase 1 L07 notes
- **Type:** concept · **Q types asked:** `definitional` (Q6) then `free-recall` (Q7) → **Last Q Type `free-recall`**
- **Why this slot:** scheduled due review — the row's `next_review` was 2026-11-03 (the 2026-09-21 ledger row was `review`, retries 2). Two items were asked on this concept, so two ledger rows follow.
- **Questions:** the verbatim prompt text was **not carried in the handoff envelope** — recorded as a handoff gap, not reconstructed. The envelope carried each item's type, the learner's verbatim answer and the graded gap.

## Q6 — definitional (spam classifier with the free / money features)

- **Learner answer (verbatim):** "the assumption is that given a class, it is conditionally independent of another class. it is false for words tht genuinely deped on each other e.g New and York. because of this, its calibrated probabilites are not accurate."
- **Targets retrieved (recorded on the attempt, all live):** `n_8eb8ab836f` (Conditional independence definition), `n_69cc6762f5` (Naive Bayes assumption usually false), `n_01bd088722` (Naive Bayes overconfidence).
- **Verdict:** **FAIL** — confidence `hunch`, 0 hints, miss_class `execution`, `pow: none` (grade-audit corrected a claimed pass to fail).
- **Why:** both clauses are present — conditioning on the class, and the genuinely-dependent case ("New" and "York") — so the definition half is intact. The consequence has no direction: "its calibrated probabilities are not accurate" does not say **which way** the error runs. Double-counting correlated evidence inflates the posterior toward the class the evidence already favours, i.e. overconfidence, which is the property the graph node `n_01bd088722` names and the item was retrieving.

## Q7 — free-recall (sample evidence vs theoretical independence: weather service, significance test)

- **Learner answer (verbatim):** "i`m not sure"
- **Targets retrieved (recorded on the attempt, all live):** `n_00153be013` (Independence means no information), `n_60799d4869` (Chi-square test and the meaning of p-values), `n_d141e5e6fe` (Theoretical independence is binary and exact).
- **Verdict:** **FAIL** — confidence `no-idea`, 0 hints, miss_class `cue`, `pow: none` (grade-audit agreed; route `source_return` / `retrieval_cue`, one attempt).
- **Why:** nothing came — no condition named, no evidence read, no verdict. This is a retrieval-cue gap rather than a misconception: the item asked for a judgment (does sample evidence of dependence settle the theoretical-independence claim?) and no ladder was started.

## Recorded state

- **Attempts.json:** two attempts dated 2026-11-08 — `fail` (`definitional`, `hunch`, hints 0, targets `n_01bd088722,n_69cc6762f5,n_8eb8ab836f`), then `fail` (`free-recall`, `no-idea`, hints 0, targets `n_00153be013,n_60799d4869,n_d141e5e6fe`). Net: `interval_index` 2 → 1 → **0**, `consecutive_correct` 1 → **0**, `consecutive_wrong` 0 → **2**, `last_reviewed` 2026-10-20 → **2026-11-08**, `next_review` 2026-11-03 → **2026-11-11** (concept ladder, +3d at index 0), mastery **0.15** advisory, Feynman flag `pass` unchanged (no explain-back result carried in the envelope).
- **Mistakes ledger:** **two new rows** dated 2026-11-08 —
  1. Q6 — error_type `application` / `[miss: execution]` / `[targets: n_01bd088722,n_69cc6762f5,n_8eb8ab836f]` / `active` / retries 0 / next retry **2026-11-11** (envelope `error_type` `execution` canonicalized to `application` = "knew but applied wrong"; the envelope's diagnosis is preserved in the `[miss: …]` prefix).
  2. Q7 — `structural` / `[miss: cue]` / `[targets: n_00153be013,n_60799d4869,n_d141e5e6fe]` / `active` / retries 0 / next retry **2026-11-11**.
- **Active Concepts:** row synced — `last_reviewed` 2026-10-20 → **2026-11-08**; `next_review` 2026-11-03 → **2026-11-11**; `Last Q Type` discriminative → **free-recall**; mastery 0.15 advisory.
- **Advisory mastery:** **0.15** — Feynman: `pass` (unchanged, carried).

## Carry-forward

Two open halves: (a) the **direction** of the consequence — correlated evidence counted twice inflates the posterior toward the predicted class (overconfidence), not merely "inaccurate"; (b) the **evidence-vs-theory** judgment — theoretical independence is a binary, exact claim about the joint distribution, while a significance test reads sample evidence, so failing to reject or rejecting at some α does not by itself settle the theoretical claim.
