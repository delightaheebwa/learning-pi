# Session — Information Theory (Phase 1 L09) — 2026-09-11

## Position
Phase 1 L09 — Information Theory (Entropy, KL Divergence). Prereqs: L06 Probability (done), L07 Bayes (done). Scout digest fresh (live-fetched 2026-09-11, no drift): context-p1l09-information-theory.json.

## Probe verdict (prereq edge)

| Q | Strand | Answer | Tag | Grade | Note |
|---|--------|--------|-----|-------|------|
| Q1 | A prob/expect | C (−3 bits) | sure | FAIL | −log₂(1/8)=+3; sign flip (recurrence of 09-06) |
| Q2 | A prob/expect | C (p(x)) | hunch | correct-but-unknown | weight on surprise = p(x); hunch → re-probe |
| Q3 | B log-stability | D (overflow) | sure | PASS | subtract-max |
| Q4 | C CE/NLL | A (decrease) | sure | PASS | −log(ŷ) falls as ŷ→1 |
| Q5 | C CE/NLL | C (H(P)−H(Q)) | hunch | FAIL | that is KL's shape; CE ≥ the entropy of the weighting/data distribution — H(Q) in this lesson's Olah letters, H(P) in the en.md/ML letters (P = truth); = iff the two agree |
| Q6 | A prob/expect | fuzzy | — | unknown | expectation = weighted avg of X, not "avg of p(x)" |
| Q7 | B log-stability | overflow/underflow | sure | PASS | correct |
| Q8 | C CE/NLL | fuzzy (distance) | — | unknown | KL intuition, not the likelihood identity |

Strand states: **A = UNKNOWN** (log sign + expectation fuzzy) · **B = SOLID** (softmax stability) · **C = UNSTABLE** (CE≥H and CE≡NLL not landed).

*Lettering note (added 2026-09-12): the probe ran before the CP3 convention reconciliation. This session uses Olah letters (model P, truth/data Q), so the floor reads H(Q); the en.md/ML letters used in the Q5 probe line flip P and Q. See `Lessons/Lesson — Information Theory — 2026-09-11.md` line 6.*

## Priority-1 misconception (load-bearing)
The 09-06 structural mistake ("inverted the −log mechanism") RECURRED in Q1 (sign) and Q5 (CE conflated with the KL subtraction). This is the exact hinge of L09 — every formula here is −log-based. Open the lesson on it.

## Known / Unknown / Reframe (hypothesis)
| Prereq | State | Action |
|--------|-------|--------|
| PMF/PDF + expectation | unknown (fuzzy) | expand — expectation as weighted average; fix "avg of p(x)" |
| softmax + subtract-max | solid | skip-fast (recent pass) |
| CE/NLL + −log sign | unstable → priority-1 | reframe — rebuild −log from "surprise"; un-invert the sign |
| bits vs nats | unknown (untested) | expand during the units checkpoint |

## Build language
Python (Rohit `Language: Python`).

## Resume pointer
Next: Plan (Mermaid graph) → Checkpoint 1 opens on the −log sign fix.


## Pause (2026-09-11)
Paused at Checkpoint 2/6. CP1 (surprise / −log p sign) passed. CP2 (entropy) concept taught; practice sign-flipped (−2.585 vs +2.585 bits) — recurrence of the −log sign inversion, recorded in Mistakes.md. Resume at CP2 to re-seal the sign, then CP3 cross-entropy.


## Pause exit ticket (2026-09-11)
E1 (surprise) pass · E2 (die entropy) pass · E3 (entropy = expectation of surprise, weighted by probability) pass. Sign re-sealed on entropy — Mistakes row bumped review/retries=1. Resume at CP3 cross-entropy.


## Ingest (2026-09-11, Clerk)
Banked CP1–CP2 as 2 new Active Concepts rows (developing) + 2 wiki pages + index/log. Lesson stays in-progress (paused 2/6); digest kept. Resume at CP3 cross-entropy.


## Resume 2 (2026-09-12)
Resumed from CP2. Warm-up (quiz-audit PASS): W1 sign +3 bits sure ✅ · W2 spinner H = 1.5 bits sure ✅ · W3 expected-surprise explanation ✅ — sign re-sealed again, 4 consecutive tests.

