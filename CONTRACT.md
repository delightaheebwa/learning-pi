# CONTRACT — the behavior the learning system requires

This file defines **what the learning system expects**, independent of the pi
version, the extension packages, or how any of them speak. It is the thing the
update gate protects. Pi may churn; this contract must not change by accident.

Machine-readable form: [`contracts/learning-core.json`](contracts/learning-core.json).
Every invariant there carries an ID, a severity, and the test-name substrings
that must have at least one passing test. `scripts/learn-check` fails if an
active invariant has no passing test, or if a listed test name matches nothing.

## The two doors

| | **Update door** — `harness/pi-safe-update update` | **Revise door** — deliberate change |
|---|---|---|
| Trigger | a newer pi / extension package exists | **you** decide behavior should change |
| This contract | **frozen** | edited first, in the same commit as its tests and implementation |
| Tests | immutable | updated to match the new contract |
| Who reviews | the gate promotes only if every invariant still passes | you approve the contract diff |

The update door may **never** touch `contracts/`, `CONTRACT.md`, or `test/`.
That is what stops an automated repair from silently weakening verification.
Changing behavior is ordinary, deliberate work: edit the invariant, add/adjust
its tagged test, change the implementation, all in one reviewed commit.

## Invariants

### Gate (turn verification)

- **G-grade-requires-agreeing-audit** *(hard)* — a grade turn renders only with
  an agreeing `grade-audit` receipt; a verifier disagreement is rejected and its
  `correct_verdict` is surfaced (`GRADE_MISMATCH`). One batched `items[]`
  envelope may carry several learner answers from a single reply (one entry per
  answer); a mismatch surfaces the per-item corrections. Only the newest grade
  verdict may block: a corrected agreeing re-dispatch supersedes an older
  disagreement, so a stale `agrees:false` receipt cannot poison every later
  grade turn in the flow (the 2026-10-06 review close looped on exactly that).
- **G-grade-repair-dual-verify** *(hard)* — a grade turn that also teaches (the
  diagnose-first repair) is covered by two receipts: the `grade-audit` covers the
  graded question/answer/verdict and the `fact-check` covers the repair prose
  (`rendered_content` = the full emitted turn). When the grade-audit does not
  cover the whole emitted text and no fact-check covers it, the turn is withheld
  (`GRADE_AUDIT_STALE`) with a remedy to fact-check the prose or split the turn —
  the gate never loops re-dispatching the grade-audit (the 2026-10-05 session
  looped on exactly that).
- **G-grade-verdict-only-binds** *(hard)* — a verdict-only `[[TURN:grade]]`
  (only the graded answers + their verdicts) renders with just the agreeing
  `grade-audit` receipt. The receipt binds the graded question/answer/verdict,
  which a terse confirmation does not repeat verbatim; the model judge has a
  `GRADE TURNS` carve-out and the deterministic fallback accepts a turn that
  restates every graded answer and stays short (the 2026-10-06 resume session
  looped as `GRADE_AUDIT_STALE` because a verdict-only turn could not bind at
  all). Teaching/repair prose is still uncovered and needs its own fact-check.

- **G-receipts-consumed-per-message** *(hard)* — a receipt is consumed by the
  message it verified; the same receipt cannot authorize a later turn.
- **G-partial-ungated** *(hard)* — an unfinished generation
  (`stopReason` error/aborted/length) passes through with its tag stripped and
  consumes no receipt.
- **G-ingest-requires-review** *(hard)* — an ingest summary renders only with a
  valid review verdict; a Clerk-completed ingest is not held hostage.
- **G-ingest-clerk-relay-flagged** *(policy)* — a verdict relayed by the Clerk
  (not an independent `review-gate` run) surfaces `⚠️ INGEST GATE`.
- **G-review-evidence-required** *(policy)* — a review-family verdict (`review-gate`,
  `review-session-audit`, `scout-audit`) with no `evidence`
  list is unsubstantiated and flagged.
- **G-scout-banner-not-withhold** *(policy)* — a partial/missing Scout digest
  banners (`SOURCES INCOMPLETE` / `SCOUT DIGEST UNVERIFIED`), never withholds.
- **G-scout-audit-required** *(hard)* — a new lesson's first teaching claims turn
  renders only with a valid independent `scout-audit` receipt over the Scout
  digest (completeness: all curriculum + Further Reading sources fetched or
  explicitly failed, digest fields + `theory` lines + prereqs present, raw files
  on disk; fact-check: excerpts/synthesis grounded in the raw files, no
  synthesis from failed refs, contradictions surfaced). A missing audit
  withholds (`NO_SCOUT_AUDIT_PASS`) with a re-dispatch remedy; an `ISSUES`
  verdict surfaces `⚠️ SCOUT AUDIT FLAGS SURFACED` and never hard-blocks (the
  lesson teaches around the gaps visibly, like the ingest `REVIEW FLAGS
  SURFACED` path). A wrong-shape receipt naming no `digest` releases nothing.
- **G-provider-fallback** *(policy)* — after two consecutive provider failures,
  offer (never force) a one-shot alternate-model re-dispatch.
