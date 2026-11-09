# Session — Dimensionality Reduction Ingest (P1 L10 resume, CP2 mini 3 sealed) — 2026-10-03

**Type:** ingest (partial `/pause` handoff, Clerk) · **Track:** AIEFS (AI Engineering from Scratch) · **Lesson:** Phase 1 L10 — Dimensionality Reduction (PCA, t-SNE, UMAP)
**Position after ingest:** in-progress, paused at **Checkpoint 2/6, mini 3/4** (CP1 sealed 2026-09-30; CP2 minis 1–2 sealed 2026-10-02; mini 3 sealed 2026-10-03). Resume **CP2's single practice**, re-shaped per the new no-code-in-chat preference, then CP3.

## Session Info

- **Date:** 2026-10-03
- **Topic:** CP2 mini 3 — the full `MyPCA` class assembled line-by-line and raced against sklearn on a seeded synthetic cloud
- **Source material:** `Lessons/Lesson — Dimensionality Reduction — 2026-09-26.md`, the Tutor's teaching note `Sessions/Session — Dimensionality Reduction (P1 L10 resume, CP2 mini 3 sealed) — 2026-10-03.md`, and Learning Record `Learning Records/Learning Record — PCA CP2 mini 3 — 2026-10-03.md`. No new upstream fetches — the 2026-09-25 L10 sources (Rohit `docs/en.md`, Shlens, Distill t-SNE, UMAP docs/params/FAQ, 3B1B eigenvectors) are unchanged and still unconsumed by any wiki page before today.
- **Handoff:** `Core/Pending Ingest.json` (`partial: true`; status "paused at Checkpoint 2/6 (mini 3/4 sealed) — CP2 practice (re-shaped per no-code-in-chat preference) next"; `checkpoints_done`: CP1 + CP2 minis 1–3). The lesson file's own `Status:` / `Resume from:` **agree** with the handoff — nothing to surface or merge.

## What was sealed (from the Tutor's note)