CP3 (cross-entropy) taught: H(P,Q) = Σ q(x)·(−log₂ p(x)), weights from truth Q / surprises from model P; = CE loss = NLL (collapses to −log ŷ under one-hot labels); H(P,Q) ≥ H(Q). Practice (fact-checked): coin Q=(0.75,0.25) true, P=(0.5,0.5) model → H(P,Q) = 1 bit exact ✅; floor follow-up FAIL (1 bit = model's H) → corrected to H(Q) ≈ 0.811; misconception logged in Mistakes.md.

Learner paused at CP3/6. Simplified floor re-explanation emitted (fact-check PASS 4/4). CP4 (KL) was emitted BEFORE the pause request but NOT answered/practiced — must be re-emitted fresh on resume.

Resolved tangent (Open Questions): "is the floor H(P,Q) ≥ H(Q) or ≥ H(P)?" — both, convention-dependent: floor is always the entropy of the weighting (true/data) distribution; this lesson's convention → H(Q), Rohit/ML convention (P = data) → H(P). Anchor: "in CE − entropy = KL, the entropy term is always the data's entropy." fact-check PASS 4/4.

## Pause exit ticket (2026-09-12, CP3 only — quiz-audit PASS after 3 fix cycles)
E1 (weights from truth Q, surprises from model P) B sure ✅ · E2 H(P,Q) for Q=(0.9,0.1), P=(0.25,0.75) = 1.84 bits sure ✅ (direction stripped from stem — convention applied from recall) · E3 floor = H(Q) ≈ 0.47 bits (chose C over near-miss D = H(P) ≈ 0.81) sure ✅ — floor misconception re-sealed on a new distribution. All grade-audit agreed.

State: Cross-entropy attempt logged (pass, mastery 0.80, next_review 2026-10-12). Mistakes row (floor) → review/retries=1. Resume at CP4 (re-emit CP4 fresh).

## Resume 3 (2026-09-14)
CP3 warm-up issued (quiz-audit PASS_WITH_FLAGS after 1 fix cycle). Results: W1 H(P,Q)=1 bit sure ✅ · W2 floor=H(Q)≈0.881 (A) sure ✅ · W3 Q=label distribution (C) sure ✅ · W4 FAIL — picked reversed inequality H(P,Q) ≤ H(Q) (tag sure); correct is B, H(P,Q) ≥ H(Q). Grade-audit agreed (correct_verdict fail).

Floor-direction REGRESSION logged: own Mistakes row dated 2026-09-14 (active, due 2026-09-17); attempt logged under canonical key Cross-Entropy from NLL (fail, next_review 2026-09-17; alias key merged away per 09-12 ingest). Active Concepts row updated (last_reviewed 09-14, next_review 09-17 + regression note).

Next: CP4 (KL) — idea block re-emitted 2026-09-14 (fact-check PASS 5/5, opens with the KL ≥ 0 → H(P,Q) ≥ H(data) re-seal); practice not yet issued. CP4 was NOT practiced.

CP4 (2026-09-14, cont.): asymmetry clarification fact-checked 4/4 (learner's Laplace-smoothing wonder-out answer confirmed correct; label smoothing parked for CP6 — log as Open Question/Tangent: Laplace ↔ label smoothing link). Practice issued (quiz-audit PASS, cycle 2) and graded: P1 a/b/c = 1.000 / 0.469 / 0.531 bits all sure ✅ · P2 C sure ✅ — grade-audit PASS (correct_verdict pass). Attempts: "KL Divergence" pass (interval_index 1, next_review 2026-09-21) · "Cross-Entropy from NLL" pass (next_review 2026-09-21). At CP4 Pause #2 — next: on "no questions" → CP5 (mutual information).

## Pause (2026-09-14, CP4 Pause #2)
Learner paused; DECLINED the exit ticket ("CP4 practice just graded — no need") — accepted, per learner-paced protocol; no Day-1 material re-quiz. State: CP1–CP4 done (CP4 graded pass), resume at CP5 (mutual information). Open: CP3 floor-direction retrieval re-test due 2026-09-17 (Mistakes row active). Run /ingest to bank today's progress: Clerk should bank the KL Divergence Active Concepts row (concept, developing, 2026-09-14 → 2026-09-21), realign Cross-Entropy from NLL Next Review to 2026-09-21, refresh Learner History, and close the Mistakes alias rows. Lesson stays in-progress (paused 4/6).