- **G-no-duplicate-factcheck** *(hard)* — re-verifying an already-verified draft
  is blocked; a materially corrected post-ISSUES draft is allowed, as are the
  re-dispatches `CLAIMS_INCOMPLETE`, `FOUNDATION_INCOMPLETE`, and the repair-shape
  remedy mandate (the same draft with the missing claims, foundation beats, or
  `repair` block added). The corrected receipt supersedes the incomplete one, so
  the emission binds the complete pass.
- **G-async-notify-mints** *(hard)* — async completion notifications mint
  content-bound receipts from the dispatch envelope; failures clear pending.
- **G-infer-claims-from-bound** *(hard)* — a dropped `claims` tag is recovered
  only from a content-bound passing fact-check (100% coverage with a judge, ≥95%
  plus a bounded unverified tail on the legacy path).
- **G-infer-grade-quiz** *(hard)* — a dropped `grade`/`quiz` tag is inferred
  from a bound receipt or the single valid pending receipt; ambiguity withholds.
- **G-claims-requires-factcheck** *(hard)* — claims render only with a
  content-matched passing fact-check; a pending one withholds with a wait hint.
- **G-claims-complete** *(hard)* — the generator may not curate its own exam:
  every hard fact in the draft (decimal, percentage, scientific notation, 3+
  digit integer, LaTeX/math expression, URL) must appear in the submitted
  `claims[]`, or the turn is withheld (`CLAIMS_INCOMPLETE`). A number or formula
  nobody listed is a number or formula nobody verified. Containment is
  notation-insensitive: the same fact written as LaTeX in the draft and as plain
  prose in `claims[]` (e.g. `\mathrm{Per}(P_i) = 2^{H(P_i)}` vs
  `Per(P_i) = 2^(H(P_i))`, `\sigma_i` vs `sigma_i`, or `q_{ij} \propto
  1/(1+d_{ij}^2)` vs `q_ij proportional to 1/(1 + d_ij^2)`) counts as present, so
  a notation difference — a LaTeX symbol macro, or whitespace around an operator
  — cannot dead-end the turn.
- **G-draft-tail-bound** *(hard)* — an emission may reproduce a verified draft
  with reordering or punctuation edits but may not append unverified prose: at
  most `LENGTH_SLACK_TOKENS` (12) emitted tokens may be absent from the draft.
  The old 1.4× length ratio allowed an unbounded unverified tail.
- **G-foundation-beats** *(hard)* — the gate checks omission, not just commission.
  In a teach/resume flow a `claims` turn must declare a valid `turn_kind`:
  `plan`, `triage`, `attack`, `hint`, `autopsy`, `answer`, `repair`,
  `grade_feedback`, or `idea`. A `triage` turn ships a non-empty `triage[]`
  where every row names an item and a valid bucket and every non-solid row
  carries the learner's quote or a source citation; the optional
  `requires`/`on_path` fields order the attack plan and must be acyclic. An
  `attack` turn ships exactly one subtype (`mechanism`/`counterexample`/
  `perturbation`/`source_clash`/`sabotage`/`synthesis`); `plan`/`answer`/
  `repair`/`hint`/`grade_feedback` need no shape block. An `autopsy` turn ships
  exactly one reasoning `step` (`index`/`total`/`fact`/`rests_on`/`check`) with
  the `fact` and `check` prose present in the draft; more than one step is a
  lecture and is withheld. An `idea` turn (a new definition, formula,
  mechanism, or micro-step the learner actually asked for) carries all four beats
  — `problem` (what it is for), `where_from` (conceptual entailment/mechanism),
  `conditions` (assumptions/boundary cases), `contrast` (nearest-neighbour
  distinction) — each non-empty and its prose present in the verified draft;
  `where_from` never demands a symbolic derivation. A missing or unknown
  `turn_kind`, a malformed `triage[]`, an attack without one valid subtype, or an
  autopsy without one bound step is withheld (`FOUNDATION_INCOMPLETE`) with a
  remedy naming the fix, so a fluent what-only lecture, an ungrounded triage
  claim, a chain of attacks, or a multi-step patch cannot render as if complete.
  Foundation beats are also the completeness rubric for the learner's own model:
  a missing beat is an attack target, never a Tutor paragraph. A fact-check
  verdict naming a non-empty `omitted_foundations[]` (load-bearing *conceptual*
  theory in the sources with no trace in the draft) is an `ISSUES` verdict even
  when it also says PASS; the omission check never demands a missing symbolic
  derivation, but it may require a qualitative one-step entailment.
- **G-interrogation-stance** *(policy)* — the Tutor is a sparring partner and
  stress-tester, not a primary teacher. The pi/Open WebUI layer ships the same
  interrogation stance as the Antigravity layer: never teach a topic cold, read
  the learner's material, require a closed-book model, bracket the edge when the
  model is ambiguous, triage the model as a dependency-ordered attack tree, attack
  one hole at a time, reveal at most one reasoning step when a legal reveal is
  delivered, patch the learner's model (v1 → breaking case → v2), run the
  entailment check, and graduate it with a naive-student clone. The retired
  teacher-first loop (probe → plan → mini-checkpoint lecture) is gone from the
  prompt resources; the bracket is diagnostic measurement, not a lecture.
