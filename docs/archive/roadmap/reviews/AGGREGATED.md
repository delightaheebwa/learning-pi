# Review phase — aggregated findings (REVIEW orchestrator, 2026-10-08)

Reviewers run: `R-P0`, `R-P1`, `R-P2` on `opencode-go/muse-spark-1.3-contributor`.
Raw findings: [`P0.md`](P0.md), [`P1.md`](P1.md), [`P2.md`](P2.md). All findings are reproduced here;
none are dropped silently.

Severity is the reviewer's. **Decision** is the orchestrator's: `accept` (implemented), `partial`
(some safe part implemented, remainder recorded), `defer` (recorded, not implemented), `reject`
(factually wrong — none in this pass).

Ground rules for every fix: revise door (contract first, same commit) for gate behavior; additive;
small commits; a test for every behavior change; `learn-check --no-load --with-sidecars` and
`ops_test` must stay green.

---

## Deduplicated master list

### HIGH

#### H1 — Solo flow leaks teaching on three paths (none turn / retry-cap dump / grade repair tail)
- **Sources:** P0-[HIGH] §1; P0-[HIGH] §2 (judge path) is the same defect on the judge branch.
- **Where:** `engine.ts:561-566` (solo block), `:925` (legacy cap), `:1413` (judge cap); `solo.md:9`.
- **Evidence:** live probes — (1) `[[TURN:none]]` with novel teaching prose in `[[FLOW:solo]]` renders;
  (2) a solo `claims` re-emitted 3× reaches the cap and renders `⛔ UNVERIFIED` with content because
  `SOLO_NO_TEACHING` is not exempt from `G-retry-cap`; (3) a solo `[[TURN:grade]]` with an agreeing
  grade-audit plus a fact-checked repair tail renders the repair.
- **Impact:** P0.5's headline "teaching impossible by construction" fails open; the independence
  signal P0.4/P0.5 exist to produce is contaminated.
- **Decision: accept (partial).** Implemented: (a) `SOLO_NO_TEACHING`/`SOLO_NO_AIDS` are exempt from
  the retry-cap dump and withhold outright; (b) a solo `[[TURN:none]]` whose text carries hard facts
  is withheld as `SOLO_NO_TEACHING` (deterministic proxy for embedded teaching); (c) a solo `grade`
  turn carrying a fact-checked teaching tail is withheld. Residual (recorded, not implemented):
  **fact-free** teaching prose on a solo `none` turn still renders — no deterministic
  "is-this-prose-teaching" detector exists on the legacy path; the judge path now carries a
  deterministic solo pre-check (H2). Tests: `solo retry cap withholds teaching outright`,
  `solo none turn with hard facts is withheld`, `solo grade repair tail is withheld`.

#### H2 — Solo and claim-completeness guards vanish on the judge path
- **Source:** P0-[HIGH] §2.
- **Where:** `engine.ts:1057-1450` (`applyAssessment`); `gate-core/judge/*` (no solo references).
- **Evidence:** `grep SOLO gate-core/judge/` → 0 hits; the deterministic solo/`missingHardFacts`
  blockers exist only in `legacyMessageEnd`, so with a judge configured the guarantees degrade to
  model behavior while `learn-check` stays green (its solo tests run the legacy path).
- **Impact:** P0.2/P0.5 deterministic guarantees silently disappear on the judge path.
- **Decision: accept.** Implemented: `applyAssessment` computes the solo block and
  `missingHardFacts` incompleteness **before** consulting the judge verdict and blocks
  deterministically (`SOLO_NO_TEACHING`/`SOLO_NO_AIDS`; a claims turn whose bound draft has unlisted
  hard facts is withheld `CLAIMS_INCOMPLETE`). Tests: `judge path withholds a solo teaching claims
  turn`, `judge path withholds claims with an unlisted hard fact`.

### MEDIUM

#### M1 — `missingHardFacts` containment is substring-based (evadable) and blind to small integers
- **Source:** P0-[MEDIUM] §3.
- **Where:** `primitives.ts:507-512`.
- **Evidence:** `missingHardFacts('n=200', …n=2000)` → `[]` (`"200" in "2000"`); 1–2 digit integers
  (`k=3`, `PPL is 4`) are never extracted.
- **Decision: accept (partial).** Implemented: containment is now token-boundary–aware, so a longer
  number no longer subsumes a shorter one. Small-integer extraction is deliberately **not** extended
  (would false-positive on list markers/enumerations); the blind spot is documented in `fact-check.md`
  and `AUDIT-ROADMAP.md` P0.2 so the verifier owns it explicitly.