- **Warm-up 3/3** (verifier-agreed): eigh ascending with eigenvectors as columns; `vecs[:, order[:k]]` d×k with `Xp = Xc @ V` n×k; the shape detector restated (with the `n == d` edge flagged as owed an isomorphic re-check).
- **Class assembly:** the full `MyPCA` class taught line-by-line (**not** chat-coded, per the learner's new preference). Line-by-line check-back (a)–(d): (a) FAIL — "np.cov by default treats columns as features" (the default is `rowvar=True`, rows-as-variables), repaired in-turn; (b)/(c)/(d) PASS.
- **Race vs sklearn** (seed = 3, n = 200, cov `[[4,2],[2,1.5]]`, k = 1): explained variance 4.98024987 on both arms, components exact sign flips, max signed coordinate gap 13.201563505, max magnitude gap 8.881784197e-16 ⇒ **tie up to sign**.
- **Learner-initiated pokes sealed:** the 13.2 reading (= 2× the biggest coordinate = the cloud's own size, a label mirror, not information loss) plus the caveat that sign-sensitive thresholds must be restated as `|score|`; and variance non-negativity — variance = the average of squared deviations ⇒ `uᵀCu` = projected variance ⇒ C is PSD ⇒ eigenvalues ≥ 0, consolidated in their own words.
- **Exit ticket 3/3** (grade-audit agreed, all `sure`): X1 sign flips/magnitudes to float noise · X2 variance = average of squared deviations · X3 rows-as-variables default, `rowvar=False` for points-in-rows — the (a) repair stuck. PCA mastery → 1.00.
- **New durable learner preference (2026-10-03):** **no code written in chat** — code carrying conceptual insight is taught/walked by the Tutor, the learner reasons in prose, and from-memory builds happen in their own environment and arrive as artifacts or prose descriptions. Now recorded in `Core/💡 Learning Profile.md` (Workflow Preferences) as well as the lesson/record.

## Writes

- **Wiki (3 new pages, 1 enriched):**
  - `Knowledge Wiki/wiki/PCA (Dimensionality Reduction).md` — the 5-step recipe with the why of each step, the NumPy idioms (`np.cov(Xc, rowvar=False)`; `eigh` ascending with eigenvectors as columns; `order = vals.argsort()[::-1]`; `V = vecs[:, order[:k]]` d×k; `Xp = Xc @ V` n×k), the three layout detectors (shape / `rowvar` / slice), the two silent failures (`components_`, `transform`), the variance-as-importance assumption and its limit, open questions (round cloud, curse of dimensionality, `n == d`), and the learner's own phrasings.
  - `Knowledge Wiki/wiki/PCA Sign Ambiguity (svd_flip).md` — eigenvectors are defined up to sign; what is immune and what flips as a pair; the seeded race table; why a 13.2 signed gap is harmless (2× the biggest coordinate, a label mirror); the `|score|` threshold caveat; `svd_flip` as a cosmetic convention.
  - `Knowledge Wiki/wiki/Variance is Non-Negative (PSD Covariance).md` — squared deviations ⇒ `uᵀCu ≥ 0` ⇒ PSD ⇒ eigenvalues ≥ 0; λ = 0 means zero spread; scope notes (PSD is not a property of all symmetric matrices; `n < d` singularity).
  - `Knowledge Wiki/wiki/Covariance and correlation.md` — **enriched** with an "In NumPy" section: `np.cov(Xc, rowvar=False)` features-as-variables, the `rowvar=True` default trap, the `1/(n-1)` normalization, and cross-links to the three new pages.
  - `Knowledge Wiki/index.md` — three new Concepts links; `Knowledge Wiki/log.md` — today's entry.
- **Concepts:** no new rows — the Dimensionality Reduction section stays at 3 (`Variance & Covariance`, `Eigenvalues & Eigenvectors`, `PCA (Dimensionality Reduction)`; **38 live concepts**). `PCA (Dimensionality Reduction)` **enriched** with the assembly + race + the `rowvar` slip and **synced to Attempts.json** (`last_reviewed` 2026-10-03, `next_review` 2026-10-16 → **2026-11-02**, mastery 1.00, `interval_index` 3, 6 consecutive correct); `Eigenvalues & Eigenvectors` **synced** (2026-10-02 → 2026-10-03; 2026-11-01 → **2026-11-02**); `Variance & Covariance` **annotated** with the PSD reinforcement (no attempt logged today — dates unchanged at 2026-10-02 / 2026-11-01, matching Attempts.json). No `Attempts.json` edit was needed: the Tutor logged every attempt via `ops.py attempt`.
- **Mistakes:** one **new** row — `2026-10-03 | PCA (Dimensionality Reduction) | deviation` (the `np.cov` `rowvar=True` default stated backwards; repaired same turn; locked by exit ticket X3) — status `review`, retries 1, next retry **2026-11-02**, realigned to Attempts.json. Judged **not** a double-log: it is a different item from the `2026-10-02` PCA row (the `eigh` output layout / `[::-1]` collision). That older row was **advanced** in the same pass — its item came back clean at warm-up W1/W2 and in line-by-line (b)/(c) → `review`, retries 1, next retry 2026-11-02.
- **Position:** `MISSION.md` (Position), `CURRICULUM.md` (Phase note + row 10 + the Phase-1 exit line), `Core/💡 Learning Profile.md` (Last-Updated block / Current Focus / Current Position / Sequencing / Workflow Preferences) and `📚 Active Concepts.md` (metadata Last-Updated line, Live System Notes pointer, Mastery-Summary AIEFS bullet, L10 section header) all now read **P1 L10 Dimensionality Reduction — in-progress, paused at Checkpoint 2/6, mini 3/4 (CP1 sealed 2026-09-30; CP2 minis 1–2 sealed 2026-10-02; mini 3 sealed 2026-10-03) as of 2026-10-03**; resume **CP2's single practice (re-shaped: from-memory write in the learner's own environment, audited by the seeded race + line-by-line rubric)**, then CP3. Row 10 stays **in-progress** (partial handoff — never `done`).
- **Marker / digest:** `Core/Pending Ingest.json` **cleared** (partial handoff — the marker only). The Scout digest `Learning System/.tmp/context-01a0d78c-…-dimensionality-reduction.json` is **kept** per partial-close, and the lesson file + curriculum row stay **in-progress**.

## State audit

Baseline **0 errors / 5 warnings** → post-write **0 errors / 1 warning**. Fixed here with the `STATE_AUDIT_FIXES` hints: the two `attempts_sync` warnings (E&E 2026-11-01 → 2026-11-02; PCA 2026-10-16 → 2026-11-02) and the `pending_ingest` marker. Remaining, deliberately: the **kept Scout digest**, now **8 days old** — past its 7-day TTL, so the audit's own hint applies: **re-scout before teaching L10 again** (it is kept only because this is a `/pause` ingest, not a final one).

## Surfaced, not fixed

1. **Aged Scout digest (8 days, TTL 7d).** The digest is kept per the partial-close rule, but it has outlived its TTL; when the lesson resumes, re-scout rather than trusting the cached synthesis.
2. **`Curse of dimensionality`** (probe Q2, "I don't know", genuinely new material) still has **no** Active Concepts row and no Attempts entry — not in the handoff `concepts[]`, so no row was invented; it remains in the lesson's open questions and surfaces at CP3.
3. **`n == d` shape-detector edge** (flagged at warm-up W3, isomorphic re-check owed) is carried in the lesson file, the new `PCA (Dimensionality Reduction)` wiki page (Open questions), and the PCA row — it should fold into the CP2 practice.
4. The seven fetched L10 source bodies under `raw/sources/2026-09-25 - dimensionality-reduction - *` are now **partly** consumed by the three new pages; the t-SNE / UMAP bodies still wait for CP4–CP5.