- **G-triage-shape** *(hard)* — a `turn_kind:"triage"` turn carries a non-empty
  `triage[]`; every row has an item and a bucket in `solid|missing|suspect`, and
  every non-solid row carries grounding (the learner's exact words for
  `suspect`, a source citation for `missing`). Optional `requires` names the rows
  whose repair must land first and `on_path` marks the shortest dependency path to
  the model's goal; a reference to an unknown row, a self-reference, a duplicate
  item name, or a cycle is withheld (`FOUNDATION_INCOMPLETE`) with a triage-specific
  remedy, so the attack plan is always traversable. A missing/empty table, an invalid
  bucket, or an ungrounded non-solid row withholds the turn the same way.
- **G-attack-shape** *(hard)* — a `turn_kind:"attack"` turn declares exactly one
  subtype from the attack menu; a missing, unknown, or multiple subtype withholds
  the turn (`FOUNDATION_INCOMPLETE`) with an attack-specific remedy. The verifier
  additionally rejects an attack that does not target a non-solid triage row, an
  attack on a dependent hole before its `requires` are solid, a counterexample
  that does not satisfy the learner's statement as written, a perturbation of a
  cosmetic term, or an attack that fills the hole
  (`SPOONFEEDING_DETECTED` / `LECTURE_SLIP`).
- **G-repair-trigger** *(policy)* — teaching mode is a repair, not a lesson. After
  a graded miss the learner first gets the hint ladder (R0–R2 + a source return)
  and one self-repair attempt; `structural` misses get one verification nudge
  first, and a `missing` gap has nothing to cue and enters repair mode at once.
  Re-attacking the same gap, or re-asking the same item, without a repair turn
  once that attempt has failed is `REPAIR_MODE_SKIPPED`. The trigger is
  verifier-enforced (`fact-check` §4c); the gate enforces the receipt that
  follows.
- **G-repair-method** *(hard)* — a `turn_kind:"repair"` turn ships a `repair`
  block bound to exactly one `gap`, naming the diagnosed `miss_class`
  (`cue|discrimination|execution|structural` — a `careless` miss is re-checked,
  never repaired; a `missing` triage row uses the class `grade-audit` returned,
  usually `cue`) and the `tactic` that diagnosis selects
  (`source_return|retrieval_cue|contrasting_pair|worked_step|push_down|
  full_teach`), with `status:"teaching"|"done"`. A `teaching` turn
  ships exactly one reasoning `step` (`index`/`total`/`fact`/`rests_on`/`check`)
  whose `fact` and `check` prose are in the draft — a multi-step repair is a
  lecture and is withheld. The verifier additionally enforces the method:
  start from the unconditional truth the gap rests on, one motivated step at a
  time, Socratic first (expository only when the step is beyond cold reach or
  the learner asked to be told), check every step, never build on an
  undemonstrated step, and no wall of text that "covers" the missing ground
  (`LECTURE_SLIP`).
- **G-repair-scope** *(policy)* — a repair turn teaches **only** its bound gap,
  never the wider curriculum, and the learner still authors the model: the Tutor
  never writes, polishes, or merges v1/v2 (`MODEL_GHOSTWRITING`). Widening a
  repair into a lesson is `REPAIR_SCOPE_DRIFT`.
- **G-repair-complete** *(hard)* — an open repair blocks the attack battery: a
  `turn_kind:"attack"` turn is withheld (`NO_REPAIR_RECEIPT`) while any repair is
  open — including at the retry cap, so a soft attack can never leak the battery
  — and a second gap cannot be opened before the first is closed
  (`REPAIR_INCOMPLETE`). A repair is closed only by a `status:"done"` turn that
  names (a) the **fresh-surface** check the learner already answered and
  `grade-audit` passed, bound to the graded item with `repair_gap` equal to this
  repair's gap (never to prose, and never to a check graded for another gap),
  and (b) the learner's own-words restatement, quoted verbatim. A done turn with
  no graded pass, a mismatched gap, or no restatement is withheld
  (`REPAIR_INCOMPLETE`). The fresh-surface check must not be a re-ask of the
  repair turn's own question or answerable by reciting its prose (`quiz-audit`
  repair rule); a recital is `SHALLOW_PASS` (`grade-audit`).

- **G-interrogation-turn-kinds** *(hard)* — every teach/resume claims turn
  declares a valid `turn_kind`; `plan`/`triage`/`attack`/`hint`/`autopsy`/
  `answer`/`repair`/`grade_feedback` need no foundation beat and only `idea`
  does. An `autopsy` carries exactly one reasoning `step` block; other non-idea
  kinds carry neither. An unknown or absent kind is withheld
  (`FOUNDATION_INCOMPLETE`). A grade-feedback turn is a claims turn verified with
  `turn_kind:"grade_feedback"` + `grade_verdicts[]`; it reproduces the audited
  verdicts exactly and never exposes verification internals.
