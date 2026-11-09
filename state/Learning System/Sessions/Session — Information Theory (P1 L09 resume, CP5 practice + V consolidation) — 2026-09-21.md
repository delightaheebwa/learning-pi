# Session — Information Theory (P1 L09 resume, CP5 practice + V consolidation) — 2026-09-21

Resume of `Lessons/Lesson — Information Theory — 2026-09-11.md` from its `Resume from:` chain (09-18 state: paused mid-CP5, CP5 practice pending). No Scout digest in `.tmp/` (resume flow — lesson file + prior session notes are the source of truth). Session fully inside 2026-09-21 — no date-label drift this time.

## Flow (checkpoint pause protocol honored throughout)

1. **Warm-up (quiz-audit PASS; grades grade-audit-agreed)** — 2/2:
   - W1 (CP4 identity MCQ, this lesson's letters): C, sure → PASS. Attempts: KL Divergence pass.
   - W2 (the overdue variables-vs-distributions KL-form repair, Mistakes retry due 2026-09-21): "joint distribution of X and Y ∥ product of the marginals", sure → PASS. First successful retrieval of that slip after the 09-16 and 09-18 failures. Attempts: Mutual Information pass (interval_index 1).
2. **CP5 practice (quiz-audit PASS; grade-audit agreed FAIL)** — first-ever I(X;Y) on a fresh joint [[0.35,0.15],[0.15,0.35]] (rows = X): learner answered **−0.119 bits (sure)**. Magnitude exactly right; sign impossible (MI ≥ 0, Gibbs). Almost certainly H(X,Y) − H(X) − H(Y) = 1.8813 − 2 subtraction-order flip. Two hint requests honored (H(X)/H(Y)/H(X,Y) marginalization; the KL/ratio method — both fact-checked, one sign-reading error in the hint draft caught by the verifier and corrected before emission). Attempts: Mutual Information fail (mastery 0.35, next_review 2026-09-24).
   - **Correction delivered**: theorem-as-error-detector framing — a negative MI should feel like a negative probability. Logged as a Mistakes handoff row (application error).
3. **CP5.5 — V(X,Y) = H(X,Y) − I(X,Y) taught** (fact-check PASS, 5/5 claims): source framing (Olah: union/overlap/wings), algebra V = H(X|Y)+H(Y|X) = H(X)+H(Y)−2I (checked on today's joint: 1.8813 − 0.1187 = 0.8813+0.8813 = 1.7626), range 0 ≤ V ≤ H(X)+H(Y), V=0 iff mutual determinism / V=H(X)+H(Y) iff independent, external angle Meilă 2003 COLT / 2007 (VI is a true metric — triangle inequality — used to compare clusterings; MI is not a metric: MI(X,X)=H(X)≠0, die = 2.585 bits — an "anti-distance").
   - Learner follow-ups (both fact-checked PASS before emission):
     - "Why is VI a metric but MI isn't?" — learner's own similarity/dissimilarity intuition validated and sharpened with the four metric axioms.
     - Elaboration on the triangle inequality (fact-check PASS 5/5): bounds for free (VI(A,B)=0.8, VI(B,C)=0.6 → 0.2 ≤ VI(A,C) ≤ 1.4) + the intransitivity counterexample (A=X, C=Y, B=(X,Y): I(A;B)=1, I(B;C)=1, I(A;C)=0; VI: 1,1,2 with 2 ≤ 1+1 tight).
     - Apparent contradiction caught by the learner ("you said the flip of MI is VI, a metric, but also that simple flips fail axiom 4") — resolved and fact-checked PASS 5/5: *arithmetic* flips (pure functions f(I): −I, c−I, 1/(1+I)) all die at axiom 1 because d(X,X)=f(H(X)) can't be 0 for every entropy value (f would have to be identically 0), while *VI is the geometric Venn-complement flip* — not a function of I alone; its H(X)+H(Y) offsets cancel identically at d(X,X): VI(X,X)=2H(X)−2H(X)=0. Also surfaced honestly: my earlier "fail the fourth axiom" shorthand was loose — they already die at axiom 1; the triangle-inequality failure is a second, deeper failure.
4. **CP5.5 practice (quiz-audit PASS; grades grade-audit-agreed)** — 2/2: V1 independence MCQ → B (2 bits), sure — dodged the 0-bits "V=0 at independence" distractor (that's MI's zero); V2 two-route computation on today's joint → 1.7626 bits both ways, sure. Attempts: Variation of Information pass (new concept; interval_index 1).
5. **Exit ticket (today's material only; quiz-audit PASS; grades grade-audit-agreed)** — 3/3, all sure: E1 V-own-words ("what X and Y don't tell each other — their 'secrecy level'; 0 at perfect coupling, max at independence") → PASS; E2 V = 3 − 2(0.8) = 1.4 bits → PASS; E3 negative-MI report → "I(X;Y) can never be less than zero, so the negative answer is wrong" → PASS (the sign-detector lesson internalized). Attempts: Variation of Information pass (interval_index 3), Mutual Information pass (interval_index 1, next_review 2026-09-28).

## Position

- Lesson: paused **after CP5.5**; CP6 (perplexity + bits/nats + label smoothing) not started. Resume chain: (1) CP6, (2) Feynman explain-back, (3) final cumulative quiz → lesson-end handoff.
- Handoff: `Core/Pending Ingest.json` (partial) — Clerk to enrich/add wiki pages (notably a new `Variation of Information` page + Active Concepts row, Type `concept`), append the Mutual Information application-mistake row, consider graduation of the 09-18 MI structural row (KL-form repair passed under retrieval today) and the 09-15 KL row (its "graduate both together" exit condition long met), and reconcile position pointers to "paused after CP5.5 (2026-09-21)".

## Gate anomaly (surfaced, not silently swallowed)

Several teaching turns were verified PASS by the fact-check verifier **repeatedly** (VI-metric answer 9×; triangle-inequality elaboration 3×; flip-clarification 2× — all claims PASS each run, including independent recomputation of the arithmetic) yet the gate withheld the render with NO_FACT_CHECK_MATCH / QUIZ_AUDIT_ISSUES and, after retries, UNVERIFIED banners. Receipt-binding malfunction, not content defects: the verifier verdicts and the emitted text were identical. Also one provider-level 429 on the verifier mid-session → retried per protocol → alternate model (deepseek-v4.1-flash) took over and passed. Worth an `/audit` look at the gate's receipt matching.

## Verification summary

- quiz-audit: warm-up, CP5 practice, CP5.5 practice, exit ticket — all PASS (no revision cycles needed today).
- grade-audit: W1, W2, P1(fail), V1, V2, E1, E2, E3 — verifier agreed with every claimed verdict.
- fact-check: hint-1 (4/4), ratio-method hint (cycle 1: 3 PASS + 1 sign-reading error caught → corrected; cycle 2: PASS), CP5.5 idea (5/5, three independent runs), metric follow-up (5/5), elaboration (5/5), flip-resolution (5/5).
