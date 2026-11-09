# Session — Information Theory Ingest (CP3) — 2026-09-12

Partial ingest (lesson paused at Checkpoint 3/6). Source: `Lessons/Lesson — Information Theory — 2026-09-11.md` + teaching note `Sessions/Session — Information Theory (P1 L09) — 2026-09-11.md` (Resume 2 section + CP3 exit ticket). Handoff: `Core/Pending Ingest.json` (`partial: true`, concepts: Cross-entropy (H(P,Q), CE loss, NLL)).

## Ingested (0 new)

None — no new row was needed once the overlap check came back positive.

## Enriched (1, aiefs, developing)

- **Cross-Entropy from NLL** (existing row line 65; existing page `wiki/Cross-Entropy from NLL.md`)
  - **Overlap check** — one `ops.py bundle` with the alternation regex `cross-entropy|CE|NLL|negative log-likelihood|KL|divergence|floor|log loss` over `Core/📚 Active Concepts.md` and the wiki: hits on the Active Concepts row `Cross-Entropy from NLL` (line 65, aiefs, concept, developing) and the page `Cross-Entropy from NLL.md`; the wiki also holds `Negative Log-Likelihood (NLL).md` and the two P1 L09 pages (`Information Content (Surprise)`, `Entropy (Average Surprise)`), which already cross-link to the cross-entropy page as their nearest neighbour. → **enrich, do not duplicate**: one concept, two views (P1 L06 loss view + P1 L09 information view).
  - **Added to the page:** the two-distribution definition H(P,Q) = Σ q(x)·(−log₂ p(x)) with an explicit weights-from-truth-Q / surprises-from-model-P reading; the Olah-vs-Rohit/ML letter-convention table with the anchor "the entropy term is always the data's entropy"; the floor rule H(P,Q) ≥ H(Q) with equality iff P = Q; the worked coin (Q = (0.75,0.25), P = fair → H(P,Q) = 1.0 bit, H(Q) ≈ 0.811, H(P) = 1.0, gap ≈ 0.189) with the "floor ≠ model's H(P)" misconception called out; the KL bridge KL(Q∥P) = H(P,Q) − H(Q) as a labelled CP4 preview; units (bits vs nats); nearest-neighbour and index/summary lines. The existing loss-view content (one-hot collapse to −log ŷ_correct, softmax gradient, PyTorch `CrossEntropyLoss` behaviour) is retained and extended.
  - **Row change:** `last_reviewed` 2026-09-09 → **2026-09-12**; `next_review` **2026-09-15** (+3d, unchanged value — the concept stays on a short interval: the −log sign inversion recurred and the floor misconception is fresh); `Last Q Type` unchanged (`discriminative`); `Source` extended with P1 L09 + Olah + PyTorch `CrossEntropyLoss`; insight cell now carries H(P,Q), the conventions, the floor and the coin numbers.
  - **Arithmetic verified in-session** (python): H(Q) = 0.8113, H(P) = 1.0, H(P,Q) = 1.0, KL = 0.1887; E3 coin H(P,Q) = 1.8415, H(Q) = 0.4690, H(P) = 0.8113; swapped-letters CE = 1.2075; 0.8113 bits = 0.5624 nats.

## Untouched

- CP1 row `Information Content (Surprise)` and CP2 row `Entropy (Average Surprise)` (2026-09-11) — rows and pages unchanged.
- `Core/Attempts.json` and `Core/🧯 Mistakes.md` — no new rows written (the floor misconception row of 2026-09-12 already exists; a duplicate would double-count).
- **CP4 (KL divergence) NOT banked** — taught but never answered or practiced; recorded only as a labelled preview on the cross-entropy page.
- Curriculum row stays **in-progress** (never `done`).

## Naming notes for the Tutor (bookkeeping, not content)