- **G-verifier-interrogation-audit** *(policy)* — the fixed verifier prompts
  police mental-model integrity as strictly as truth. `fact-check` audits attack
  grounding, dependency ordering, and counterexample validity, triage integrity,
  model ghostwriting, ungrounded holes, lecture slips, one-step autopsy patches,
  spoonfeeding, cue leakage, and visual sufficiency (`visual_plan` present;
  `VISUAL_PLAN_MISSING` / `VISUAL_MISSED`). `grade-audit` grades the mechanism and
  the direction/extreme check, applies the attack and battery rubrics, flags
  `SHALLOW_PASS` when the learner merely remixes the Tutor's recent turns, records
  sure-but-fail as false confidence, grades the graduation conceptual entailment
  without demanding algebra, and requires a real `naive_student_receipt` for a
  clone. `quiz-audit` enforces context-appropriate item types (bracket probe,
  pre-attack prediction, practice, review, solo), the concept-label ban, the
  qualitative-trace requirement, and check craft.
- **G-clone-protocol** *(hard)* — graduation for a `concept`/`design` runs an
  entailment check before the naive-student clone: one qualitative question
  asking why the patched claim must hold given what the learner already accepted,
  and what would have to be true for it to break. Pass requires the learner's own
  conceptual one-step entailment plus the breaking condition; this is not a
  symbolic derivation and must not demand algebra. The clone then hands over v2
  **verbatim** (never a Tutor paraphrase) plus the concept, a seeded
  misconception, prerequisite level, and a qualitative prediction/tool-choice
  task. The clone reports `NAIVE_STUDENT_RECEIPT` with `task_succeeded` and
  `questions_unanswered`; a failed clone is a fail regardless of the claimed
  verdict, a missing receipt is an `ISSUES` verdict, and the outcome is logged as
  `feynman_pass`/`feynman_fail`. v1 and v2 are preserved verbatim in order with
  the breaking case labelled between them.
- **G-review-no-mcq** *(hard)* — review and solo batches test cue selection and
  transfer, not recognition: no MCQs (MCQs are legal only in a bracket probe),
  items are unlabeled for selection/application, and the learner must produce the
  3-line qualitative trace (cue & principle → mechanism/knob-turn → direction &
  extreme check). Review/solo batches include operational items (perturbation,
  misapplication, decoy/near-miss). A review presents verified feedback and
  **pauses for learner questions** before any state is persisted; `review-clerk`
  runs only on an explicit "no questions".
- **G-solo-no-teaching** *(hard)* — in an AI-free solo flow (`[[FLOW:solo]]`) the
  Tutor cannot teach: a claims turn is withheld (`SOLO_NO_TEACHING`) and a widget
  turn is withheld (`SOLO_NO_AIDS`), so the learner's answers are unassisted. A
  `none` transition carrying hard facts and a
  `grade` turn carrying a fact-checked teaching/repair tail are withheld too, and
  `SOLO_*` is exempt from the retry-cap dump (withheld outright, never delivered as `UNVERIFIED`).
  The block is enforced deterministically on both the legacy and judge paths. The
  closed-book quiz batch and grading render; the first content turn requires a
  `review-scout` run (deterministic queue); the close uses the same
  `review-session-audit` as a review.
- **G-none-evasion-guard** *(hard)* — `[[TURN:none]]` over a verified or
  in-flight fact-check draft is withheld (`TURN_TAG_MISMATCH` /
  `FACT_CHECK_PENDING`). Review-flow carve-out: closing review feedback/summaries
  legitimately reuse verified prose under a `none` tag, so a `none` turn covered
  by a passing fact-check renders in the review flow (the content is verified);
  the in-flight guard still withholds, and the carve-out does not apply outside
  review.
- **G-non-learning-not-gated** *(hard)* — a session with no `[[FLOW:...]]`
  marker is never gated; messages pass through untouched.
- **G-tutor-audit-required** *(hard)* — after a Learning System write in
  teach/resume, a summary turn needs a passing `tutor-audit` over the files
  written; quiz/grade turns are not held hostage.
- **G-review-session-audit** *(hard)* — after the review flow writes its session
  note (or the delegated `review-clerk` run returns), a summary turn needs a
  `review-session-audit` receipt. Only a receipt with zero issues releases the
  summary: an `ISSUES` verdict blocks it (`REVIEW_SESSION_AUDIT_ISSUES`) until the
  writes are corrected and a fresh audit returns zero issues (any severity), with
  no per-flow pass cap.
- **G-review-context-required** *(hard)* — a review's first claims/quiz turn is
  withheld (`NO_REVIEW_CONTEXT`) until a `review-scout` run has happened; a
  partial review digest banners, never withholds.
- **G-scout-required** *(hard)* — a new lesson's teaching claims are withheld
  (`NO_SCOUT_CONTEXT`) until a scout run has happened.
- **G-retry-cap** *(hard)* — repeated withheld turns are capped; beyond the cap
  the turn surfaces with `⛔ UNVERIFIED` rather than looping.
