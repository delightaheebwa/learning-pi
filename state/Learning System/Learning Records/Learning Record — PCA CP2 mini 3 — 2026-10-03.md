# Learning Record — PCA (Dimensionality Reduction) — CP2 mini 3 — 2026-10-03

**Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP)
**Segment sealed today:** CP2 mini 3 — assemble the full `MyPCA` class from scratch, race vs sklearn `PCA(n_components=1)` on a seeded 200-point 2D cloud
**Checkpoint progress:** CP2 now at mini 3/4 sealed (minis 1–2 sealed 2026-10-02); CP2 practice (from-memory class write) still pending.

## What was learned (learner's own words where quoted)

- **Sign-flip split, stated cold and correct:** "eigenvalue ranking is what remains untouched. the pair that flip sign are the signed projected coordinates and the axis direction" — corrected their earlier "all of them" prediction themselves after the $C(-u)=\lambda(-u)$ hint. Highest Bloom: **Analyze** (mapping which outputs are sign-invariant vs not, from the reflection identity).
- **Why variance can't be negative (self-generated consolidation):** "all its doing is summing squared deviations and a mere sign flip doesnt matter because of the square." Extended unprompted to $u^\top C u$ as projected variance — the PSD story landed.
- **Race verdict read off the printout:** explained variance identical (4.98024987 both arms); components exact sign flips; max signed coord gap 13.2 understood as "2× the biggest coordinate — the cloud's own size, not an error" (asked to elaborate on exactly this, then sealed it); magnitude gap 8.9e-16 = float noise.
- **Line-by-line class audit (a)–(d):** (b) $d\times k$, columns = directions, rows = component slots ✓; (c) named both downstream consumers (`components_`, `transform`) that silently break without `[::-1]` ✓; (d) skip signed coordinates because sklearn flips sign and ours doesn't ✓. (a) failed first pass — **"np.cov By default treats columns as features"** (reversed default) — repaired in-conversation: default `rowvar=True` treats rows as variables; `rowvar=False` suits points-in-rows/cols-as-features data. Exit ticket X3 confirms the repair stuck (A, sure).

## Race results (verifier-reproduced)

seed=3, n=200, mean 0, cov [[4,2],[2,1.5]], k=1:
`MyPCA explained = sklearn explained_variance_ = 4.98024987`;
`MyPCA comp = (-0.88907314, -0.45776516)`, `sklearn comp = (0.88907314, 0.45776516)`;
signed coord max gap 13.201563505; magnitude max gap 8.881784197e-16.

## Teaching preference (new, 2026-10-03)

**Learner does not write code in chat** — "kinda like how I don't write formulas here." If code carries conceptual insight, the Tutor teaches/walks it; the learner engages in prose. Carry into every future code lesson (CP2 practice must be re-shaped: from-memory write happens in their own environment, not typed in chat; apply the same rule to later phases' build lessons).

## Open items

- CP2 practice pending (re-shape per the no-code-in-chat preference).
- Carried: curse of dimensionality (rowless, probe Q2); round-cloud degenerate case pocketed for CP3.

## Highest Bloom demonstrated

Analyze (sign-invariance mapping from the race printout + the reflection identity).
