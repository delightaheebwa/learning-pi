# Session — Dimensionality Reduction (P1 L10 resume, CP5 mini 4 taught) — 2026-10-16

**Session:** Tutor (teach/resume) · **Date:** 2026-10-16 · **Track:** AIEFS · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP) — **in-progress**
**Position at close:** paused at **Checkpoint 5/6** — CP5 mini 4 **taught, idea landed, NO exit ticket** (minis 2–3 sealed 2026-10-14; mini 1 sealed 2026-10-13). **Resume from: CP5 mini 4 exit ticket**, then mini 5 (pipeline PCA→UMAP→HDBSCAN + center-only-vs-standardize).
**Sources:** fresh 2026-10-13 re-scout digest `Learning System/.tmp/context-01a134d5-4aeb-715d-8ab7-fe2f4f944481-dimensionality-reduction.json` (audited PASS, inside TTL — no re-scout); raw bodies `Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - {umap-paper, umap-faq, umap-params, rohit}.md`.

## What happened this session

1. **Warm-up = the two banked knob-crossing repairs** from the 2026-10-14 exit ticket, re-asked in fresh frames (quiz-audit PASS cycle 2; grade-audit agreed 2/2):
   - **W1 ✓ pass** (sure): raising `n_neighbors` 2→50 gains a coherent overall arrangement, fine local detail blurs away.
   - **W2 ✗ fail** (sure): picked C — "forcing points farther apart breaks the connections" — the knob-crossing slip resurfaced exactly as banked; kept answer was B (connectivity untouched, packing only). Calibration flag: sure-wrong on the re-ask.
2. **W2 diagnose-first repair — learner self-located.** Locate question on the two-stage pipeline → his words: *"it acts on stage 2. and no it can change the pairs of points that have been decided. it can only move them around by making them further or nearer."* (mid-sentence "no" = his own self-correction). Sealed with the detector (stage-2 dial promoted to stage-1 powers ⇒ story suspect; **min_dist never touches the graph**) and the isomorphic micro-check: which single dial fixes fragmentation → **n_neighbors**, *"raising it increases the neighbors hence there is more overlap between neighborhoods and less seperate clumps"* ✓ (grade-audit agreed).
3. **CP5 mini 4 — the 'better global structure' claim (idea delivered, landed, no exit ticket):**
   - Elicitation (quiz-audit PASS): learner prior — *"the global structure comes from the gluing together of the charts. i think what stops it is the 'glue'(the overlap between neighborhoods/charts)."* (right half: connectedness transmits information).
   - Guiding Q1 (1 of 2 spent; UMAP has no independence evidence): repulsion pool question → *"i didnt quite understand the question but i think it should sample from edges which are disconnected."* Right place; widened to **every pair across the whole embedding** (edges scarce ⇒ most sampled pairs are non-edges).
   - Check-and-extend idea turn (fact-check PASS 7/7 first cycle): global term = whole-embedding negative sampling + symmetric union B = A + Aᵀ − A∘Aᵀ (connectedness leaks global info); t-SNE contrast (cross-cluster P_ij ≈ 0, gaps weakly constrained); **⚠️ Sources disagree** surfaced and resolved: Rohit flat advantage vs umap-paper "**arguably**" vs umap-faq **goal-not-guarantee** ("One of UMAPs goals is to have distance between clusters of points be meaningful" + the 'How UMAP can go wrong' outlier collapse, `disconnection_distance` mitigation) — resolution: **graduated claim** (design goal, normally visible, breakable by the documented failure; trust relative arrangement more than t-SNE's, never as a certificate).
   - Elaboration re-delivery on learner request (*"i kinda get the idea but in a fuzzy way... elaborate more and simply"*): three-cluster/strings picture — fact-check **ISSUES first cycle** (t-SNE cost overstated as "exactly 0"; absolute drift-free phrasing; unsupported "usually succeeds"; failure mode needs "sufficiently many" far points) → corrected draft **PASS 5/5**, adding the honest wrinkle: the paper's weaknesses section credits much of the global advantage to the **Laplacian/spectral initialization** (Kobak & Linderman: t-SNE with the same init can match). Learner: *"makes sense."*

## Attempts (ops.py, already logged in-session)

- `UMAP (Dimensionality Reduction)` — 2026-10-16: pass (`applied`, sure, 0 hints — W1) · fail (`applied`, sure, 0 hints — W2) · pass (`micro-check`, 0 hints — MC1) → **mastery 0.65, interval_index 3, next_review 2026-11-15**; consecutive_wrong reset to 0.

## Mistakes (handoff — for the Clerk)

- **No new row.** The W2 fail is the **second occurrence** of the already-open knob-crossing row (2026-10-14, `application`, self-attribution pending): bump `retries` on that row and leave `active`; next retry per SRS. No new self-attribution was elicited (learner self-located in-ladder).

## Dependency events

- `dependency_events: []` — no `just_tell_me`, no `told_repair`, no `declined_generation`. The elaborate/simplify request was a pacing call, not an opt-out; the guiding-question budget spent 1 of 2.

## Learner words for the wiki (`## My understanding`, verbatim, `status=learner-note`)

1. *"the global structure comes from the gluing together of the charts. i think what stops it is the 'glue'(the overlap between neighborhoods/charts)."* — accepted as the right half; extended in-session with the whole-embedding repulsion pool and the symmetric union.
2. *"i think it should sample from edges which are disconnected."* — direction-correct; sharpened in-session to "every pair across the whole embedding, most of them non-edges."
3. *"they should reach for n_neighbors. raising it will change the number of points deemed as neigbors for each point. raising it increases the neighbors hence there is more overlap between neighborhoods and less seperate clumps."* — complete-correct micro-check answer (fragmentation fix).

## Clerk task list (at /ingest)

- Deepen `Knowledge Wiki/wiki/UMAP (Dimensionality Reduction).md` with a `## Global structure: goal, not guarantee` section (mechanism: whole-embedding negative sampling + symmetric union; ⚠️ Rohit-vs-FAQ contradiction resolved as graduated claim; the Laplacian-init wrinkle; `disconnection_distance`).
- Append the three verbatim learner statements above to `## My understanding`, annotated around, never rewritten.
- Bump retries on the open knob-crossing Mistakes row (no new row).
- Reconcile position: MISSION / CURRICULUM / Learning Profile / Active Concepts metadata → **paused at CP5 mini 4 (taught 2026-10-16, exit ticket unrun; resume = mini 4 exit ticket)**; sync Active Concepts row to Attempts.json (mastery 0.65, last_reviewed 2026-10-16, next_review 2026-11-15, Last Q Type micro-check).
- Update `Knowledge Wiki/index.md` + `log.md`; regenerate `Core/Learner History.md`.
- The fresh 2026-10-13 digest stays in `.tmp/` (expected warning at a partial close).
