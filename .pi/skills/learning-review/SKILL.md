---
name: learning-review
description: Quality-gate learning-system output before it is finalized, wherever it originates. Use after every standalone ingest, at the end of any teaching lesson that produced wiki pages or Active Concepts rows (review-gate), AND at the close of a standalone /review session (review-session gate on the Review notes / session note / touched state rows). The review-gate subagent flags accuracy, correctness, clarity, and completeness issues; every in-scope issue blocks until fixed regardless of severity, and the re-check runs until the verifier returns zero issues (no cycle cap). The review-session close audit likewise withholds the close summary on an ISSUES verdict until the writes are fixed and a fresh audit returns zero issues.
---

# Learning system review gate

This gate checks the learning system's ingest output: the wiki pages and Active Concepts rows an ingest wrote. Run it at the end of every standalone ingest, at the end of any teaching lesson that wrote wiki pages or Active Concepts rows, and on demand.

Scope is strictly the ingest's own output. State drift is out of scope. State drift means MISSION, CURRICULUM, Learning Profile, Learner History, Mistakes, Attempts, lesson files, and index bookkeeping. `audit_state.py` checks those at ingest close and review close. The Tutor's writes are checked by `tutor-audit`.

Lesson files, learning records, and glossary entries promoted by lessons are verified live during teaching by `fact-check` and `quiz-audit` or `tutor-audit`, not by this gate.

## Review-session gate

A standalone `/review` mirrors the teaching pipeline:

1. `review-scout` gathers context and builds the due queue at the start. The gate withholds the first turn with `NO_REVIEW_CONTEXT` until it runs. A partial `REVIEW_SCOUT_DIGEST` raises a banner.
2. The Reviewer runs the interactive review in the main session.
3. `review-clerk` owns the durable writes at the close.

Per-grade `grade-audit` validates each verdict as it is presented. The review-session gate validates the persisted writes against the transcript and those verdicts. A review-clerk persists the `Reviews/Review — [Concept] — [Date].md` notes, the `Sessions/Session — …md` note, and the touched `📚 Active Concepts.md`, `🧯 Mistakes.md`, and `Attempts.json` rows.

- Verifier: the `review-session-audit` subagent on `muse-spark-1.3-contributor`, high, read-only. Send this envelope: `{"gate":"review_session","concepts":[...],"transcript":"exact Q/A + learner answers + claimed verdicts","grade_verdicts":[{"concept","correct_verdict"}],"written_files":[{"path"}],"state_rows":"...","pass_number":N}`.
- The gate arms when the delegated `review-clerk` run returns, or when the main session writes the session note. It withholds the closing summary until a receipt exists (`NO_REVIEW_SESSION_AUDIT`). An untagged closing summary counts as an implicit `[[TURN:none]]` once the receipt is present, so a dropped tag never dead-ends the session.
- Verdict: `PASS|ISSUES`, plus `issues` and `context_notes`. An `ISSUES` verdict withholds the close summary (`REVIEW_SESSION_AUDIT_ISSUES`). Fix the writes by re-dispatching `review-clerk`, then re-audit until `PASS`. There is no cycle cap.
- Scope is fenced. MISSION, CURRICULUM, Learning Profile, Learner History, `Knowledge Wiki/`, and git drift go in `context_notes`, never `issues`. `audit_state.py` owns state drift and the review-clerk runs it. `review-gate` owns the wiki.

## Config

- Verifier: the `review-gate` agent, dispatched with `dispatch({ agent: "review-gate", task: { ...envelope... } })`. The `task` is the envelope as an object, never a JSON-encoded string. It runs on `muse-spark-1.3-contributor` by default. This is a separate run with its own context, dispatched by the parent and not by the Clerk whose writes it reviews. Model separation from the writer is a preference, not a guarantee.
- The `learning-gate` extension enforces the gate by requiring a matching receipt. The fixed `review-gate` agent prompt enforces it too. Do not bypass either.
- Envelope schema: `{"gate":"review","concepts":[...],"target_files":[{"path","content"}],"out_of_scope":[...],"source_url"|"source_file"|"lesson_ref","pass_number":N}`.
- Verdict schema: `{"verdict":"PASS|ISSUES","evidence":["<file read / check run>",...],"issues":[{"severity","location","issue"}],"context_notes":[{"location","note"}]}`. The `evidence` field is mandatory. A verdict without it is surfaced as unsubstantiated. Any `issues` entry blocks at any severity.
- `review-gate` has no `bash` tool. Fetch sources through `pi-web-access` `fetch_content`. It cannot and must not audit git history or the whole repo.

The canonical review prompt is fixed in `.pi/agents/review-gate.md`. Send data only.

## Steps

### 1. Determine the ingest type

A new concept, meaning no overlap existed, gets the quality gate and the factual spot-check. An enrichment, meaning an existing concept was updated, gets the quality gate only.

### 2. Run the quality gate

Dispatch one foreground `review-gate` envelope:

```json
{"gate":"review","concepts":["Concept"],"target_files":[{"path":"Knowledge Wiki/wiki/<page>.md","content":"exact written text (must match disk — generation-to-emission, never a summary)"}],"out_of_scope":["MISSION.md","CURRICULUM.md","Learning Profile.md","Learner History.md","Mistakes.md","Attempts.json","lesson/session/log bookkeeping"],"source_url":"https://...","lesson_ref":"Learning System/Lessons/...md","pass_number":1}
```

A grounding field is required: `source_url`, `source_file`, or `lesson_ref`. Every concept must appear in `target_files`. Never put state files in `target_files`.

Save the verdict JSON to `Learning System/Reviews/Quality Gates/<concepts>-pass<N>-<date>.json` and show it to the user.

### 3. Run the factual gate for new concepts

For each new concept, spot-check 1 or 2 load-bearing factual claims such as mechanisms, formulas, and definitions against authoritative sources. Flag mismatches. If the check is inconclusive, note it as unverified rather than flagging it.

### 4. Fix until the gate is clean

On any `issues` entry, at any severity, fix the target text. Then re-run the quality gate with the updated target text and the same sources and concepts. There is no cycle cap. Keep fixing and re-running until the gate returns `PASS` with zero issues. Never ask the parent or another agent to run a pass on your behalf.

A clean target gets `PASS`. Remaining `ISSUES` are surfaced only when they are out-of-scope bookkeeping demoted to `context_notes`. The reviewer never rewrites content. You own the final wording.

### 5. Report

Tell the user concisely:

- the gate result per concept, including how many cycles it took and any remaining flags;
- the verdict file paths;
- what you fixed;
- anything unverified or still flagged.

If the result is not `PASS`, say so plainly. The ingest still proceeds with a visible `⚠️ REVIEW FLAGS SURFACED` banner. It is not blocked. That banner applies only to out-of-scope bookkeeping flags demoted to `context_notes`. In-scope issues still block the review-session close and keep the uncapped fix loop running until `PASS`. The ingest turn itself is never hard-blocked.

## Rules

- Never skip the gate silently. If it cannot run, say so and surface what was unverified.
- Never run this gate on lesson files, learning records, or glossary promotions. Those use `fact-check` and `tutor-audit`.

