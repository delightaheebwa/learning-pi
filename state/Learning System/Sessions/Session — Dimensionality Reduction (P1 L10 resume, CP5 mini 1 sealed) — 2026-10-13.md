# Session — Dimensionality Reduction (P1 L10 resume, CP5 mini 1 sealed) — 2026-10-13

**Session:** Tutor (learning-teach, resume flow) · **Date:** 2026-10-13 · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Position reached:** paused at Checkpoint 5/6 — **CP5 mini 1 sealed** (CP4 fully sealed 2026-10-12). Resume: **CP5 (UMAP) mini 2 — the `n_neighbors` dial.**
**Verification state:** fresh Scout digest (2026-10-13, audited PASS) · every warm-up/elicit/exit batch quiz-audited (PASS) · every fact-check envelope landed (hmm — all fact-checks PASS as listed below) · grade-audit agreed 3/3 on the warm-up and 3/3 on the exit ticket · tutor-audit dispatched on this batch at handoff.

## Sources

- **Re-scout completed this session** (was standing on the lesson's Resume-from line): fresh digest `Learning System/.tmp/context-01a134d5-4aeb-715d-8ab7-fe2f4f944481-dimensionality-reduction.json` (created 2026-10-13T13:55Z), replacing the 17-day-old past-TTL digest `context-01a0d78c-…` (kept).
- 11 raw bodies re-fetched live under `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - *` (rohit, umap, umap-params, umap-faq, **umap-paper (new)**, shlens, distill, sklearn-kpca, cs229-prob (new), gundersen (new), 3b1b-eigen). scout-audit verdict: **PASS, zero issues.**
- Drift note per digest: rohit body word-identical to the 2026-09-25 fetch (hash deltas = extractor artifacts); umap trio unchanged; roadmap sha bookkeeping only.

## Flow

1. **CP4 recall warm-up (3 graded MCQs, quiz-audit PASS after two length-parity fix cycles; grade-audit agreed 3/3, all `sure`):**
   - W1 B — t-SNE cluster size on the plot = spread of the 2-D coordinates, not a data fact.
   - W2 C — map side is the Student-t with one degree of freedom, $q_{ij} ∝ 1/(1+d_{ij}^2)$, fat tail keeps mid-range $q_{ij}$ up.
   - W3 A — Gaussian $q_{ij} → 0$ at distance ⇒ each moderate pair's escape fine $P_{ij}\log(P_{ij}/Q_{ij})$ explodes ⇒ crowd stays squeezed.
   - Attempt: t-SNE pass (discriminative, sure, 0 hints).
2. **CP5 mini 1 — what UMAP is actually assuming (sealed at the learner's stop):**
   - **Elicitation** (ungraded, quiz-audit PASS first cycle): learner's prior — manifold = "an area of the plot whereby there are many folds (like our swiss roll example)"; assumption = "each layer of the fold is a plane."
   - **Tie-down ×2** (fact-check PASS 3/3): flat unrolled sheet counts ⇒ folding is not the definition; patches glue where they share ⇒ what must be true for stitching to be honest.
   - **State rung ×2, both partial:** "A manifold is simply whatever shape is of dimension 2D or higher" · "There must be no sharing of points hence there must be distinct neighborhoods." Budget of 2 guiding questions spent (UMAP independence: no evidence).
   - **Check-and-extend (idea turn, four-beat foundation, fact-check PASS 8/8, no omitted foundations):**
     - manifold = a **local** property: every small patch is essentially flat space; a straight line is a 1-D manifold, a flat plane a 2-D one — the learner's "each layer is a plane" instinct WAS the idea, "2D or higher" was the frame slip.
     - stitching needs **continuity, not distinctness** — overlap is the stitching; the docs' failure page: a maximally-far point's k-NN comes out random, all maximally similar ⇒ optimizer drags them together, shredding structure; `disconnection_distance` cuts such edges.
     - the three assumptions named: **uniform on a Riemannian manifold · locally constant metric · locally connected** (umap.md; paper derives the construction from these as axioms).
     - mechanism: each point's neighborhood patch → patches overlap through shared neighbors → glued into one global fuzzy structure → embedding = the low-D arrangement whose fuzzy structure best matches.
     - contrast: t-SNE states **no** data assumptions (pairwise neighbor probabilities, non-parametric). Banked pointer: the Rohit-vs-FAQ "better global structure" disagreement surfaces at a later CP5 mini.
3. **CP5 mini 1 exit ticket (3 MCQs, quiz-audit PASS after two fix cycles — X3 length/shape parity rebuilt, X1 strawman distractor replaced with a global-vs-local-flat one; grade-audit agreed 3/3, all `sure`):**
   - X1 C — manifold = every small patch looks like ordinary flat space.
   - X2 B — patch → glue → matching low-D arrangement (C = t-SNE recipe and D = PCA recipe as near-miss siblings).
   - X3 A — far-from-all point: k-NN random and maximally similar ⇒ optimizer drags them together; `disconnection_distance` cuts such edges.

## Attempts this session (ops.py)

- t-SNE (Dimensionality Reduction) pass — discriminative, sure, 0 hints (warm-up).
- UMAP (Dimensionality Reduction) attempt 1 pass — definitional, sure, hints 2, prereq edge recorded **UMAP → t-SNE (Dimensionality Reduction)**.
- UMAP (Dimensionality Reduction) attempt 2 pass — applied, sure, 0 hints.
- Result: **UMAP mastery 0.80, interval_index 3, next_review 2026-11-12**; t-SNE stays 1.00 (next 2026-11-11).

## Mistakes / dependencies

- **Mistakes candidates: none** — no graded fail today; both partial State-rung statements were corrected through the ladder (check-and-extend), standard teaching, no attempt row.
- **Dependency events:** none — no `just_tell_me`, no `told_repair`, no `declined_generation`; the learner made both State-rung generations ("2D or higher" and "distinct neighborhoods") before the idea turn.

## Position

- Lesson file updated: paused at Checkpoint 5/6 — CP5 mini 1 sealed 2026-10-13; resume **CP5 mini 2 (`n_neighbors` dial)**; the re-scout note in the Resume-from line replaced (fresh digest, no re-scout needed).
- Pending Ingest.json written (partial): resume_from `CP5 (UMAP) mini 2 — the n_neighbors dial`; concepts ×1 (UMAP (Dimensionality Reduction)); mistakes ∅; dependency_events ∅.
- Standing rule in force: paper walks / graded MCQ batches only; no code writes as a learning-system task (learner, 2026-10-05); parked code-write integration folds into the final cumulative quiz.
