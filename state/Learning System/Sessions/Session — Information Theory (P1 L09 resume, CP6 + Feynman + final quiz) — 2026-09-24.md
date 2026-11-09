# Session — Information Theory (P1 L09 resume, CP6 + Feynman + final quiz) — 2026-09-24

Resume of `Lessons/Lesson — Information Theory — 2026-09-11.md` at CP6 (lesson file + prior session notes as source of truth; Scout digest swept by TTL — Rohit en.md re-fetched live from GitHub raw, PyTorch CrossEntropyLoss docs re-fetched live, no drift found vs the 09-11 digest's takeaways). Lesson **completed** this session: CP6 → Feynman → final cumulative quiz → lesson-end handoff.

## Flow (checkpoint pause protocol honored throughout)

1. **Warm-up (CP5.5 retrieval, quiz-audit PASS; grades grade-audit-agreed)** — 2/2 sure: W1 independence-VI MCQ → D (H(X)+H(Y)), dodged the MI-zero distractor; W2 on-paper V from H(X)=1.2, H(Y)=0.9, I=0.5 → 1.1 bits. Attempts: Variation of Information pass ×2 (interval_index 3).
2. **CP6 idea (fact-check PASS 10/10)** — bits/nats/hartleys (1 nat = 1.4427 bits; PyTorch/TF default nats); perplexity = 2^H bits / e^H nats = effective number of equally likely choices, uniform-over-k anchor → PPL exactly k; GPT-2 ~30, modern single digits; label smoothing soft_target = (1−ε)·one-hot + ε/K (0.025/0.925 example), target entropy 0 → positive, L = (1−ε)·CE + ε·H_uniform, infinite-logits motivation; external angle = PyTorch docs (label_smoothing float [0,1] default 0.0, Inception mixture, LogSoftmax+NLLLoss equivalence). No source contradictions.
3. **CP6 follow-ups (each fact-checked PASS before emission; one ISSUES corrected pre-emission)**:
   - Perplexity vs label smoothing staging: no CE→PPL→smoothing pipeline; PPL = evaluation-time output-side conversion (mainly LM reporting), smoothing = training-time input-side target modification. (Verifier initially returned PASS but with a missing-draft binding failure; re-dispatched same claims WITH rendered_content — all 5 PASS. Gate anomaly: one turn rendered via UNVERIFIED fallback after binding failure, content unchanged.)
   - Two uniforms disentangled: perplexity's uniform = hypothetical yardstick (any distribution has PPL = 2^H; a non-uniform model can have PPL 7); smoothing's uniform = real target ingredient. Unrelated uses of the word.
   - Formula breakdown: ε/K lives in the **second** term (ε·H_uniform = Σ (ε/K)(−log p_c)) — my draft said first term; verifier caught it (ISSUES → corrected_claim applied). Smoothed loss = CE against soft target, regrouped. Underscores = snake_case code naming, not math.
   - Logits & log-odds: unnormalized scores, softmax = exp/normalize; log-odds z = log(p/(1−p)) exact in two-class only; multi-class log-odds live in logit *differences* (z_c − z_j = log(p_c/p_j); shift-invariance); probability 1 ⇔ log-odds → ∞.
   - Squeezed-interval elaboration: 0.999→0.9999 is 10× error-mass shrink but only 0.001 linear; log-odds re-rules to odds-ratio distance (6.9→9.2 nats); Bayes-additivity; matches −log(p_true) loss.
   - Learner's synthesis confirmed with sharpening: log gives big shifts CREDIT (true size), not permission; whole-line re-ruling, middle compression intentional.
   - **Adaptive-ε wonder-out** → learner proposed task-adaptive ε "like Adam": affirmed as real research direction (fixed 0.1 standard; adaptive/data-dependent smoothing family exists), info-theoretic target = Bayes-optimal label posterior (ε = crude one-knob proxy), distillation = principled informed-smoothing version (Hinton 2015), optimizer-vs-target lever caution. **Logged as Open Question.**
4. **CP6 practice (quiz-audit PASS; grades grade-audit-agreed)** — P1 perplexity from 5 bits: **FAIL** — answered ≈11.048 (≈ e^2.4: nats formula on a bits value) instead of 2^5 = 32; repaired with the detector "bits → base 2, nats → base e". P2 2.3 nats → 3.3 bits: **PASS**. P3 ε=0.2, K=5 soft target: **FAIL** — picked A (0.2 everywhere = the ε=1 extreme) instead of D (0.84 true / 0.04 others); repaired with the mixture algebra. Attempts: Perplexity fail, Bits vs Nats pass, Label Smoothing fail.
5. **Feynman explain-back (grade-audit gate)** — attempt 1 FAIL (one-liner, ~1/4 rubric); attempt 2 FAIL (chain present but missing why-used / KL-vs-CE distinction / concrete example); attempt 3 **PASS**: classifier loss, KL punishing term, LM perplexity reporting, floor distinction, GPT-2 ~30 example. Floor sentence sharpened post-pass: **both** quantities have floors — CE ≥ H(data) irreducible, KL ≥ 0 (reached at prediction = reality). Attempt logged: Information Theory pass + Feynman pass.
6. **Final cumulative quiz (quiz-audit: cycle 1 ISSUES on Q4/Q5 length-parity → parallel-shape rewrite → cycle 2 PASS_WITH_FLAGS lows-only, accepted silently; grades grade-audit-agreed)** — 5/6:
   - Q1 entropy (0.5,0.25,0.25) **FAIL**: answered 5 bits = 1+2+2, the **unweighted-surprise slip** (weights dropped). Learner asked where the weights come from → repaired (fact-check PASS): the weights ARE the probabilities — the distribution feeds itself (p_i both inside the log as surprise generator and outside as weight). Mistake row (application error).
   - Q2 KL via floor identity: 1.75 − 1.5 = 0.25 bits **PASS**.
   - Q3 joint-vs-product KL = MI: B **PASS** — the repaired E1 form holds under cold retrieval.
   - Q4 VI/MCQ: D **PASS** (V=0 iff mutual determinism; VI true metric, MI not).
   - Q5 nats-vs-bits perplexity comparison: C **PASS** (4 nats = 5.77 bits > 5 bits → model B).
   - Q6 label smoothing own-words: **PASS** (target stops demanding probability 1 → finite logits suffice).
   - Attempts: KL pass, MI pass, VI pass, Bits vs Nats pass, Entropy fail, Label Smoothing pass (Q6; an erroneous duplicate fail entry + a spurious extra fail were appended by mistake and corrected in Attempts.json directly — Label Smoothing now [fail P3, pass Q6], interval_index 1).
7. **Isomorphic entropy re-test (quiz-audit PASS; grade-audit agreed)** — 4-sided die (0.5, 0.125, 0.125, 0.25): **1.75 bits, sure → PASS**. Entropy retrieval re-sealed; Attempt: Entropy pass (interval_index 1).

## Position

- Lesson: **done**. Curriculum row L09 → done at Clerk reconciliation. Next: L10 Dimensionality Reduction.
- Handoff: `Core/Pending Ingest.json` (status: done) — Clerk to write wiki pages (Perplexity, Bits vs Nats, Label Smoothing, Logits & Log-odds), add Active Concepts rows (Perplexity, Bits vs Nats, Label Smoothing — Type per profile; Logits & Log-odds optional), append Mistakes rows: Entropy application error (unweighted-surprise slip, repaired same session, 1 isomorphic re-test pass — can graduate on next review) and Label Smoothing application error (ε=1-extreme misread, repaired same session); consider graduating the 09-18 MI structural row and the 09-15 KL row; reconcile curriculum position to done and clear the paused pointers.

## Verification summary

- quiz-audit: warm-up, CP6 practice, final quiz (2 cycles — Q4/Q5 length-parity highs fixed, then PASS_WITH_FLAGS lows), entropy re-test — all gated.
- grade-audit: W1, W2, P1(fail), P2, P3(fail), Feynman ×3 (fail, fail, pass), Q1(fail)–Q6, R1 — verifier agreed with every claimed verdict.
- fact-check: CP6 idea 10/10; staging answer 5/5; two-uniforms 4/4; formula breakdown 5/5 + 1 corrected_claim applied (ε/K term placement); logits/log-odds 5/5; squeezed-interval 5/5; synthesis-sharpening 3/3; adaptive-ε 4/4; grade-summary turn 2/2; repairs 3/3.
- tutor-audit: dispatched on the handoff batch (lesson file, session note, learning record 0008, Pending Ingest.json).

## Open Questions

- What would an information-theoretically principled *adaptive ε* look like (learner's own wonder-out, Adam analogy kept distinct: adapting the target vs the optimizer)? Distillation (Hinton 2015) is the principled informed-smoothing version — relevant in a later phase.

## Gate anomaly (surfaced, not silently swallowed)

- One fact-check dispatch returned "verdicts PASS" but the gate reported FACT_CHECK_MISSING_DRAFT (envelope binding), then the retry rendered via the UNVERIFIED fallback with identical content. Also one subagent-call-per-turn rejection when two grade-audits were dispatched in parallel — split into sequential foreground dispatches. No content defects; receipt-binding fragility persists (same family as the 09-21 anomaly).
