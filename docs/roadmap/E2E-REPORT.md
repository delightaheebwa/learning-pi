# E2E Report — final end-to-end verification (2026-10-08)

Final stage of the audit cascade (`P1 → P2 → P3* → REVIEW → E2E`). This report tests the
claims in [`AUDIT-ROADMAP.md`](../../AUDIT-ROADMAP.md) against the integrated system and records
what actually works, what does not, and what was fixed. No next stage follows.

## 0. Environment

| | |
| --- | --- |
| Date (UTC) | 2026-10-08T~17:50Z |
| `learning-pi` | `5a31bed54f25f707a6a464ac3c6c4b442d60e64f` (`main`, clean, in sync with `origin/main`) |
| `learning-system` | `9a06820c781b7e78c2d573f1b0ed63225efc9d26` (`main`, clean, in sync with `origin/main`) |
| E2E fix commit | `d8b682f` (learning-pi) |
| Runtime | deno 2.9.6; pi pinned by `versions.lock.json`; default provider `opencode-go/kimi-k2.6`; judge `gemini-3.5-flash-lite` (key present in `~/.pi/agent/auth.json`) |
| Live model path | **Ran.** Sandboxed smoke journeys executed with real models (`opencode-go`, judge via gemini auth). Network reachable (`api.opencode.ai` 200). |

## 1. Static / offline suites — all pass

| Check | Command | Exit | Evidence |
| --- | --- | --- | --- |
| pi learning layer (offline) | `scripts/learn-check --no-load --with-sidecars` | **0** | `learn-check: OK`; 193 gate assertions; 45/45 contract invariants covered |
| pi learning layer + load probe | `scripts/learn-check --with-sidecars` | **0** | `PASS load-probe: pi answered; 8 prompts + sentinel loaded; no load errors` |
| ops sidecar suite | `python3 -m unittest scripts.ops_test` | **0** | `Ran 59 tests … OK` |
| wiki provenance | `python3 scripts/wiki_provenance.py --check` | **0** | `220 pages … unverified 220 / missing 0` |
| state audit | `python3 ~/learning-pi/pi/audit_state.py --root ~/learning-system` | **0** | `0 error(s), 2 warning(s)` (2 warnings: stale 13-day Scout digest; `.tmp` digest present) |

Tail of learn-check:

```
PASS ops_test (sidecar, read-only)

learn-check: OK
```

## 2. Targeted feature verification (P0/P1/P2/P3 claims)

