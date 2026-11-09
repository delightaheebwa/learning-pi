# Learning Record 0015 — UMAP's two dials: n_neighbors and min_dist — 2026-10-14

**Date:** 2026-10-14 · **Lesson:** Phase 1 L10 Dimensionality Reduction (CP5 minis 2–3) · **Source(s):** umap-parameters sweep (`Knowledge Wiki/raw/sources/2026-10-13 - dimensionality-reduction - umap-params.md`); umap-paper Definition 11 / Algorithm 5 (`…- umap-paper.md`); Rohit P1 L10 (`…- rohit.md`). Digest: fresh 2026-10-13 re-scout (audited PASS).

## What was learned

- **n_neighbors (Bloom: Understand → Analyze):** the hard integer k that sets each point's local chart coverage — one fixed list length for the whole run, not a per-point soft count like t-SNE's perplexity. Small k = charts barely overlap → components and singletons; large k = charts overlap everywhere → the map coheres while fine local detail blurs away. The knob carries the whole local↔global balance by itself — there is no separate global module in the construction.
- **The k=2/20/200 sweep is the anchor evidence:** at 2 UMAP "merely glues together small chains" and leaves singletons; by 20 there is "a fairly good overall view"; at 200 the overall structure is captured but individual colors drift from their nearest matches.
- **min_dist (Bloom: Understand → Apply):** the OUTPUT-side packing floor — the minimum distance apart that points are allowed in the 2-D picture. Default 0.1; 0.0 gives clumps and strings; larger values push structures "apart into softer more general features". It never touches the graph; a fragmented graph stays fragmented regardless.
- **The floor arrives as a force curve:** the paper's piecewise rule is approximated by a smooth attraction/repulsion curve with $a$, $b$ fitted from min_dist and `spread` — sub-floor placements are penalized, not vetoed. Sources disagree on how 'hard' the floor is (docs vs paper); surfaced in-session and resolved: practical reading = strong resistance, mechanism = gradient penalty.
- **The leaves-and-stomata analogy (learner's own):** small k = zooming into a leaf (stomata resolved, leaf shape lost); large k = zooming out (leaf shape understood, stomata lost). One number, different jobs at different settings.
- **The box-packer analogy (learner's own):** min_dist tells the packer how tightly items go in the box; higher = more spacing, lower = tighter. Refined in-session: the floor is permissive (pack down TO it, never through it), and the push fires only on sub-floor pairs — though raising the value reshapes the whole curve, softening the entire picture, not just the tightest spots.

## Evidence

- Warm-up (CP5 mini 1): 3/3 all `sure` before new material (local-flatness definition, patch→glue→match recipe, random-k-NN pull-together failure).
- Mini 2 State rung: the leaf analogy, accepted and extended with the mechanism — the learner's own words carried the idea; two guiding questions given (UMAP had no independence evidence, budget 2).
- Mini 3: tie-downs 2/2 (output-side floor; fragmentation = overlap failure), Idea turn 8/8, the closing generation "it kicks in when two points try to go lower than the floor in terms of distance between them" complete-correct.
- Pause exit ticket 1/3: the knob-crossing slip fired twice in one batch (X1 gains-only answer; X3 input-side min_dist) — self-attribution pending, repair banked for a later warm-up per the learner's choice.

## Learning notes

- The knob-separation lesson is the pattern to watch: this is the same 'which dial do I turn' pressure that the t-SNE perplexity knobs passed, and it needs one more pass before independence.
- Highest Bloom demonstrated: Analyze (the leaf analogy reasoning trade-offs on both ends unprompted).

## Dependency

- No opt-outs: no `just_tell_me`, no `told_repair`, no `declined_generation` — every State-rung generation was made (leaf analogy, box analogy, the floor trigger).
