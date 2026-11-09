# Session — Dimensionality Reduction (P1 L10 resume, CP4 mini 4 sealed) — 2026-10-10

**Type:** teach (Tutor, /pause handoff — partial) · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction
**Position at pause:** in-progress, **paused at Checkpoint 4/6 — CP4 mini 4 sealed 2026-10-10** (teaching only; **the CP4 practice is still pending**; minis 2 and 3/3b sealed 2026-10-09; mini 1 sealed 2026-10-08; CP3 fully sealed 2026-10-07; CP2 sealed 2026-10-05; CP1 sealed 2026-09-30). Resume from the **CP4 practice**: one graded MCQ batch on the whole t-SNE chain (mini 2 perplexity incl. the n−1 ceiling; mini 3 objective; mini 3b heavy tail; mini 4 misreading protocol), then CP5 (UMAP).

## What happened (chronology)

1. **Warm-up — CP4 mini 3/3b recall (graded, verifier-agreed 3/3, all sure):** W1 C ✓ (push KL down as far as a 2D map can; zero unattainable) · W2 A ✓ (Q is what moves — the 2-D map's neighborhood probabilities, steered via the coordinates; P frozen) · W3 B ✓ (Gaussian Q collapses Q_ij → 0 so P log(P/Q) blows up; the Student-t fat tail keeps Q_ij up). Quiz-audit PASS first cycle. Attempt: t-SNE pass (discriminative, sure, 0 hints).
2. **Heavy-tail 3b re-walk (learner-requested pacing call honored; fact-check PASS):** 5-step pair-level walk — P_ij = 0.05 frozen from the data; Q_ij the steerable number; fine = P_ij · log(P_ij/Q_ij), a **log-ratio, not a product** (agreement ⇒ ≈0.05 log 1 ≈ 0; disagreement 0.05 vs 0.001 ⇒ ratio 50, log 50 ≈ 3.9, cost ≈ 0.2); Gaussian e^{−d²} collapse ⇒ every escape fined; Student-t tail ⇒ moderate pairs spread affordably while big-P pairs still pay (JMLR: "mismatched tails compensate for the mismatched dimensionalities"). **Micro-check:** P = 0.2, Q = 0.001 → learner answered **≈1.529** ✓ (his log₂ route: 0.2 × log₂200 ≈ 0.2 × 7.64 ≈ 1.53 bits; nats route ≈ 1.06 — grade-audit agreed, pass). The 2026-10-09 pacing call is **resolved**.
3. **CP4 mini 4 atom 1 — cluster sizes meaningless (sealed):** E4 elicit → "each cluster has its own perplexity knob… tuning perplexity would increase the cluster sizes" (knob instinct right, ownership muddled) → Guiding Q1 (ownership; mini-2 anchor: per-point σ_i binary search toward ONE user-set target) → "the user owns the target. the knob is really about per point." ✓ → first state attempt was internally inconsistent with ownership ("each point in cluster A has higher perplexity than each point in cluster B") → Guiding Q2 (one plot ⇒ one target ⇒ size can't come from the knob) → own words: "the 2d coordinates the otpimizer produced in cluster A are further apart than those in cluster B" ✓ → check-and-extend (fact-check PASS): apparent size = map-internal spread ⇒ **cluster sizes on a t-SNE plot are meaningless** (Distill misreading #1); sizes shift with perplexity and re-runs; pure noise at low perplexity still shows dramatic clumps; sibling of mini 1's caution (pairwise relationships spoofed vs quantities read off the layout).
4. **CP4 mini 4 atom 2 — cluster distances (sealed):** E5 elicit → distances "tracking the KL objective"; bets the C–D gap grows with higher perplexity; implication: "reading off those distances isnt about the data but about perplexity knob applied to the 2d neighbors the optimizer happened to arrange" (right shape) → Guiding Q1 (the weightless pair: far-apart pairs get P_ij ≈ 0 ⇒ fine ≈ 0 under any separation) → "near zero, low fine" ✓ → Guiding Q2 (no guaranteed direction) → "free to rearrange either way… the objective doesnt guarantee the direction of motion" ✓ → check-and-extend (fact-check PASS): **cluster distances mean little at an untuned perplexity**; **fragile exception:** tuned-perplexity matching the data's natural cluster structure makes inter-cluster distances *somewhat* meaningful (heterogeneous densities may admit no single valid perplexity). **⚠️ Sources disagree surfaced:** Rohit's unconditional "distances between clusters in the output are not meaningful" vs Distill's tuned exception — **resolved both-true-at-scope: Rohit = safe default rule; Distill = fragile exception requiring a deliberate tuning experiment.**
5. Learner requested the pause **before** the CP4 practice → this partial handoff.

## Verification this session

- quiz-audit: warm-up PASS (first cycle) · E4 elicitation PASS (first cycle) · E5 elicitation PASS (first cycle).
- grade-audit: warm-up agreed 3/3 · re-walk micro-check agreed (≈1.529 bits, log₂ route).
- fact-check: 3b re-walk (5 claims; the verifier's only ISSUE was a base-convention slip in an internal claim, corrected before any learner-facing emission — learner text never contained the wrong number) · mini 4 atom 1 check-and-extend PASS · mini 4 atom 2 guiding-turn PASS · mini 4 atom 2 check-and-extend PASS (with the Rohit-vs-Distill contradiction registered).

## Attempts (ops.py) at this handoff

- t-SNE (Dimensionality Reduction) — pass (warm-up, discriminative, sure, 0 hints) · pass (re-walk micro-check, qtype micro-check, sure, 0 hints) → mastery **1.00**, interval_index 3, next_review **2026-11-09**.
- Bookkeeping: two extra rows (explain-back / free-recall with hints 2) were briefly over-logged for the ungraded guiding/statement rounds, then **reverted** (Attempts.json edited back + the two legit rows re-logged via `--date 2026-10-10`). Net ledger = exactly the two graded items.

## Handoff payload for the Clerk

- `concepts`: t-SNE (Dimensionality Reduction) — mini 4 content (misreading protocol: sizes meaningless; distances meaningless untuned / somewhat meaningful tuned; the ⚠️ Rohit-vs-Distill resolution) + the 3b re-walk annotation ("cost is a log-ratio, not a product", now sealed with a computed micro-check).
- `status` / `resume_from`: paused at Checkpoint 4/6 — CP4 mini 4 sealed 2026-10-10 (teaching only; CP4 practice pending); resume from the CP4 practice, then CP5 (UMAP).
- `mistakes: []` — no graded fail today; the ownership/state detour was repaired in-ladder (ungraded).
- `dependency_events: []` — no just_tell_me / declined_generation; every State-rung generation made.
- `lang_recommendation`: Python (lesson header).
- `partial: true` — keep the lesson row in-progress; keep the Scout digest note: the digest is 15 days old (past TTL) — **re-scout before CP5** fresh-source teaching; CP4 teaching consumed the t-SNE halves of the cached sources (this session's fact-checks re-cited Distill/JMLR).
- Pacing note (durable): the 2026-10-09 heavy-tail pacing request was honored and closed today; no new pacing requests.

## Wiki writes expected from the Clerk (suggestions, not done by Tutor)

- `t-SNE (Dimensionality Reduction)` — add the misreading-protocol learnings (sizes meaningless; distances meaningless untuned / somewhat meaningful tuned + the Rohit-vs-Distill scope split), plus the 3b re-walk product ("cost is a P-weighted log-ratio" already banked — now with the learner's own computed example 0.2·log₂200 ≈ 1.53 bits).
- `## My understanding` (status=learner-note) — the learner's verbatim statements: "the user owns the target. the knob is really about per point." · "the 2d coordinates the otpimizer produced in cluster A are further apart than those in cluster B" · "reading off those distances isnt about the data but about perplexity knob applied to the 2d neighbors the opimizer happended to arrange" · "i think whats left is perplexity so i think its free to rearrange either way the knob moves. the objective doesnt guarantee the direction of motion" · "the fine is approx 1.529".
