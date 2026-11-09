# Learning Record 0016 — UMAP's global structure: a goal, not a guarantee — 2026-10-16

**Date:** 2026-10-16 · **Lesson:** Phase 1 L10 Dimensionality Reduction (CP5 mini 4) · **Source(s):** umap-paper §3.2/§4/§6 (`Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap-paper.md`); umap-faq "How UMAP can go wrong" (`…- umap-faq.md`); Rohit P1 L10 (`…- rohit.md`). Digest: fresh 2026-10-13 re-scout (audited PASS, inside TTL).

## What was learned

- **The global term, mechanically (Bloom: Understand → Analyze):** UMAP's edges only encode local neighborhoods, yet relative cluster positions carry signal because of two mechanisms the learner's glue prior missed: (1) the repulsive term of the fuzzy-set cross-entropy is **sampled across the whole embedding** — push-apart pressure that never switches off with distance, so cluster drift collides with push-back from everything else; (2) the symmetric union B = A + Aᵀ − A∘Aᵀ keeps an edge if either direction voted for it, so chains of overlapping charts transmit pull indirectly — **connectedness itself leaks global information**.
- **The t-SNE contrast, quantitatively honest:** cross-cluster pairs carry P_ij ≈ 0, so rearranging the gaps barely moves the objective (weakly constrained, not literally zero — the probability bookkeeping still couples positions); the gaps end up decided by starting position and drift.
- **⚠️ Sources disagree — resolved as a graduated claim:** Rohit states "better global structure" as a flat advantage ("tend to be more meaningful"); the umap-paper itself hedges ("*arguably* preserves more of the global structure"); the umap-faq frames it as a **goal** ("One of UMAPs goals is to have distance between clusters of points be meaningful") with a documented failure mode: points maximally far from everything get essentially random k-NN edges, all read as maximally similar, and **sufficiently many of them pull the whole space together** — mitigated by `disconnection_distance` (edges above a threshold get cut; those points stay disconnected and are pushed away). Safe rule: trust relative arrangement more than t-SNE's, never as a certificate.
- **The honest wrinkle:** the paper's weaknesses section credits a significant part of the global-structure advantage to the **Laplacian/spectral initialization** (citing Kobak & Linderman: t-SNE with the same init can match it) — one more reason the claim stays "arguably."

## Evidence

- **Warm-up = the banked knob-crossing repairs, re-asked:** W1 ✓ (n_neighbors trade), **W2 ✗ fail** — the slip fired a second time ("raising min_dist breaks the connections"); learner tagged `sure` (calibration flag).
- **W2 diagnose-first repair — self-located:** his own two-stage mapping — *"it acts on stage 2... it can only move them around by making them further or nearer"* — plus the detector (stage-2 dial promoted to stage-1 powers ⇒ story suspect) and the isomorphic micro-check passed complete-correct (n_neighbors; more overlap ⇒ fewer separate clumps).
- **Ladder:** elicitation prior (glue/overlap = the global glue), 1 of 2 guiding questions ("sample from edges which are disconnected" — widened to the whole-embedding pool), then the check-and-extend idea turn (fact-check PASS 7/7 first cycle).
- **Elaboration re-delivery on request:** first draft failed fact-check on four overstatements (t-SNE "exactly 0", absolute drift-free phrasing, "usually succeeds" rate, single-point map collapse); corrected draft PASS 5/5 — the learner heard the honest version, including the Laplacian-init wrinkle, and confirmed "makes sense."

## Learning notes

- The knob-crossing slip has now fired twice (2026-10-14 exit ticket, 2026-10-16 warm-up W2) but was **self-located** this time — the repair is converging; one more clean pass under pressure expected before the row can graduate.
- The learner's glue-first mental model is a genuinely good half of the mechanism; the teaching moved it to whole-embedding repulsion without discarding it.
- Highest Bloom demonstrated: Analyze (pipeline-stage mapping in the locate question; the widened repulsion pool).

## Dependency

- No opt-outs: no `just_tell_me`, no `told_repair`, no `declined_generation`. The "elaborate more and simply" request was a pacing call, honored with a corrected re-delivery — every State-rung generation was made.