- Test: `hard fact is not subsumed by a longer number`.

#### M2 — `extractHardFacts` false positives (`3,000` → `000`; year `1800`)
- **Source:** P0-[MEDIUM] §4.
- **Where:** `primitives.ts:481-500`.
- **Evidence:** `'3,000 sentences'` → `["000"]`; `'In 1800 …'` → `["1800"]` (only 19xx/20xx excluded);
  `'$5 … $10'` → `["5 and pays"]` (currency-pair regex).
- **Decision: accept (partial).** Implemented: comma-grouped thousands are no longer split into
  fragments (`3,000` is not extracted as `000`), and the calendar-year carve-out covers `1[0-9]\d{2}`
  / `20\d{2}` (so `1800` is treated as a year, not a hard fact). The `$…$` currency false positive is
  **deferred** — narrowing the math-delimiter regex risks dropping real LaTeX facts; documented.
- Tests: `comma-grouped thousands are not treated as a hard fact`, `four-digit years are not hard
  facts`.

#### M3 — Provenance lint accepts malformed/meaningless markers (`--check` cannot fail on content)
- **Source:** P0-[MEDIUM] §5.
- **Where:** `wiki_provenance.py:34-53,63-81`.
- **Evidence:** `status=bogus` → `"unverified"` (passes); `status=verified | source=legacy |
  verified-by=—` (no evidence of any check) → `"verified"`; marker mid-file accepted; `scan()`'s
  `invalid` list is dead code; no unit tests.
- **Decision: accept.** Implemented: `read_status` returns the raw status; an unknown status is
  reported as malformed and `--check` fails; `status=verified` requires non-empty `source` and
  `verified-by` and a valid `date`; the marker must sit in the first 5 lines; `scan()` reports
  `invalid`. Tests added in `scripts/wiki_provenance_test.py` (wired into the E2E-sidecar check and
  run directly).
- **Note:** all 220 live pages carry `status=unverified`, so `--check` stays green.

#### M4 — Wiki trust inversion is labelling, not enforcement (F2 path still open)
- **Source:** P0-[MEDIUM] §6.
- **Where:** `learning-system/AGENTS.md:228-248`, `Knowledge Wiki/AGENTS.md:25-50`,
  `llm-wiki/SKILL.md`.
- **Impact:** Scout/step-0 still read wiki pages as context; nothing gates on the marker.
- **Decision: defer.** A flow-level mechanism (require `verified`-or-source re-grounding for
  load-bearing claims, surface provenance in Scout digests) is an architectural change beyond a safe
  review-phase edit. Recorded here and in `AUDIT-ROADMAP.md`; the ROIADMAP P0.6 line is softened to
  "label contamination" (see M-lite below).

#### M5 — P0.1 State rung reuses the unguarded `none` channel; "just tell me" can still bypass generation
- **Source:** P0-[MEDIUM] §7.
- **Where:** `.pi/skills/learning-teach/SKILL.md:235-239`, `engine.ts:770-795`.
- **Decision: defer (partial).** The procedural `none` prompt is now covered on the solo path by H1,
  but on the normal teach path a framing-laden prompt tagged `none` still renders. The
  measurement-only nature of `just_tell_me` (no compensation) is documented in `AUDIT-ROADMAP.md`;
  a re-probe rule is out of scope for a review pass. Recorded.

#### M6 — Ledger is best-effort silent and unbounded
- **Source:** P0-[MEDIUM] §8.
- **Where:** `engine.ts:90-105`, `pi-adapter/index.ts:236-252`.
- **Evidence:** write failures swallowed; no rotation; ledger dir created without `0700`; no model
  field.
- **Decision: partial.** Implemented: the ledger directory is created with mode `0700`. Rotation /
  write-failure counter / model field are **deferred** (schema/operability change); recorded.

#### M7 — `stability` contradicts "never a false 0"; `--mode`/`--confidence` unvalidated
- **Source:** P0-[MEDIUM] §9.
- **Where:** `ops.py` `compute_dimensions`, `do_attempt` arg parsing.
- **Evidence:** `stability = min(3, interval_index)` is always an int; `--mode Solo` silently records
  a non-`solo` mode `independence_ok` ignores.