- **G-hard-fact-withhold** *(hard)* — at the retry cap, a `claims` turn whose
  draft states hard facts (`extractHardFacts`: URL, LaTeX/math expression,
  scientific notation, decimal, percentage, or 3+ digit integer) is **withheld
  entirely** — only the banner renders, no content — rather than delivered as
  `⛔ UNVERIFIED`, **but only when the block implicates verification**
  (`FACT_CHECK_*`, `CLAIMS_INCOMPLETE`, `FOUNDATION_INCOMPLETE`,
  `NO_FACT_CHECK_MATCH`). A `FOUNDATION_INCOMPLETE` idea turn is withheld the same
  way even with no hard facts, so a complete-sounding but foundation-less summary
  is never shown. A verified draft
  blocked only on context (`NO_SCOUT_CONTEXT`/`NO_REVIEW_CONTEXT`) degrades
  gracefully. Non-hard-fact prose still degrades with the UNVERIFIED banner, and
  `G-retry-cap` semantics are unchanged for grade/quiz/none turns. A deliberate
  inversion of the anti-dead-end policy for load-bearing facts and for the
  missing theoretical foundation: a number or formula nobody verified — or a
  "why" nobody taught — is never shown.
- **G-out-of-scope-demoted** *(policy)* — review findings are demoted to flags
  only when **every** finding cites an explicit bookkeeping-path `location`
  (state/session/review/lesson notes, log/index bookkeeping, git metadata). A
  finding that cites a content location, or gives no location, is never demoted:
  a content defect that merely mentions a bookkeeping word in its `issue` text
  still blocks. The whitelist is path-shaped (a bare keyword such as
  `provenance` no longer matches). The old issue-text fallback and the blanket
  low-severity demotion are removed (they could swallow a real content finding).
- **G-state-audit-blocking** *(hard)* — the content gate
  (fact-check/quiz/grade/review) and the state gate are split. At the
  ingest/review close, the deterministic state audit's **errors** block the
  summary (`STATE_AUDIT_ERRORS`) until the drift is fixed and the audit re-runs
  clean; **warnings** remain a non-blocking `⚠️ STATE AUDIT` banner. A warning
  can never dead-end the flow. The block is subject to the standard retry cap: a
  persistent, unfixable error withholds twice and then degrades to
  `⛔ UNVERIFIED` rather than dead-ending the close.
- **A-subagent-result-shape** *(hard)* — the dispatch envelope is recovered from
  `tool_call` when pi-subagents redacts `task` on a foreground result.
- **G-receipt-shape-binds** *(hard)* — a receipt minted from a
  present-but-wrong-shape envelope must not satisfy its gate. A quiz/grade
  receipt with no bound text (a quiz-audit sent with `items[]` instead of
  `questions_json`, or a grade envelope with no question/answer/verdict)
  authorizes no emission; a write-gate receipt with no artifact list
  (tutor-audit `files`, review-session `written_files`, review-gate
  `target_files`, scout-audit `digest`) releases no summary and a scout-audit
  receipt with no `digest` releases no teaching turn. Only an envelope-less async completion
  notification falls back to unbound. One wrong-shape receipt must not bind every
  later turn.
- **G-quiz-binds-full-batch** *(hard)* — a `quiz-audit` receipt binds the whole
  emitted batch: the envelope's `rendered_content` (the full batch text) is the
  bound text the judge sees, and without it the derived bound text includes each
  item's `options`. A questions-only binding cannot strand a valid quiz turn as
  `QUIZ_AUDIT_STALE`.
- **G-language-drift** *(hard)* — a learner-facing turn emitted predominantly in
  CJK/kana/Hangul while the learner's latest message and every submitted/verified
  draft are not is language drift (a fluent translation, not a rendering glitch,
  whatever the model claims). The deterministic script guard withholds it as
  `LANGUAGE_MISMATCH` before binding, on both the judge and legacy paths, and
  never dumps it at the retry cap. A learner who writes CJK is exempt, and the
  verified draft survives for a clean re-emit. Scope is CJK/kana/Hangul only
  (Latin, Greek, and Cyrillic are excluded because math and names mix them into
  English prose); drift into other non-Latin scripts is not covered.
- **G-dispatch-object-task** *(hard)* — verifier/worker dispatches go through the
  `dispatch` helper, which takes the JSON envelope as an **object** and runs the
  child through pi-subagents' structured delegation bridge (`subagent` is
  `exposure: "model-only"`, so the bridge is the only extension path). `dispatch`
  serializes the envelope and mints the gate receipt itself, so a model that emits
  an object `task` — the shape that dead-ends the `subagent` tool with
  `task: must be string` — still gets a bound receipt. The legacy `subagent`
  `workflow`/`args` forms are blocked and redirected to `dispatch`. Nothing in
  the prompt resources may spell a `subagent(` dispatch call.
- **G-ui-turn-requires-audit** *(hard)* — a `[[TURN:ui]]` message renders only
  with a passing, bound `ui-audit` receipt: missing → `NO_UI_AUDIT`, an
  `ISSUES` verdict → `UI_AUDIT_ISSUES`, a valid-but-unbound receipt →
  `UI_AUDIT_STALE`. The widget the bridge embeds is exactly the payload the
  verifier audited.
- **G-ui-audit-binds-payload-and-prose** *(hard)* — a `ui-audit` receipt binds
  only when the emitted turn carries exactly one OpenUI Lang payload fence, its
  canonical payload equals the audited `payload`, **and** its `rendered_content`
  covers the emitted text; a different payload, a second unaudited fence, or a
  present-but-wrong-shape envelope missing the payload or `rendered_content`,
  authorizes no emission.
