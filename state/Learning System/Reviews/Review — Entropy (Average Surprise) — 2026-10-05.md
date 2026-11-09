# Review — Entropy (Average Surprise) — 2026-10-05

- **Track/Source:** aiefs — Rohit P1 L09 + Olah (Python)
- **Type:** concept · **Q type:** definitional (short recall + computation)
- **Why this slot:** priority-1 due mistake — the 2026-09-11 ledger row (`review`, retries 1, next retry 2026-10-05) was the oldest due mistake in the queue (`ops.py queue aiefs --date 2026-10-05`); the 2026-09-24 row (the unweighted-surprise slip on this same distribution) was due too.
- **Question:** "Entropy is an expectation: what is being averaged, what are the weights? Compute entropy of P=(0.5,0.25,0.25) in bits."
- **Learner answer (verbatim):** "surprise is what is being averaged. the weights is the truth. entropy=1.5 bits"
- **Verdict:** PASS — grade-audit agreed (dispatch note below). Why: the averaged quantity is named correctly (surprise, −log p) and the 1.5-bit result is right — 0.5·1 + 0.25·2 + 0.25·2 — so the historical unweighted-sum slip (5 bits = 1 + 2 + 2 on this very distribution) stayed away; "the weights is the truth" is a loose articulation, but the arithmetic shows the p_i weights were applied. **Dispatch note:** grade-audit v1 ran against the claimed `fail` and disagreed; the corrected re-dispatch (learner answer + verifier verdict) returned `correct_verdict: pass`, and the recorded verdict follows the verifier.
- **Feynman explain-back:** none offered — the item was a short definitional item, not an explain-back (`feynman: none`); the row's existing Feynman flag stays `fail`.
- **Attempts.json:** pass → mastery 0.75, interval_index 3, next_review 2026-11-04, q_type `definitional` (Feynman flag unchanged: `fail`).
- **Mistakes ledger:** the 2026-09-11 row advances `review` → `graduated` (retries 2, second consecutive correct; next retry realigned to 2026-11-04). The 2026-09-24 row was already `graduated`; its own item — 1.5 bits on (0.5, 0.25, 0.25) — was thereby directly re-tested clean.
- **Carry-forward:** Last Q Type is now `definitional`; open halves are the Feynman explain-back (`fail`) and the loose weights articulation (the p_i-as-weight framing was not put in the learner's own words).
