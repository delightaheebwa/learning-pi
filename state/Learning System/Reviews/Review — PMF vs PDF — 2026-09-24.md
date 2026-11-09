# Review — PMF vs PDF — 2026-09-24

- **Track/Source:** aiefs — Rohit P1 L06 + CS229 probability review (Python)
- **Type:** concept · **Q type:** discriminative
- **Why this slot:** priority-1 due mistake; retry was due 2026-09-22.
- **Question:** For a continuous variable with density f, choose the correct statement and explain density, interval probability, and CDF in one line.
- **Learner answer:** "B. a density value is not a point probability because it is as a result of integrating over an interval in a probability distribution. an interval probability that an event happens within a certain range/interval of the probability distribution. CDF differs in that it is computed from the very start of the distribution and not some arbirtrary range in the distribution."
- **Verdict:** FAIL — grade-audit corrected the claimed pass. The selected statement B was right, but the explanation did not state P(X = a) = 0, inverted what integration produces, and did not give the requested PMF nearest-neighbour contrast.
- **Attempts.json:** mastery 0.39, interval_index 0, next_review 2026-09-28, Feynman: fail
- **Mistakes ledger:** existing PMF row returned to `active`, retries 0, next retry 2026-09-28.
- **Repair target:** state the density/point-probability distinction, then integrate over an interval; distinguish CDF as accumulated probability from the left.