- **G-ui-standalone-turn** *(hard)* — a ```openui payload fence may only appear
  in a `[[TURN:ui]]` message; a widget block inside a claims or transition turn
  is withheld (`UI_REQUIRES_OWN_TURN`).
- **G-ui-payload-valid** *(hard)* — a `[[TURN:ui]]` message with no parseable
  ```openui payload fence — or with more than one — is withheld
  (`UI_PAYLOAD_INVALID`).
### The judge (model-based semantic decisions)

The gate can run a **judge**: a model (Gemini `gemini-3.5-flash-lite`, with
`gemini-3.5-flash` as an escalation) that answers the semantic questions the
deterministic code cannot. The judge only **sees and writes text** — it runs no
tool, writes no file, changes no state. The engine performs every action. When
no judge is configured, or the judge faults, the gate runs the legacy
deterministic path unchanged (G-judge-degraded-fallback).

- **G-turn-type-inferred** *(hard)* — turn tags are hints; the judge reads the
  turn type from the content. Verifier/notification channels are never gated.
- **G-full-coverage-binding** *(hard)* — a turn renders only when 100% of the
  emitted text is covered by the verifier's verified draft; any uncovered span
  blocks, and the remedy names the span.
- **G-pass-substantive** *(hard)* — a PASS the judge scores unsubstantiated
  (thin/none, missing items, no evidence) does not verify the turn.
- **G-issues-no-cap** *(hard)* — while **any** verifier issue remains (any
  severity) the gate keeps blocking and never dumps the turn as `⛔ UNVERIFIED`;
  the cap applies to every other reason. Severity labels no longer gate: a `low`
  blocks exactly like a `high`.
- **G-verifier-recheck-uncapped** *(hard)* — verifier re-checks are not dispatch-
  capped: a `review-gate`, `review-session-audit`, or `scout-audit` may be re-dispatched as many
  times as needed, and the Tutor/Reviewer keeps fixing and re-checking until the
  verifier returns **zero issues at any severity**. There is no per-flow pass
  limit and no "max 2 cycles" stop. An identical issue that never changes is
  still bounded by G-verifier-dispute (three identical blocks escalate to the
  judge), so the loop cannot spin on a stale finding.
- **G-any-issue-blocks** *(hard)* — every verifier finding blocks at any
  severity. A verdict object carrying a non-empty `issues[]` is an ISSUES verdict
  regardless of the stated verdict word or the severity labels, so a
  `PASS_WITH_FLAGS` listing residual `low` issues is not a pass. `PASS_WITH_FLAGS`
  survives only as the review-gate/scout-audit out-of-scope bookkeeping demotion
  (G-out-of-scope-demoted), never as a verifier's own severity tolerance.
- **G-verifier-dispute** *(policy)* — the same issue blocking three times is
  adjudicated by the judge (does it still apply?); if not, the engine releases
  the turn with `⚠️ VERIFIER DISPUTED`. The judge only answers.
- **G-receipt-source-is-verifier** *(hard)* — a receipt is the verifier's own
  statement; the judge never authors or rewrites receipt fields.
- **G-judge-degraded-fallback** *(policy)* — a judge fault falls back to the
  legacy checks; a learning turn never dead-ends on a judge fault.
- **G-judge-escalation** *(policy)* — a hard case (valid receipt not fully
  covering, no best receipt, or thin substantiveness) escalates from
  `gemini-3.5-flash-lite` to `gemini-3.5-flash`, budget-capped per day; a
  primary outage escalates before falling back to the legacy path.

The judge also writes the **ledger** (`~/.pi/agent/learning-gate/`: 
`receipts.ndjson`, `decisions.ndjson`) — receipt provenance for the weekly
audit and the accountability record for every decision.

### Bridge (OpenAI-compatible face over pi)

`bridge/` puts Open WebUI in front of the pinned pi runtime. It is intentionally
thin — all learning behaviour stays in pi — but these load-bearing properties
must hold or unverified content reaches the learner, or the runtime stops
starting. They are covered by the Python `unittest` suite in `test/bridge/`,
whose `PASS <test id>` lines `scripts/learn-check` feeds into the same contract
coverage check as the deno gate suites.

- **B-deltas-never-forwarded** *(hard)* — assistant text reaches the client only
  from the completed `message_end` message (the post-gate turn). `message_update`
  text/thinking deltas carry the raw pre-verification draft and are never
  emitted, so a withheld teaching draft cannot leak while it streams.
- **B-withheld-banner-forwarded** *(hard)* — a withheld or retry-capped turn
  surfaces the gate's own banner text written into `message_end` (`⛔ WITHHELD` /
  `⛔ UNVERIFIED`) — never the raw draft, and never a bridge-authored substitute.
- **B-newest-message-only** *(hard)* — one pi RPC session per chat, reused across
  turns; only the newest user message of each posted transcript is forwarded (pi
  owns its context). The session is started with a deterministic `--session-id`,
  so a bridge restart or a pi crash resumes the same transcript instead of
  starting blank and re-deriving context from the state repo. A resend of the
  same message is a regenerate: the bridge forks the session back to that user
  message before re-prompting, and falls back to appending if the fork fails.
