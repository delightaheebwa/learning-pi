# Session — Information Theory Ingest (CP6 + Feynman + final quiz, L09 done) — 2026-09-24

**Type:** ingest (final, non-partial lesson handoff) · **Track:** AIEFS (AI Engineering from Scratch) · **Lesson:** Phase 1 L09 — Information Theory (Entropy, KL Divergence)
**Content source:** `Lessons/Lesson — Information Theory — 2026-09-11.md` (`Status: **done (2026-09-24)**`) via the Tutor's `Core/Pending Ingest.json` (`partial:false`, `status:"done"`, `resume_from:null`); teaching note `Sessions/Session — Information Theory (P1 L09 resume, CP6 + Feynman + final quiz) — 2026-09-24.md`; Learning Record `Learning Records/0008-perplexity-units-and-label-smoothing.md`.
**Live sources this session:** Rohit `phases/01-math-foundations/09-information-theory/docs/en.md` (Tutor re-fetched; no drift vs the 09-11 digest) and PyTorch `torch.nn.CrossEntropyLoss` docs. Lesson letter-convention caveat (Olah `H(P,Q)` weights-from-truth vs Rohit/ML P=data) stays in force on the wiki pages.

## Concepts added — 3 Active Concepts rows, 4 new wiki pages

| Concept | Type | Page | Core idea banked |
|---------|------|------|------------------|
| Perplexity | concept | `wiki/Perplexity.md` | PPL = 2^H bits / e^H nats = effective number of equally likely choices; uniform over k → exactly k (GPT-2 ≈ 30, frontier single digits); evaluation-time output-side conversion; its "uniform" is a hypothetical yardstick, not label smoothing's ingredient; the 5-bits-as-e^2.4 = 11.048 unit slip (repair: bits → base 2, nats → base e) |
| Bits vs Nats | memory | `wiki/Bits vs Nats.md` | bit / nat / hartley; 1 nat = 1.4427 bits; base is a pure unit (order, zeros, KL = CE − H all unchanged); the exponent-base detector; 2.3 nats → 3.3 bits and 4 nats = 5.77 bits |
| Label Smoothing | concept | `wiki/Label Smoothing.md` | soft_target = (1−ε)·one-hot + ε/K (0.84 / 0.04 at ε=0.2, K=5); L = (1−ε)·CE(hard, p) + ε·H_uniform with ε/K in the second term; PyTorch `label_smoothing` ∈ [0,1] default 0.0; the ε=1-extreme slip (0.2 everywhere); ε=1 erases the label; open question = principled adaptive ε (distillation, Hinton 2015) |
| Logits & log-odds | supporting (page only, no Active Concepts row — handoff status `supporting`) | `wiki/Logits & Log-odds.md` | logits = unnormalized scores, softmax = exp/normalize + shift invariance; two-class exactness z = log p/(1−p); multi-class log-odds = logit differences z_c − z_j = log p_c/p_j; certainty at +∞; squeeze vs stretch (0.999 → 0.9999 = 10× error-mass shrink, 0.001 linear; 6.9 → 9.2 nats) and Bayes additivity |

All four pages are cross-linked into the existing information-theory cluster and cite the lesson source, the Rohit `docs/en.md` and the PyTorch docs.

## Concepts enriched — 4 pages, no duplicates

- `wiki/Entropy (Average Surprise).md` — new section "Why the weights are the probabilities (2026-09-24)": the unweighted-surprise slip on final-quiz Q1 (answered 5 bits = 1+2+2 for (0.5, 0.25, 0.25)), the repair (p(x) appears twice — surprise generator inside the log, weight outside; the distribution feeds itself), the isomorphic 4-sided-die re-test (1.75 bits, sure), and the 2^H / e^H bridge to the new pages.
- `wiki/KL Divergence.md` — retrieval log 2026-09-24: floor identity 1.75 − 1.50 = 0.25 bits PASS; the KL(joint ∥ product) form cold PASS; smoothing-family cross-links.
- `wiki/Mutual Information.md` — retrieval log 2026-09-24: Q3 cold retrieval of the KL form (the 09-16 / 09-18 variables-vs-distributions slip now holds across two later sessions); MI ≥ 0 detector behind the 09-21 sign slip.
- `wiki/Variation of Information.md` — retrieval log 2026-09-24: warm-up 2/2 (independence MCQ → H(X) + H(Y), dodging the MI-zero distractor; V = 1.2 + 0.9 − 1.0 = 1.1 bits).

`Knowledge Wiki/index.md` gained the four new Concept links; `Knowledge Wiki/log.md` gained this session's entry.

## State reconciled (from the handoff as single source of truth)

- `MISSION.md` (Position), `CURRICULUM.md` (Mission 2 phase note, row 09 → **done**, exit line), `Core/💡 Learning Profile.md` (Last Updated / Current Focus / Current Position / Sequencing), `Core/📚 Active Concepts.md` (AIEFS status bullet + IT section header): all now read **L09 Information Theory done 2026-09-24; position pointer L10 Dimensionality Reduction — not-started**. The lesson file's own `Status: **done (2026-09-24)**` and `resume_from: null` agree with the handoff — no contradiction to surface, nothing merged. Lesson file, teaching note and Learning Record 0008 are untouched history.
- Active Concepts IT section: +3 rows (`Perplexity`, `Bits vs Nats`, `Label Smoothing`), section now 8 rows, AIEFS 34 live concepts. Synced from `Attempts.json` (2026-09-24): `Entropy (Average Surprise)` → 2026-09-24 / 2026-10-01, `KL Divergence` → 2026-09-24 / 2026-10-24, `Mutual Information` → 2026-09-24 / 2026-10-24, `Variation of Information` → 2026-09-24 / 2026-10-24.
- `Attempts.json` hygiene: the Tutor's duplicate key `Entropy` (its 2026-09-24 fail + isomorphic-re-test pass) was canonicalized into `Entropy (Average Surprise)` (5 attempts preserved, merge note added) and the alias key removed; `Information Theory` (Feynman pass) kept as the lesson roll-up.
- `Core/🧯 Mistakes.md`: +3 rows with canonical concept names (Entropy (Average Surprise), Perplexity, Label Smoothing).
- `Core/Learner History.md` regenerated via `scripts/learner_history.py`.

## Open questions carried

- What would an information-theoretically principled *adaptive* ε for label smoothing look like? (learner's own wonder-out; the Adam analogy was kept distinct — adapting the target vs adapting the optimizer; distillation is the principled informed-smoothing version, Hinton 2015). Logged on the `Label Smoothing` row and page.

## Marker / cleanup

- Final ingest: `Core/Pending Ingest.json` consumed and cleared. No `.tmp/context-*.json` digest exists in this checkout (resume flow; the Tutor re-fetched live) → nothing deleted; `Learning System/.tmp/l09-en.md` is the fetched Rohit source body, not a Scout digest, and stays (`.tmp/` is gitignored).

## Verification

- Parent-owned `review-gate` targets the 8 wiki pages Clerk wrote: `Perplexity`, `Bits vs Nats`, `Label Smoothing`, `Logits & Log-odds`, `Entropy (Average Surprise)`, `KL Divergence`, `Mutual Information`, `Variation of Information`. State files are out of review scope (covered by the state audit).
- State audit (read-only, `audit_state.py --root .`): see the Clerk summary line (`STATE_AUDIT_VERDICT`).
