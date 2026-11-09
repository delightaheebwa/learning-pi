# Review — PMF vs PDF — 2026-09-30

- **Track/Source:** aiefs — Rohit P1 L06 + CS229 (Python)
- **Type:** concept · **Q type:** definitional (free recall, three parts)
- **Why this slot:** priority-1 due mistake — the 2026-09-11 ledger row (`active`, next retry 2026-09-29) was the oldest due mistake; the item re-tests the PMF/PDF label inversion that recurred on 2026-09-26 (probe Q9, L10).
- **Question:** Definitional free recall, three parts — (a) which object gives point probability, and what do its values do? (b) how do you get the probability of a range from the other one? (c) is the density value at a point itself a probability?
- **Learner answer:** "1a) PMF. they sum to 1. b) you get the pdf for that range. c) false. this is because density is gotten through integrating over an interval."
- **Verdict:** PASS — grade-audit agreed (batch verdict agrees: true, item 1). Why: both labels are right (PMF = discrete point probability whose values sum to 1; PDF = density) and the density-at-a-point-is-not-a-probability claim is correct with its reason (probability comes from integrating the density over an interval) — the 09-11 / 09-25 / 09-26 label inversion did not recur. Part (b) is phrased loosely: "you get the pdf for that range" implies but does not state the integration step.
- **Attempts.json:** mastery 0.50, interval_index 1, next_review 2026-10-07, Feynman: fail (carried — no Feynman item this session).
- **Mistakes ledger:** 2026-09-11 row → `review`, retries 1 (first correct recall since the row was opened), next retry 2026-10-07.
- **Carry-forward:** Last Q Type is now `definitional`, so the next queue entry for this concept is a discriminative item; the Feynman flag is still `fail` and has not been re-attempted.