- **B-chat-identity-routing** *(hard)* — when Open WebUI forwards
  `X-OpenWebUI-Chat-Id`, the chat id (not the first-message fingerprint) is the
  pi session identity, so two chats with the same first message never share a
  session. An existing conversation without a chat-id session is migrated once
  from its fingerprint session; a brand-new chat whose first prompt matches an
  old one is not.
- **B-attachments-forwarded** *(hard)* — an uploaded image reaches pi as an
  `ImageContent` block on the prompt, including an image-only message; text
  parts are forwarded unchanged. Non-image files follow Open WebUI's own
  file-context/RAG path into the user message.
- **B-chat-delete-mirrored** *(hard)* — deleting an Open WebUI chat removes its
  pi session. A background sweep deletes only on an explicit 404, never on a
  network error, and leaves an in-flight turn for the next pass.
- **B-chat-fork-mirrored** *(hard)* — forking or cloning a chat copies the
  parent's pi branch at the fork point into a session owned by the new chat id:
  a user-message fork keeps that message, an assistant fork keeps its turn, and
  the copy is reused after a bridge restart instead of duplicated.
- **B-bash-guard-floor** *(hard)* — the bridge passes `--bash-guard-disabled`
  only when bash-guard is actually installed in the agent dir. A headless session
  needs the catastrophic-command floor disabled to stay usable, but pi rejects an
  extension flag no loaded extension registered, so passing the flag when
  bash-guard is absent would stop pi from starting.
- **B-single-learning-writer** *(hard)* — a single-writer learning lock admits one
  learning turn at a time on the shared state repo: a second learning turn in
  another chat is told to wait rather than overlapping the write, while general
  (non-learning) chats are exempt.
- **B-steps-metadata-only** *(hard)* — the live action trace is emitted as
  Open WebUI `<details>` content blocks built only from completed records. A tool
  step carries its name, its arguments truncated to 200 characters, its status
  and its duration — never its result in a learning flow. A thinking step carries
  only its duration in a learning flow ("Thought for Ns"); its text appears only
  in a general (non-learning) chat. `message_update` deltas never become a step
  (B-deltas-never-forwarded still holds), and a step block is always complete and
  parseable: nested `<details>` text cannot end it early.
- **B-steps-stream-before-settle** *(hard)* — in a streaming response each
  completed step is written as its own `chat.completion.chunk` while the pi turn
  is still running (before `agent_settled`), in stream order; the post-gate prose
  is written only after settlement. Open WebUI therefore shows actions as they
  happen instead of the finished turn all at once.
- **B-status-done-always** *(hard)* — when Open WebUI supplies the chat/message
  ids (the connection's custom forwarded headers `{{CHAT_ID}}` /
  `{{MESSAGE_ID}}`), the bridge posts best-effort `status` events for the live
  one-line status and its timeline. Any sequence that starts ends with
  `done: true`, including after a provider error, so the shimmer never sticks;
  without a message id nothing is posted, and a failed status call never affects
  the turn.

### Launcher & update gate

- **S-1** behavior lives here and in the tagged tests; it changes only through
  the revise door.
- **S-2** tests run against a synthetic fixture state; real learning state is
  never a fixture and never written by the harness.
- **S-3** every promotion is journaled in `versions.lock.json` and reversible
  with `pi-safe-update rollback`.
- **S-4** the launcher (`bin/pi`) never updates anything; `pi-safe-update` is
  the only path that changes versions.
- **S-5** the end-to-end learner journeys (`harness/e2e-runner.py`, `test/e2e/`)
  replay real flows against a sandbox and read model access from the real agent
  dir read-only (credentials and model catalog copied into a throwaway 0700
  sandbox; packages never installed into the real agent). They are an **opt-in**
  gate step (`lpi e2e`, `learn-check --e2e`, `pi-safe-update update --e2e`), not
  a default. A failed journey never promotes and never patches code; it leaves a
  transcript and result JSON under `~/.cache/learning-pi/e2e-*`.

### Sidecars (existing suites)

- **P-1** `ops.py` resolves its root to a checkout containing
  `Learning System/Core` (not a hardcoded path).
- **P-2** `ops.py` rejects path escapes outside the workspace.
- **P-3** `ops.py state <track>` returns the concept table rows, not just the
  heading.
- **P-4** `audit_state.py` is read-only and prints a `STATE_AUDIT_FIXES:` JSON
  hint array.
- **P-5** `audit_gates.py` exits non-zero on error-level findings.

### Knowledge graph (propositions + reasoning chains)

- **G-graph-world-only** — the graph stores the subject, never the learner:
  propositions (one self-contained statement, verbatim aliases, provenance) and
  reasoning chains (a premise set that jointly entails a conclusion). No mastery,
  verdicts, confidence, attempts, or "the learner understands X"; a misconception
  enters as its true correction. Unknown record fields are rejected at merge.
- **G-graph-provenance** — every node and chain names the source file it came
  from. A re-encounter appends a `link` line: the verbatim phrasing joins
  `aliases[]`, provenance unions with the `define` line, and the original
  statement is never overwritten. Only `pi/graph.py merge|retract` writes the
  ledgers; no agent hand-edits the JSONL.