1. `Pending Ingest.json`, `Mistakes.md` and `Attempts.json` use the label **"Cross-entropy (H(P,Q), CE loss, NLL)"** while the wiki page and Active Concepts row are named **"Cross-Entropy from NLL"** — the same concept. The canonical row/page name was left unchanged (renaming would break inbound links in `Entropy (Average Surprise)`, `Information Content (Surprise)` and `index.md`); the page header now records the alias. `Attempts.json` hence holds two keys: `Cross-Entropy from NLL` (09-06 fail, 09-08 pass, 09-11 fail; next_review 2026-09-14) and `Cross-entropy (H(P,Q), CE loss, NLL)` (two 09-12 passes, mastery 0.80, next_review 2026-10-12). The row's 2026-09-15 deliberately follows the short ingest interval for an unstable concept; the next logged `ops.py attempt` under the canonical name will recompute it.
2. `Attempts.json` also held a stray key **"Entropy (expected surprise)"** (2026-09-12 warm-up) alongside the row `Entropy (Average Surprise)` — same concept, two names.
2b. **Resolved 2026-09-12 (parent), after the review gate flagged it:** both alias keys were MERGED into the canonical names — `Cross-entropy (H(P,Q), CE loss, NLL)` → `Cross-Entropy from NLL`, and `Entropy (expected surprise)` → `Entropy (Average Surprise)` — with attempt histories merged chronologically and the interval state re-run mechanically (per-step `interval_index` clamp, +1 per pass, +2 on the second consecutive pass, −1 per fail). Both now sit at `interval_index 3` → `next_review 2026-10-12`; the Active Concepts rows for `Cross-Entropy from NLL` (was 2026-09-15) and `Entropy (Average Surprise)` (was 2026-09-18) were aligned to match. `Core/Learner History.md` was regenerated: no duplicate rows remain (previously the same concept appeared twice, once mis-filed under the frozen SWE-era heading), and the frozen-era totals returned to `swe 66` from an inflated 68.
2c. Counting definitions (not a contradiction): `📚 Active Concepts.md` "28 live concepts" counts **table rows**; the generated `Learner History.md` `aiefs 26` counts concepts with an `Attempts.json` entry (2 of the 28 rows have no attempts logged yet), so the two figures differ by construction.
2d. Near-term recall of both concepts is still guaranteed despite the long sidecar interval: `🧯 Mistakes.md` holds due rows for them (Entropy row 2026-09-11 → retry 2026-09-17; Cross-Entropy rows 2026-09-11/2026-09-12 → retries 2026-09-14/2026-09-19), and mistake slots are priority-1 in the review queue.
3. Stale checkpoint counter corrected in the state files: `CURRICULUM.md` (two places) and the Active Concepts IT section header said `paused 2/6` while the lesson file says `paused at Checkpoint 3/6`; both now read 3/6. Status stayed `in-progress`.

## Lesson status

In-progress, **paused 3/6**, resume at **CP4 — KL divergence** (CP4 idea block re-emitted 2026-09-14, fact-check PASS 5/5 — see Session — Information Theory (P1 L09) — 2026-09-11.md §Resume 3; next: invite questions, then issue CP4 practice. CP4's teaching block was never practiced). `Core/Pending Ingest.json` cleared. The Scout digest `context-p1l09-information-theory.json` is **not present in this working copy** (`Learning System/.tmp/` does not exist; the directory is gitignored) — nothing was deleted, and the 7-day TTL could not be checked here.

Interleaving: n/a (ingest, not review — 1 concept enriched; next review 2026-09-15).

## Review gate (2026-09-12)

- **Cycle 1** (pass 1, `lesson_ref` = the lesson file): **ISSUES** — 2 medium (the Olah convention attributed to "P1 L09" although the cited `en.md` uses the ML lettering; a flat "false" for `H(P,Q) ≥ H(P)` where the page's own coins satisfy it) + 2 low (envelope `source_url` slug typo; imperative strings verified benign).
  - Fixed: conventions table relabelled (**Olah / this lesson as taught** vs **Rohit `en.md` source doc + most ML code**), an explicit "the letters here are a deliberate deviation from the cited source" paragraph added, the sentence now reads "not a valid floor rule — the floor is H(Q)" with the Q=(0.99,0.01) / P=(0.9,0.1) counterexample (0.184 < 0.469), and the correct source URL added to the page's Source section.
- **Cycle 2** (pass 2, updated content): **ISSUES** — 1 medium: the page said KL "has not been taught", while the lesson file / CURRICULUM / this note say CP4 *was* emitted but never practiced.
  - Fixed after cycle 2: the KL section heading and last sentence now read "preview only (CP4 was emitted, never practiced, so it is not banked)". **No third in-cap pass was run** (learning-review 2-cycle cap) — this flag is surfaced here, not silently closed.
- **Post-cap re-check (parent-initiated, run 15f4d3f1):** the post-fix *wiki text* was re-verified — the page came back **clean** (no high/medium finding). Its single medium finding was a position-of-record split outside the page (`MISSION.md`, `💡 Learning Profile.md`, `Active Concepts.md` still at 2/6/CP3 and routing to L08); fixed by the parent in commit `47fdae7`. Artifact: `Reviews/Quality Gates/information-theory-p1l09-cp3-pass3-parent-recheck-2026-09-12.json` (labelled a post-cap re-check, not a third in-cap cycle).
- **Verdict files:** `Reviews/Quality Gates/information-theory-p1l09-cp3-pass1-2026-09-12.json`, `Reviews/Quality Gates/information-theory-p1l09-cp3-pass2-2026-09-12.json`

## Position-of-record reconciliation (2026-09-12, post review-gate)
The review-gate (pass 3, post-fix text) cleared the wiki page but flagged a state split: `MISSION.md:14`, `💡 Learning Profile.md:13/19/27` still said "paused 2/6, resume CP3", and `📚 Active Concepts.md:22/:42` still routed the next lesson to **L08** ("paused 2/5") even though L08 is DONE (2026-09-10). Fixed by the parent: all four files now read **L09 Information Theory paused at Checkpoint 3/6, resume at CP4 — KL divergence**, and the L08 resume pointer was replaced with L08 ✅ done. CURRICULUM.md and the lesson file already read 3/6/CP4, so the position now agrees across MISSION.md · CURRICULUM.md · Learning Profile.md · Active Concepts.md · lesson file.