| Claim | How exercised | Result |
| --- | --- | --- |
| P0.2 hard-fact completeness (`CLAIMS_INCOMPLETE`) | `deno test/gate_test.mjs` → `draft with an unlisted hard fact is withheld`, `hard fact listed in claims is allowed`; `test/redteam` | **PASS** |
| P0.2 tail bound (`G-draft-tail-bound`) | `gate_test.mjs` → `unverified tail beyond the draft is withheld`, `reordered verified draft still renders`; contract coverage = 2 tests | **PASS** |
| P0.2 correctness fixes (M1/M2) | `gate_test.mjs` → `hard fact is not subsumed by a longer number`, `comma-grouped thousands are not treated as a hard fact`, `four-digit years are not hard facts` | **PASS** |
| P0.3 always-on claim-level ledger | `gate_test.mjs` reads NDJSON and asserts a `fact_check` line with `claims[]` + `envelopeHash`; test ledger has **341** such lines (995 receipts, 533 with claims, 732 with hash) | **PASS** (deterministic) · see finding F3 for live-coverage caveat |
| P0.5 `/solo` withholds claims + viz, allows the batch | `gate_test.mjs` → `solo flow withholds a teaching claims turn` (`SOLO_NO_TEACHING`), `solo flow withholds a visualization` (`SOLO_NO_AIDS`), `solo flow allows the closed-book quiz batch`, `solo first quiz requires a review-scout run`; judge-path `solo … claims turn` withheld; `solo retry cap withholds teaching outright`; `solo none turn with hard facts is withheld`; `solo grade repair tail is withheld` (8 contract assertions + 2 judge tests) | **PASS** |
| P0.4 mastery dimensions + independence gate | `python3 -m unittest scripts.ops_test.TestMasteryDimensions` (6 tests) + `ops.py mastery --json` prints six dimensions, `calibration`, `transfer_ok`; `test_independence_gate_blocks_solid_after_a_failed_solo` | **PASS** |
| P1.1 Feynman graduation gate | `TestLearnerHistoryFeynmanGate` (concept can't be `solid` without a pass; memory exempt) | **PASS** |
| P1.2 `q_type` enum + deterministic MCQ | `TestQTypeEnum` (unknown rejected, aliases normalized) + `TestGradeMcq` (mixed/empty/length-mismatch/non-letter) | **PASS** |
| P1.3 prerequisite edges | `TestPrereqs` (fuzzy blocks, open mistake blocks, unknown does not block, `--set` persists) + `--prereq` merges; refusal documented in `learning-teach`/`learning-system` SKILL | **PASS** |
| P1.4 confidence calibration | `TestCalibration` (overconfidence flag, untagged count, mastery surfaces it) + `ops.py calibration` runs (no tagged data yet — grandfathered state) | **PASS** |
| P1.5 transfer dimension | `TestTransferDimension` (far-transfer feeds transfer 3 + `transfer_ok`; fail → 0); deterministic `transfer-far` cadence (`test_queue_schedules_far_transfer_on_cadence`) | **PASS** |
| P1.6 withhold unverified hard-fact claims | `gate_test.mjs` `/golden` — `retry cap withholds a hard-fact claims turn`, `retry cap still delivers non-hard-fact prose`, `retry cap delivers verified hard-fact prose blocked only on context` | **PASS** |
| P1.7 learner-authored wiki | `learner-note` provenance + `## My understanding` documented in `llm-wiki`/`clerk`; page-level provenance checked by `wiki_provenance` | **PASS** (doc/behavior) |
| P1.8 seeded-error red team | `deno test/redteam/redteam_test.mjs` → `REDTEAM: caught 5/5 seeded errors; clean controls 2/2`; asserts its own known limitation (listed-but-false + PASS renders) | **PASS** |
| P0.6/P1.7 wiki provenance | `wiki_provenance.py --check` 220/220; trust order `raw source > verified claim > labelled synthesis > learner note` in `AGENTS.md:231`; malformed-marker lint tests (10) | **PASS** |
| P2.1 state gate blocking | `golden_test.mjs` → `review close with state audit errors is withheld`, `… warnings banners`; contract `G-state-audit-blocking` (3 tests) | **PASS** |
| P2.2 demotion anchored | `gate_test.mjs` → `content path embedding a bookkeeping word is not demoted`, `a real bookkeeping path still demotes`, `content review findings are not demoted by a bookkeeping word` | **PASS** |
| P2.5 `ops.py amend` | `TestAmend` (re-date + reason, field fix, rejects missing reason/unknown field/negative hints/future date) | **PASS** |
| P2.8 misconception→prereq link | `TestMistakePrereqLink` (marker parsed/stripped, absent is empty) | **PASS** |
| P3.1–P3.4 | Deferred by the user (roadmap §P3, no-op forwarder) | **N/A (declared deferred, not falsely claimed)** |

Aggregate gate suites: `gate_test.mjs` **69 PASS / 0 FAIL**, `golden_test.mjs` **32 PASS**,
`judge_test.mjs` (incl. judge-path solo + `CLAIMS_INCOMPLETE`) PASS, `redteam` 5/5 + 2/2.
All 45 contract invariants in `contracts/learning-core.json` are covered by matching passing tests.

## 3. Live journey

A judge/model is configured, so the live path was exercised (not skipped):

| Command | Result |
| --- | --- |
| `python3 harness/e2e-runner.py --tier smoke --jobs 2` | **PASS 5/5** — `audit-smoke` (12.8s), `lesson-smoke` (119.5s), `ingest-smoke` (179.7s), `review-smoke` (108.7s), `viz-smoke` (175.2s) |
| `… --scenario review-smoke` (after fix) | **PASS** (132.0s), real ledger untouched |

`learn-check --e2e --e2e-tier smoke` is the same runner wrapped by the entrypoint; it was invoked
directly to keep the artifacts from the static run intact. The equivalent offline fallback
(`learn-check --with-sidecars`, including the sandboxed load probe) also passed and is reported above.

## 4. Integration / drift

| Check | Result |
| --- | --- |
| `git -C ~/learning-pi status --short` | clean (after `d8b682f`); before the fix: 2 modified files |
| `git -C ~/learning-system status --short` | clean |
| Both repos pushed | yes — `rev-list --left-right --count origin/main...main` = `0  0` in both |
| `contracts/learning-core.json` invariants covered | **45/45** (learn-check), 193 gate assertions |
| Shared-skill drift (`learning-pi/.pi/skills` vs `learning-system/Skills`) | Intended: all four skills differ **by design** — the `learning-system` copies carry the FROZEN/LEGACY banner and lack all P0–P2 pedagogy (solo, learner-authored understanding, provenance). This is exactly the P2.4 canonicalization, not unintended drift. `audit_openwebui.py` could not run (no `OPENWEBUI_API_KEY`). |

## 5. Findings

| # | Severity | Finding |
| --- | --- | --- |
| F1 | **Medium** | **Sandbox E2E leaked into the real gate ledger.** `pi-adapter/makeFileLedger()` defaults to `homedir()/.pi/agent/learning-gate` and ignores `PI_CODING_AGENT_DIR`, so the sandboxed smoke run appended a `viz_audit` line to the *real* `~/.pi/agent/learning-gate/receipts.ndjson` (167 → 168 lines at 17:31:57Z). This breaches the sandbox-isolation intent of CONTRACT S-2/S-5 (provenance source contaminated by test runs). **Fixed** (see §6). |
| F2 | **Low** | `docs/roadmap/STAGE-LOG.md` still listed the P1 row as `_pending_` even though P1 landed (roadmap P1.1–P1.9 with real commits). Documentation lag. **Fixed** (see §6). |
| F3 | **Low / informational** | The always-on claim-level ledger is proven only by the deterministic gate suite (test ledger: 341 `fact_check` lines with `claims[]`+`envelopeHash`). The **real** ledger's 52 `fact_check` entries predate P0.3 and carry no `claims[]`; the live smoke tier exercised the ledger only via the synchronous `viz_audit` path (1 new line). Async `fact-check` receipts did not appear in the ledger during the smoke runs (those scenarios early-stop at or before a verifier receipt). The mechanism is correct; live coverage of the claim-level path is thin and should be re-checked after a real `/teach` session. |
| F4 | **Info** | The frozen OpenWebUI skill copies (`learning-system/Skills/*`) diverge substantially from the canonical `learning-pi` skills; this is the documented P2.4 state. No action taken; deleting the frozen path is a future decision. |
| F5 | **Info** | Legacy state is grandfathered: `ops.py calibration` reports 273 untagged attempts / 0 tagged; no live concept currently records `prereqs`. The P1.3/P1.4 code and tests are correct but have no live data yet — expected, not a defect. |

No stage agent was found to have claimed work it did not do. Deferrals recorded in
`AUDIT-ROADMAP.md` and `docs/roadmap/reviews/AGGREGATED.md` (wiki trust enforcement M4, "just tell
me" compensation M5, Feynman elicitation M10, Scout TTL enforcement M17, fact-free solo `none`
teaching, ledger rotation) are honestly labelled as deferrals, and the E2E checks confirm the
implemented parts work.

## 6. Fixes made

| Commit | Repo | Change |
| --- | --- | --- |
| `d8b682f` | learning-pi | `harness/e2e-runner.py`: set `LEARNING_GATE_LEDGER_DIR` to the throwaway sandbox agent dir so a sandboxed journey never appends to the real ledger (F1). Verified: `review-smoke` passes and the real `receipts.ndjson`/`decisions.ndjson` counts and mtimes are unchanged. |
| `d8b682f` | learning-pi | `docs/roadmap/STAGE-LOG.md`: recorded the P1 commit shas (`957d735 e297dd6 68a70ad c1eac94` / `829f5b9 308cd48 2ed8d8e`) (F2). |

### Left unfixed (recommended next step)

- **F3 live ledger coverage:** run one full real `/teach` (or a `--e2e-tier full` lesson) and confirm
  `~/.pi/agent/learning-gate/receipts.ndjson` gains a `fact_check` line with `claims[]` +
  `envelopeHash`. Owner: next operator; no code change expected.
- **F4 frozen OpenWebUI path:** decide whether to delete it or leave it frozen; run `audit_openwebui.py`
  with an API key to quantify drift if it is ever unfrozen.
- **F5 live data:** confidence calibration and prerequisite edges stay empty until sessions record
  `--confidence`/`--prereq`. The flows already instruct this; monitor.

## 7. Honest verdict

The integrated system does what the audit roadmap claims. Every P0, P1 and P2 item is present and
independently verified: the offline suites are green (45/45 contract invariants, 193 gate assertions,
59 sidecar tests, 220/220 provenance markers), each headline mechanism was exercised with its own
tests and CLI (deterministic hard-fact completeness and tail binding, always-on claim-level ledger,
the AI-free `/solo` flow, multi-dimensional mastery with a failed-solo veto, the `q_type` enum and
deterministic MCQ grading, prerequisite refusal, confidence calibration, wiki provenance, and the
seeded-error red team at 5/5 + 2/2 controls), and the live sandboxed smoke journeys passed 5/5 with
real models. The two issues found were a sandbox leak into the real gate ledger (now fixed and
re-verified) and a stale stage-log row (now fixed); the remaining items are documented deferrals or
grandfathered-data observables, not false claims. The caveat worth carrying forward is F3: the
claim-level ledger is proven deterministically but its live async coverage should be reconfirmed after
a real teaching session. On the audit's own terms — does the learner become more capable and more
independent, and can the system prove it? — the machinery to measure that now exists and is enforced;
the system is honest about the parts it cannot yet measure.
