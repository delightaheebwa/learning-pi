# Session — Dimensionality Reduction (P1 L10 resume, CP4 fully sealed) — 2026-10-12

**Type:** teach (Tutor, /pause handoff — partial) · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Position at pause:** in-progress, **paused at Checkpoint 4/6 — CP4 fully sealed 2026-10-12** (practice + exit ticket done; mini 4 sealed 2026-10-10; minis 2/3/3b 2026-10-09; mini 1 2026-10-08; CP3 fully sealed 2026-10-07; CP2 2026-10-05; CP1 2026-09-30). **Resume from CP5 (UMAP) mini 1 — re-scout first** (digest 17 days old, past TTL; only the t-SNE halves of the cached sources consumed).

## What happened (chronology)

1. **Pre-practice elicitation (quiz-audit PASS; ungraded):** learner walked the fine in his own words — "P_ij is the probability provided by the data and Q_ij is the probability provided by the model" · "it weighs the punishment by the data" · at an arbitrary perplexity the cross-cluster fine is negligible, so the optimizer's arrangement alone explains the untrustworthiness of size/distance readings. Check-and-extend (fact-check PASS 5/5): sharpened that Q is computed from the 2-D coordinates through the heavy-tailed kernel (the only mover); sealed phrasing: **the fine only speaks for pairs with P weight; anything read off the plot across weightless territory is the optimizer's arrangement** — with the Rohit-vs-Distill scope split re-anchored.
2. **CP4 practice (quiz-audit PASS; grade-audit agreed 4/4, all sure):** P1 D ✓ (knob 40 > the 24-point ceiling, H = log₂24 ≈ 4.58 bits, σᵢ saturates) · P2 C ✓ (big P tiny Q — data-near/map-far, P-weighted) · P3 B ✓ (Gaussian tail decays too fast; the t keeps mid-range Q affordable) · P4 A ✓ (no single valid global perplexity under heterogeneous densities; verify by tuning runs). Attempts: t-SNE pass ×2 (batch rows logged transfer-near + explain-back) → mastery 1.00.
3. **Kernel deep-dive tangent (learner questions, fact-check PASS per turn):**
   - **Relative tails:** near d≈0 the curves are twins; the gap opens gradually and keeps widening — Gaussian dies exponentially, t decays like 1/d². "Widening gap, no flip point" — not a half-and-half split of the axis.
   - **Where the kernels come from:** shared idea = turn distance into "probability of being neighbors". Data side: Gaussian bells, σᵢ per point (binary search → perplexity). Map side: q_ij ∝ 1/(1+d_ij²) normalized — a Student-t shape — chosen because a 2-D Gaussian Q collapses Q_ij at distance and strangles the crowd's escapes. "Neither is forced: two jobs, one shared idea."
   - **Why the crowd sits in the tail region:** by construction — P is sharply peaked (~perplexity real-weight pairs); close range is scarce and claimed first by big-P pairs (KL asymmetry); the distance-concentrated mid-range crowd (CP3 curse anchor) is pushed outward into exactly the region where Gaussian Q has died but the t is still up.
   - **σᵢ binary search re-anchored:** one user-set target; per-point bell widths (dense ⇒ narrower, sparse ⇒ wider) until each point's Per(P_i) hits the knob.
4. **Pause exit ticket (quiz-audit PASS; grade-audit agreed 3/3, all sure):** X1 B ✓ (Gaussian data side / Student-t map side) · X2 C ✓ (close range claimed first, crowd pushed into leftover room) · X3 A ✓ (bells stop short ⇒ P_ij ≈ 0 ⇒ nothing pins the gaps). Attempt: t-SNE pass (discriminative, sure, 0 hints) → mastery 1.00, interval_index 3, next_review 2026-11-11.
5. **Client glitch (cosmetic):** the exit ticket first rendered as mixed Chinese/English on the learner's end; the same verified text was re-emitted clean — no content change, no re-verification.

## Verification this session

- quiz-audit: pre-practice elicitation PASS (first cycle) · CP4 practice PASS (4 cycles: length-parity + key-coverage fixes each cycle) · exit ticket PASS (3 cycles: length-parity fixes).
- grade-audit: CP4 practice agreed 4/4 · exit ticket agreed 3/3 (run briefly detached for a supervisor request — resolved by supplying the option text; verdict PASS, agrees:true).
- fact-check: check-and-extend on the elicitation (5/5) · P3 kernel explanation turn (5/5) · tails-agreement turn (3/5 checked as drafted, all PASS) · kernel-origins/crowding turn (5/5) · three-question follow-up turn (4/4) · widening-gap turn (3/3). *(One initial dispatch was returned CLAIMS_INCOMPLETE for a missing formula claim; re-dispatched with the claim added.)*

## Attempts (ops.py) at this handoff

- t-SNE (Dimensionality Reduction) — pass (CP4 practice batch, transfer-near, sure, 0 hints) · pass (same batch, explain-back row, sure, 0 hints) · pass (exit ticket, discriminative, sure, 0 hints) → mastery **1.00**, interval_index 3, next_review **2026-11-11**.
- Bookkeeping note: the 4-item CP4 practice was logged as two rows (transfer-near + explain-back) — one batch, two rows; no further rows for it.

## Handoff payload for the Clerk

- `concepts`: t-SNE (Dimensionality Reduction) — CP4 practice sealed (whole chain: ceiling, objective, heavy tail, misreading protocol) + the kernel deep-dive (Gaussian-bells data side / 1/(1+d²) Student-t map side; widening-gap tail story; crowd-sits-in-the-tail-region-by-construction chain).
- `status` / `resume_from`: paused at Checkpoint 4/6 — CP4 fully sealed 2026-10-12; resume from CP5 (UMAP) mini 1, **re-scout first** (digest past TTL).
- `mistakes: []` — no graded fail today; all practice and exit-ticket items passed first pass, all `sure`.
- `dependency_events: []` — no just_tell_me / declined_generation; every question was a learner-initiated tangent, answered in full.
- `lang_recommendation`: Python (lesson header).
- `partial: true` — keep the lesson row in-progress at Checkpoint 4/6 (CP4 done; CP5/CP6 remain).
- Pacing note (durable): no new pacing requests; the 2026-10-09 heavy-tail pacing call remains resolved.

## Wiki writes expected from the Clerk (suggestions, not done by Tutor)

- `t-SNE (Dimensionality Reduction)` — add the kernel-origin story (data side = Gaussian bells with per-point σᵢ; map side = q_ij ∝ 1/(1+d²), a Student-t shape, chosen to keep Q alive at distance), the widening-gap tail picture (no flip point), and the crowd-placement chain (peaked P → scarce close range claimed by big-P pairs → concentrated mid-range crowd pushed outward).
- `## My understanding` (status=learner-note) — learner's verbatim statements today: "P_ij is the probability provided by the data and Q_ij is the probability provided by the model" · "it weighs the punishment by the data" · "for an arbitrary perplexity, distances mean little since there is a negligible fine and optimizer's 2d arrangement can make some clusters have more points which are closer toghether than others hence some may be smaller than others".