- **Decision: accept.** Implemented: `stability` is `None` when the entry has no attempts (matching
  the docstring); `do_attempt` validates `--mode ∈ {normal,solo}` (case-insensitive) and
  `--confidence ∈ {sure,hunch,no-idea}`, exiting 2 on bad input. Tests:
  `test_stability_is_none_without_attempts`, `test_attempt_rejects_bad_mode`,
  `test_attempt_rejects_bad_confidence`.

#### M8 — `ops.py attempt --prereq` replaces the edge list instead of merging it
- **Source:** P1-[MEDIUM] §1.
- **Where:** `ops.py` `do_attempt`: `entry["prereqs"] = [p for p in prereqs if p]`.
- **Impact:** normal use silently drops earlier prerequisite edges; a blocking fuzzy prereq can
  disappear.
- **Decision: accept.** Implemented: merge with the existing edges
  (`sorted(set(existing) | set(prereqs))`); `prereqs --set` keeps replace semantics. Test:
  `test_prereq_attempt_merges_existing_edges`.

#### M9 — Far-transfer items are never scheduled by deterministic code
- **Source:** P1-[MEDIUM] §2.
- **Where:** `ops.py:574-577` (`_question_type` alternates only definitional↔discriminative);
  review skill asks for a transfer item "every third review".
- **Impact:** the "authoritative, use verbatim" queue can never contain the item the skill asks for;
  the Tutor must disobey its own queue rule.
- **Decision: accept.** Implemented: `_queue_entry` schedules a deterministic `transfer-far` item for
  `concept`/`design` review entries that have no transfer attempt on record and whose attempt count is
  a multiple of 3 (every third review). Test: `test_queue_schedules_far_transfer_on_cadence`.

#### M10 — Feynman "mandatory beat" is prompt-mandatory, code-advisory
- **Source:** P1-[MEDIUM] §3.
- **Where:** `learning-system/SKILL.md` step 6, `review-clerk.md`, `learner_history.py:tag()`.
- **Decision: defer.** The outcome gate is hard (`tag()` cannot return `solid` for concept/design
  without `feynman_pass`, tested). Enforcing the *elicitation beat* needs a new gate/clerk contract
  change at the review close; recorded as a known gap, not silently dropped.

#### M11 — Hard-fact withhold fires on content, not verification state (over-withholds verified turns)
- **Source:** P1-[MEDIUM] §4.
- **Where:** `engine.ts` legacy + judge retry-cap blocks.
- **Impact:** a verified claims turn blocked only on `NO_SCOUT_CONTEXT`/`NO_REVIEW_CONTEXT` is
  withheld outright, suppressing verified numbers.
- **Decision: accept.** Implemented: at the cap, hard-fact withholding triggers only when the block
  set implicates verification (`FACT_CHECK_*`, `CLAIMS_INCOMPLETE`, `NO_FACT_CHECK_MATCH`); a
  context-only block still degrades to `⛔ UNVERIFIED`. Test:
  `retry cap delivers verified hard-fact prose blocked only on context`.

#### M12 — Red-team harness measures gate plumbing, not verifier judgment — headline overstates it
- **Source:** P1-[MEDIUM] §5.
- **Where:** `test/redteam/redteam_test.mjs`; `AUDIT-ROADMAP.md` P1.8.
- **Decision: accept.** Implemented: added a documented **known-limitation** case (a listed-but-false
  claim with a synthetic `PASS` receipt is asserted to *render*, proving the harness can observe the
  F1/F4 path but does not detect it) and reworded the roadmap line to "measures deterministic catch
  paths + receipt plumbing; does not measure verifier judgment".

#### M13 — `--confidence` end-to-end recording relies on LLM obedience with no check
- **Source:** P1-[MEDIUM] §6; P1-[LOW] §8 (`normalize_confidence` accepts any string) is the same gap.
- **Where:** `ops.py` `normalize_confidence`, `compute_calibration`.
- **Decision: accept.** Implemented: `compute_calibration` reports an `untagged` count so dropped
  confidence is visible, and `do_attempt` rejects unknown confidence levels. Tests:
  `test_calibration_reports_untagged_count`, `test_attempt_rejects_bad_confidence`.

#### M14 — State-gate "blocking" degrades to UNVERIFIED after the retry cap — contract overstates it
- **Source:** P2-[MEDIUM] §1.
- **Where:** `engine.ts:877` (legacy), `:1305` (judge); `contracts/learning-core.json:193-200`.
- **Evidence:** both cap paths withhold only `claims`+hard-fact or solo; a `none` close summary with a
  persistent `STATE_AUDIT_ERRORS` renders `⛔ UNVERIFIED` after 2 retries.
