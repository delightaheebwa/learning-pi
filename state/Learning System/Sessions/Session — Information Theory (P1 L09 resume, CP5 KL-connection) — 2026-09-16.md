# Session — Information Theory (P1 L09 resume, CP5 KL-connection) — 2026-09-16

Resume of `Lessons/Lesson — Information Theory — 2026-09-11.md` (paused mid-CP5, 2026-09-15). Sources: lesson file + 2026-09-15 session note (resume flow, no Scout digest needed). Live re-verification via fact-check against Olah Visual Information Theory + Wikipedia Mutual Information. Build language Python. Flow: CP4 warm-up → CP5 KL-connection walkthrough → four learner-driven pause questions → exit ticket → pause.

## Position
Derived at runtime: lesson Status ↔ CURRICULUM row 09 ("resume inside CP5 at the KL-connection walkthrough") ↔ 2026-09-15 session note Resume-from — all agreed, no contradiction. CP3 floor-direction re-test due 2026-09-17 (tomorrow) — NOT due today, untouched.

## CP4 warm-up (quiz-audit PASS_WITH_FLAGS cycle 2, accepted silently; grade-audit PASS 4/4)
Fresh pairs by design (prior numbers 0.278 / 0.326–0.449 retired): W1 identity free recall ("KL = CE − data's entropy", sure) PASS · W2 ∞-case MCQ (A, sure) PASS · W3 on-paper KL(Q∥P) for Q=(0.5,0.5), P=(0.75,0.25) → 0.208 bits, sure PASS · W4 non-symmetry MCQ (C, sure) PASS. All sure, all correct — CP4 re-seal now holds across two sessions. Attempt: KL Divergence pass (interval_index 3, next_review 2026-10-17).

## CP5 KL-connection walkthrough (claims turns, fact-checked 5/5 then 5/5)
Four steps, slow pacing honored: (1) KL roles recalled (truth first, code second); (2) independence = the exact baseline for "unrelated" (product of marginals built cell by cell); (3) I(X;Y) = KL(p(x,y) ∥ p(x)p(y)) — "MI is KL with the independence baseline plugged in"; (4) numeric check on the running joint: baseline 0.25/cell → 2(0.45·log2 1.8) + 2(0.05·log2 0.2) = 0.763 − 0.232 = 0.531 bits, same as the entropy route. Cycle-1 fact-check caught bad intermediate arithmetic in the draft (0.374 vs 0.3816; sums mislabeled 0.531) — corrected and re-verified before emission. ML hook: information gain = I(feature; label).