- **G-graph-derived-view** — edges are never stored. `graph.py export` derives a
  lossy view where each chain becomes an implication node
  (premises -> ⟹ -> conclusion), so two independent arguments for one conclusion
  stay two diamonds; identical premise sets link instead of duplicating, and
  retracting a proposition drops (and reports) every dependent chain.
- **G-graph-audit** (policy) — ingest extracts (`graph-extract`), merges
  deterministically, and the parent dispatches an independent `graph-audit` over
  **every written id** (created and linked propositions/chains) before the ingest
  closes. This is gate-enforced, not prompt-only: the close summary is withheld
  (`NO_GRAPH_AUDIT_PASS`) until a passing audit covers every id in
  `CLERK_WRITES.graph`; an ISSUES verdict (any severity) withholds it
  (`GRAPH_AUDIT_ISSUES`) until the Clerk records a fix (retract/correct +
  re-merge) and a fresh audit passes — no cycle cap and no hand-editing to
  satisfy the audit. The audit fact-checks the **connections**, not just the
  nodes: every chain premise and conclusion is grounded in the cited material
  and jointly entails it, and every link joins the same proposition.

### Cross-session grounding (prior knowledge)

- **G-prior-knowledge-grounding** — the adversarial stance uses the learner's
  own history: the fact-check envelope carries `prior_knowledge` (prior verbatim
  models, graph propositions/chains, open mistakes), every quoted prior item
  appears verbatim in it, the clash targets the same concept/model, both sides
  are verbatim, and no winner is announced. An invented or paraphrased "you once
  said…" is `PRIOR_UNGROUNDED`; a prior fact about another concept is not a valid
  attack target. Attack subtypes and the one-attack-per-turn rule are unchanged.
- **G-scout-prior-context** (policy) — lesson/review digests harvest
  `prior_knowledge` from `pi/graph.py list` plus prior verbatim models and open
  mistakes; empty arrays are legal when nothing is relevant, but a failed graph
  read must surface as a `failed_refs` entry, never a silent empty. The digest is
  grounding data, never a learner-facing summary.

### Practice doctrine (hints and misses)

- **G-hint-ladder** (policy) — the stuck ladder is R0–R5 (attention redirect,
  pattern re-description, candidate class, proposition named, move outlined,
  worked step), one rung per request, answering the first break in the trace.
  Statement repairs are free; solution information is metered. The rung needed
  is a difficulty readout, the independence budget still caps hints (2/1/0), and
  solo sessions get none.
- **G-miss-taxonomy** — every fail is classified `cue | discrimination |
  execution | careless | structural` by `grade-audit` and recorded as a
  `[miss: …]` Self-Attribution prefix by `review-clerk`. It layers on the
  existing `error_type` enum; no new enum values, no invented classes.
- **G-practice-difficulty** (policy) — review items are retrieval from an
  inactive state: interleaved targets, no immediate re-ask, decision points
  rather than restatements, ~85% success per retrieval event with hint rescue
  at the edge, and the 3-line trace as a floor rather than a cap.
- **G-item-targets** (policy) — quiz questions and grade items may carry
  `targets[]`, the knowledge-graph record ids (`n_…` propositions / `arg_…`
  chains) the item retrieves. Targets are additive record-keeping, never
  learner-facing text and never a grading input: the binding fields are
  unchanged, a missing/empty list blocks nothing, and `grade-audit` ignores
  targets when deciding a verdict. Ids are copied verbatim from the scout
  digest's `prior_knowledge` (never invented), carried from question to grade
  item to `REVIEW_WRITES.grade_verdicts[]`, and recorded on the attempt by
  `ops.py attempt --targets`; malformed ids are `TARGETS_INVALID` at
  quiz-audit and rejected by ops.py. They are the bridge to per-node mastery
  and never enter the graph ledger as learner state. Target ids are
  **liveness-checked** against the graph ledger as well as format-checked: a
  malformed id is `TARGETS_INVALID` at quiz-audit, and `ops.py attempt|amend`
  rejects a well-formed but non-live id (missing or retracted) so only current
  records can be recorded. If a digest snapshot names an id that is no longer
  live, the flow drops that id and records the attempt without it — never
  resolving, inventing, or substituting a different id. The rejection is
  implemented in the state-repo `scripts/ops.py` (learning-system@ff57645),
  which folds the same append-only ledgers as `pi/graph.py`. Per-node mastery
  aggregation is still not implemented — this is the plumbing for it — so
  `ops.py mastery` remains per-concept.

## Adding a newly installed extension

If a new extension participates in the learning flow, add its behavioral role
here (what receipts it mints, what turns it gates) and a tagged test. Do not
couple the test to the extension's internal shape — express it in domain terms
and let `pi-adapter/` (or a new adapter file) absorb the wire format.

## Residual risk (accepted)

Model-side drift — the server-side behavior of a model changing with no version
bump — cannot be pinned. It is caught by the fail-loud design (withhold +
banner, never corrupt state), the optional live smoke, and the weekly
`audit_gates` pass over real sessions. See `README.md`. The judge adds a second
model to this surface; it is bounded by the ledger, the legacy fallback, and the
free-tier budget (the gate degrades to the deterministic path when the budget is
spent).