- **Decision: accept.** Implemented: the `G-state-audit-blocking` statement now discloses the
  retry-cap degradation explicitly ("subject to the standard retry cap, after which it degrades to
  UNVERIFIED"), and a golden test pins the cap behavior. Test:
  `state audit errors degrade to unverified after the retry cap`.

#### M15 — Demotion whitelist still matches bare keywords (`provenance`)
- **Source:** P2-[MEDIUM] §2.
- **Where:** `primitives.ts:798-800` (`BOOKKEEPING_PATH_RE`).
- **Evidence:** `location: "Knowledge Wiki/wiki/Backprop.md provenance marker missing"` is demoted.
- **Decision: accept.** Implemented: the whitelist is anchored to path-shaped locations (must contain
  a `/` and a known extension/prefix or a state-dir name), so a content path embedding a bookkeeping
  word is never demoted. Test: `content path embedding a bookkeeping word is not demoted`.

#### M16 — Review-close half of the state gate has no test
- **Source:** P2-[MEDIUM] §3.
- **Where:** `golden_test.mjs:198-225`; `engine.ts:555-556`.
- **Decision: accept.** Implemented: a golden test drives `[[FLOW:review]]` through
  review-clerk + review-session-audit with a state-audit error (expects `STATE_AUDIT_ERRORS`) and one
  with warnings (expects the banner). Test:
  `review close with state audit errors is withheld`.

#### M17 — Scout TTL is a prompt instruction, not enforcement
- **Source:** P2-[MEDIUM] §4.
- **Where:** `learning-teach/SKILL.md:147`; `audit_state.py:437-469`.
- **Decision: defer.** The audit deliberately keeps a stale digest at `warn` (hard errors cannot be
  fixed retroactively and would dead-end the close). A teaching-time deterministic TTL check is a
  gate/state design change; recorded as a known gap and the roadmap claim is softened.

#### M18 — `ops.py amend` accepts semantically invalid values (negative hints, far-future re-date)
- **Source:** P2-[MEDIUM] §5.
- **Where:** `ops.py` `do_amend`.
- **Decision: accept.** Implemented: `--field hints` rejects a negative value; `--new-date` in the
  future (beyond a small skew window) is rejected; both exit 2. Tests:
  `test_amend_rejects_negative_hints`, `test_amend_rejects_future_date`.

### LOW

| # | Source | Finding | Decision |
|---|---|---|---|
| L1 | P0 §10 | `G-infer-claims-from-bound` still says ≥85% | **accept** — contract/comment updated to ≥95% + ≤12-token tail |
| L2 | P0 §11 | tail bound untested on the allow side | **accept** — added `reordered/punctuated re-emission renders` test |
| L3 | P1 §7 | `grade-mcq` accepts arbitrary non-letter tokens | **accept** — validate against `^[A-E]$`; test `test_grade_mcq_rejects_non_letter_token` |
| L4 | P1 §9 | P1.7 section-level `status=learner-note` not machine-checkable | **defer** — page-level provenance is checked; section marker is convention (matches the brief "no code gate needed") |
| L5 | P1 §10 | roadmap P1.2 says "only free-recall" to grade-audit | **accept** — reworded to "MCQ verdicts precomputed with `grade-mcq`; `grade-audit` verifies the batch" |
| L6 | P2 §6 | `looksLikeIngestSummary` arms the gate on any message with "state audit"/"files written" | **defer** — narrowing risks missing the real close; low likelihood, pre-existing shape |
| L7 | P2 §7 | `OPENWEBUI.md:10` still says "the canonical guide" under the FROZEN banner | **accept** — reworded to "legacy guide" |
| L8 | P2 §8 | prereq link surfaced, not enforced — roadmap wording stronger than code | **accept** — roadmap P2.8 softened to "surfaced in `queue` for the Tutor to re-derive first" |

---

## Summary

- Findings: **2 HIGH, 16 MEDIUM, 8 LOW** (22 across three checkpoints, after merging the duplicate
  judge-path solo item into H1/H2).
- Implemented: **H1 (partial), H2, M1 (partial), M2 (partial), M3, M6 (partial), M7, M8, M9, M11,
  M12, M13, M14, M15, M16, M18**, plus all LOW except L4/L6.
- Deferred with reason: **H1 residual** (fact-free solo `none` teaching), **M4, M5, M10, M17, L4, L6**.
- Rejected: none (no finding was factually wrong).