## Learner pause questions (all fact-checked, all verdicts folded)
1. **Bars intuition replay (09-15 Step 3)** — learner asked if their picture is valid: stacking the two bars counts overlap twice; joint entropy is a fused bar counted once; subtract the non-overlap parts ("set A only / B only") to get MI. **Confirmed valid on both halves** (fact-check 5/5), with the sharpening: stacking picture → "subtract the union once"; fused picture → "subtract the wings". Adopted learner's set-language as the working analogy; "wings" retired at the learner's request — replacements offered (set-difference strips / spotlight / puzzle pieces), recommendation: set-difference strips for language, spotlight for meaning.
2. **"MI is literally KL between relationship (joint) and independence (product of marginals)?"** — confirmed exactly (Olah footnote verbatim; Wikipedia D_KL(p_XY ∥ p_X p_Y)). Direction note: first argument = truth averaged over (the joint). Olah's own KL subscript notation D_q(p) is non-standard/reversed — flagged to the learner.
3. **"High relationship = high KL feels off — KL measures distance-from-truth"** — resolved by fixing roles: the joint IS the truth; independence is the approximation being scored; MI = "how many bits of truth the independence story fails to capture." Learner's reframing ("getting further from independence") accepted with the boats-twist: the joint doesn't drift; the independence claim is measured against it.
4. **"Why no negative KL for negative relationships? Slap an absolute on it? Model more true than the truth?"** — delivered: (a) anti-correlated Y=1−X gives I = 1 bit, the MAXIMUM (H=1+1−1); MI is direction-agnostic, it measures distance-from-chance not co-movement; (b) individual cell terms CAN be negative (off-diagonals −0.116 each) but weighted total ≥ 0 — no absolute value exists in the construction; (c) KL ≥ 0 forced by the coding reductio (negative KL ⇒ wrong-code beats the optimal truth code ⇒ "model more true than the truth" — learner's own phrasing, affirmed); formally Gibbs/Jensen. Signed direction measures = correlation's job; that's why both tools coexist. **⚠ Learner explicitly flagged: negativity discussion NOT fully digested — resume it next session, re-explain from a different angle.**

## Exit ticket (today's material only; quiz-audit PASS; grade-audit agrees 3/3)
| Item | Answer | Verdict |
|---|---|---|
| E1 KL form (free recall) | "between X and Y, truth is X", sure | **FAIL** — variables-vs-distributions slip; correct: KL(p(x,y) ∥ p(x)p(y)), joint first |
| E2 anti-correlated pair | B (1 bit), sure | PASS |
| E3 KL ≥ 0 coding argument | "model's code more optimal than the most optimal code" reductio, sure | PASS |
Attempts: Mutual Information fail → pass (interval_index 1, next_review 2026-09-24); KL Divergence pass (interval_index 3, next_review 2026-10-17). E1 fail is the priority-1 repair item: the SAME identification was stated correctly in conversation minutes earlier — retrieval not banked. Note: conversation-quality vs free-recall gap is itself a signal (fluent-with-prompt, unstable cold).

## Prereq / hypothesis map (end of session)
- KL identity + ∞ case + non-symmetry (CP4): **solid, two-session hold**.
- KL-connection concept (MI = KL joint ∥ independence): **understood in conversation, NOT banked in free recall** (E1) — repair item.
- Nonnegativity/anti-correlation: **delivered, explicitly not digested** — learner-requested re-digest.
- Bars/fused/set-strip geometry: **solid** — learner's own set-language works; no re-teach needed.
- CP5 practice (fresh joint computation): **still never tested** — next after the repairs.
- Pacing preference holds: slow, step-by-step, question-rich. Honored all session.

## Mistakes for Clerk
- **Mutual Information** — error_type `structural`, self_attribution: "E1 free recall: said the KL form is 'between X and Y, truth is X' (sure) — variables confused for distributions; had stated joint-vs-product-of-marginals correctly in conversation minutes earlier." Evidence: exit ticket E1 vs same-session conversational statement. One fail logged; same-session E2/E3 pass.
- Carry-forward (unchanged, from 09-15): KL non-symmetry "re-sealed but shallow — keep a symmetric-pair item in future reviews" (W4 warm-up PASS today counts as evidence it is holding); CP3 floor-direction re-test due 2026-09-17.

## Open questions carried forward
- **Negativity digestion** (learner-flagged, priority): re-explain KL ≥ 0 / no-negative-MI from a fresh angle next session.
- Variation of information V(X,Y) = H(X,Y) − I(X,Y): wonder-out planted (perfect bijection → V = 0 while I = H(X) = H(Y); learner noted "didn't get to the VoI part") — consolidate at resume.
- Label smoothing ↔ Laplace/add-1 link — parked for CP6.
- Letter conventions — Olah letters in lesson, Rohit flipped; translate before comparing (restated in every envelope).
- Wonder-out still open from 09-15: maximum possible overlap of two binary bars (I ≤ min(H(X),H(Y))).

## Handoff
`Core/Pending Ingest.json` — partial:true, status "paused mid-CP5 (KL connection walked)", resume_from: re-digest negativity → repair E1 KL-form slip → CP5 practice on a fresh joint → V(X,Y) consolidation → CP6. Clerk: update Mutual Information row (developing, next_review 2026-09-24 per Attempts.json, Last Q Type `definitional`), keep KL Divergence per Attempts.json (next_review 2026-10-17), keep lesson in-progress at 5/6 mid, no curriculum advance, one new mistakes row above.
