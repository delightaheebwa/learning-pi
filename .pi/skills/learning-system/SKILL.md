---
name: learning-system
description: Run the spaced-repetition learning system. Use for "review" (review the active track), "solo" (AI-free closed-book check), "ingest" (ingest new content), "teach me X"/"learn"/"study" (teaching loop, delegated to the learning-teach skill), and "lesson"/"continue" (next curriculum lesson, delegated to learning-teach). Loads Core state from the repository working copy, executes the review/ingest/teach flow, and persists session notes, wiki updates, and Active Concepts changes.
---

# Learning system

The active learning system. It runs in pi against the learner state tree in the current working directory.

## Read this first

### Trigger routing

- "review" runs the review flow for the active track in the main session.
- "solo", "AI-free check", or "closed-book" runs the solo flow. This is a closed-book review of the active track. The gate withholds teaching with `SOLO_NO_TEACHING`. The queue and close are the same as the review flow, but `review-clerk` records every attempt with `mode:"solo"` so the attempt feeds the independence gate. Teaching and hints are impossible by construction. Grade the closed-book answers only.
- "teach me X", "learn", or "study" starts the teaching loop. Use the `learning-teach` skill, not a review. The word "review" on its own still means the review flow.
- "lesson" or "continue" starts the next curriculum lesson. Use the `learning-teach` skill.
- "I'm going to read ...", "I'm reading ...", or "reading session" uses the `learning-read` skill, not a review and not a teach session. The learner attaches the source text and the session brief scopes it.

### Position discipline

The current lesson and phase are not recorded in this skill. Derive them at runtime from `Learning System/CURRICULUM.md`, `Learning System/MISSION.md`, and the newest files in `Learning System/Lessons/` and `Learning System/Sessions/`.

If those sources disagree, stop and report the contradiction to the user before doing any work. Do not guess or merge. The state files are the only source of position, and this repo has known stale statuses.

### Turn tags

Begin every assistant message with one of these tags. The gate enforces the rule.

- `[[TURN:claims]]` for teaching, claims, and plans.
- `[[TURN:quiz]]` for a question batch.
- `[[TURN:grade]]` for grading a learner answer.
- `[[TURN:none]]` for transitions and summaries.

The gate strips the tag before the learner sees it. It withholds a message whose tag is missing or unsupported by a matching, passing verification receipt. A receipt can recover a dropped tag: `grade` and `quiz` come from `grade-audit` and `quiz-audit`, and `claims` comes from a `fact-check` whose `rendered_content` covers the text. The gate does not infer `none` for ordinary turns. The only implicit `none` is the ingest or review close summary after its writer and audit return.

Dispatch each verifier once per turn with `dispatch({ agent, task: { ...envelope... } })` in the foreground. Never re-verify the same draft. On a match or binding withhold, re-emit the verified text or fix the tag.

### Context discipline

Sessions die when the conversation outgrows the model's context window. Every tool output stays in the transcript forever. The fix is fewer, denser tool calls, not smaller messages.

- Batch all reads. Never chain multiple full-file reads for state. Call the batch tool once with `python3 scripts/ops.py ...`, using paths relative to the repo root.
  - At session start, use `python3 scripts/ops.py state <track>`. For reviews, add `--review` for the compact profile and due queue.
  - For a mix of ranges, tails, and greps, use `python3 scripts/ops.py bundle "PATH:N-M" "PATH:-N" "PATH@regex1|regex2"`.
- Read wiki pages by section. First list headings with `bundle "Knowledge Wiki/wiki/<page>.md@^## "`, then fetch only the section you enrich.
- Batch all writes. Persistence at session end is one apply call, not many writes. Use `python3 scripts/ops.py apply <<'SPEC'`, then a JSON spec, then `SPEC`. The spec is `{"writes":[{"path","content"}],"appends":[{"path","content"}],"replaces":[{"path","find","replace_with"}]}`.
- Budget new tool output, not call count. Never re-read a file already in context. Never dump a whole file when you need one row. Treat every tool result as permanent. Prior knowledge comes from `node_mastery.py` inside its byte budget. A drill-down costs one node record of at most 4 KB, with at most 6 per session. For git, use `git diff --stat`, not a full diff. Use `git diff -- <path>` only for a file you need. Do not switch models mid-flow. That invalidates the prompt cache and re-bills the whole context.

## State files

Paths are relative to the working repository root.

- `Learning System/Core/💡 Learning Profile.md` holds learner preferences. Read it at session start.
- `Learning System/Core/📚 Active Concepts.md` holds per-track concept rows with a `Type` of `memory`, `concept`, `procedure`, or `design`. Type drives scheduler intervals. Grep or range only the needed track. Never read the whole file. `📦 Concept Archive.md` is out of scope.
- `Learning System/Core/Attempts.json` is the evidence-based mastery sidecar with attempt history, interval index state, and Feynman pass. `ops.py state` bundles it. Report it with `ops.py mastery <track>`. The report is advisory, not blocking. It shows recall, conceptual, procedural, transfer, independence, and stability scores, plus per-concept `calibration` and `transfer_ok`. A dimension with no evidencing attempt shows `—`, meaning unknown, never 0.
  - `ops.py attempt` accepts optional `--confidence sure|hunch|no-idea`, `--hints N`, `--mode normal|solo`, `--targets n_...,arg_...`, and `--prereq NAME`. Mode solo means AI-free. `--targets` carries the graph ids the item retrieved. The command format-checks them and liveness-checks them, so it rejects a missing or retracted id. Only current graph records are stored. Drop a stale digest id; never resolve or replace it. Per-node mastery aggregation is not implemented, so `ops.py mastery` stays per-concept. `--prereq` is repeatable. `--qtype` is an enum, and unknown values are rejected. A failed `mode=solo` attempt blocks the `solid` tag through the independence gate. A `concept` or `design` entry cannot be `solid` without a Feynman pass.
  - `ops.py calibration [TRACK]` reports confidence calibration. `ops.py prereqs "<concept>"` reports prerequisite state, where `blocks` means a fuzzy direct prerequisite. `ops.py grade-mcq --key A,B,C --answers A,C,C` grades legacy probe MCQs deterministically. Review and solo batches never use MCQs.
- `Learning System/Core/Learner History.md` is the compact tutor background generated by `scripts/learner_history.py`. Read it for learner context. Never grep `Archive/`.
- `Learning System/Core/🧯 Mistakes.md` is the structured wrong-answer ledger with error type and self-attribution. Due mistakes are priority 1 in the review queue.
- `Learning System/Core/📦 Concept Archive.md` holds paused and archived concepts. Do not grep it. It is out of scope. Search it only on an explicit revive request.
- `Learning System/Sessions/`, `Reviews/`, `Lessons/`, and `Learning Records/` receive writes.
- `Learning System/MISSION.md`, `CURRICULUM.md`, `GLOSSARY.md`, and `RESOURCES.md` hold the mission, curriculum, glossary, and curated readings. The curriculum source is a source, not the source. Enrich from its Further Reading.

## Teaching flow

Trigger: "teach me X", "lesson", or "continue".

### Step 0: Scout for a new lesson

If no `Learning System/Lessons/Lesson — <slug> — *.md` exists for the topic and no unexpired `.tmp/context-<session_id>-<slug>.json` exists, call the scout agent first. The digest has a 7-day TTL. Dispatch with `dispatch({ agent: "scout", task: "<topic/lesson + why>" })`.

Scout reads `MISSION.md`, `CURRICULUM.md`, `RESOURCES.md`, the relevant Active Concepts rows, and the curriculum source for the next lesson. That source is the live `phases/<phase>/<lesson>/docs/en.md` plus every URL in its `## Further Reading`. It fetches with this loop:

1. Direct `curl -L --max-time 30` into `.tmp/`.
2. For PDFs, extract the text.
3. For YouTube, run `yt-dlp --skip-download --write-auto-subs`.
4. For bot-blocked HTML, use `curl https://r.jina.ai/<url>`.
5. Use web search last.

Scout hashes fetched bodies, compares each hash to any prior digest hash, and surfaces drift with `SCOUT DIGEST: ⚠️ Upstream changed`. It writes `Learning System/.tmp/context-<session_id>-<slug>.json`. The digest has this shape:

```json
{
  "goal": "...",
  "slug": "...",
  "tracks": ["..."],
  "concept_rows": ["..."],
  "prereqs": [{"concept": "...", "keywords": ["aliases", "variants"], "why": "..."}],
  "source_refs": ["rohit_source", "external_ref_1"],
  "rohit_hash": "...",
  "external_refs_hashes": ["..."],
  "failed_refs": [{"url": "...", "reason": "..."}],
  "lang_recommendation": "Python | TypeScript | Rust",
  "fetched_at": "...",
  "roadmap_sha": "...",
  "synthesis": "per-strand, with a theory line for each"
}
```

Every source and external ref carries an `excerpt` of about 500 characters, a `theory_excerpt` with the derivation, mechanism, and assumptions, `takeaways`, and `adds_vs_rohit`. The top-level `synthesis` is per strand and carries a `theory` line with the mechanism, derivation, assumptions, and nearest-neighbour contrast for the foundation beat. Rohit is the agenda and the externals are enrichment.

The `prereqs` field is load-bearing. It is a list of `{concept, keywords:[aliases/variants], why}` covering every load-bearing dependency. The lesson's `Languages:` header sets `lang_recommendation`, which is Python, TypeScript, or Rust.

Scout posts a short `SCOUT DIGEST:` summary. The gate requires this digest for new lessons. Resuming an existing `Lessons/` file bypasses it.

The lesson-start context audit is parent-owned and mirrors the ingest review gate. When Scout returns its `SCOUT_DIGEST` receipt, dispatch one independent `scout-audit` on the digest with `{"gate":"scout_audit","slug":"...","digest":"Learning System/.tmp/context-<session_id>-<slug>.json","raw_files":[...],"failed_refs":[...]}`. Paths are enough because the auditor reads from disk. Fold its verdict before the first teaching turn.

The gate withholds teaching claims until a valid audit exists (`NO_SCOUT_AUDIT_PASS`). An `ISSUES` verdict surfaces as a banner and never blocks. Fix the digest by re-scouting and re-auditing until `PASS`, with no cycle cap. A digest older than 7 days is stale. Re-scout before teaching new material from it, and never treat a stale digest's source excerpts as authoritative. The state audit warns on TTL, but this rule is hard.

`phases/<phase>/<lesson>/docs/en.md` is a path in the upstream curriculum repository. Scout fetches it live and hashes it for drift. It is not a directory vendored in this repo.

### Steps 1 to 4: Teach

1. Load `Learning System/MISSION.md` and `CURRICULUM.md` to determine the next lesson or the requested topic. Derive the position as described above. If resuming, the lesson file and the last `Sessions/` note are the source of truth, and no Scout digest is needed.
2. For "lesson" or "continue", pick the next lesson from `CURRICULUM.md`, moving sequentially within a mission. If a lesson is resumable, resume where it left off. Never re-teach a `done` lesson. Retrieve-verify it instead.
3. For "teach me X", treat an in-scope topic as a curriculum node. An out-of-scope topic is a one-off that still feeds Pending Ingest for Clerk. Surface the "switching focus?" question.
4. Delegate the full interrogation flow to the `learning-teach` skill. That flow covers the entry gate, closed-book spine check, triage, targeted attacks, and model patch or clone. Verify claims and attacks with foreground `fact-check` agents, question batches with `quiz-audit`, grades with `grade-audit`, and the graduation clone with `naive-student`.

The Tutor does not write wiki pages, Active Concepts rows, or any position or state file such as MISSION, CURRICULUM, Profile, or Mistakes. It writes four handoff artifacts in one batch at pause or lesson end: the lesson file, session note, learning record, and `Pending Ingest.json`. It then hands off to the `clerk` subagent, which reconciles state at `/ingest`. Lesson end auto-ingests inline with `clerk` then `review-gate`. `/pause` is the exception and tells the learner to run `/ingest`.

## Review flow

Trigger: "review". The pipeline is review-scout, Reviewer in the main session, then review-clerk, all in one pi session. The review is interactive, so run it in the main session. Verify grades with foreground `grade-audit` agents. Do not bypass them.

Reviews test cue selection and transfer, not recognition. Items are unlabeled, interleaved, and trace-graded. There are no MCQs in a review.

### Step 0: Review scout

Before the first review turn, dispatch `review-scout` with `dispatch({ agent: "review-scout", task: "<track, or 'active'>" })`. It runs the deterministic queue command `python3 scripts/ops.py queue <track> --digest "Learning System/.tmp/review-${PI_SESSION_ID}-<track>.json"` and fills in the current position.

The digest's `queue` already carries every per-concept field: type, source, `last_q_type`, `question_type`, dates, mastery, Feynman status, and due-mistake `error_type` plus self-attribution. It also carries a grounded `source_excerpt`. The Reviewer does not gather state or build the queue itself.

The gate withholds the first `claims` or `quiz` turn with `NO_REVIEW_CONTEXT` until the scout runs. A partial digest raises a `⚠️ REVIEW CONTEXT INCOMPLETE` banner, not a withhold.

### Step 1: Select the track

Tracks `aiefs` and `aie` are the active track. If the user names an archived track, note that it is archived and offer the active one. With no track named, use the active track.

### Step 2: Read the digest

Read the scout digest. If it is missing, fall back to one `python3 scripts/ops.py state <track> --review` call. Do not read the state files separately.

### Step 3: Use the queue verbatim

The digest's `queue` is the queue. Use it verbatim. Do not rebuild, re-sort, re-filter, or re-derive it. Fewer than 5 entries is normal.

Before asking an entry, check its prerequisites under P1.3. Run `python3 scripts/ops.py prereqs "<concept>"`. If `blocks` is true, re-derive the fuzzy prerequisite first and defer the downstream item.

When a queue entry's type is `benchmark`, follow the `learning-read` skill's Retrieval sessions procedure instead of the standard item.

### Step 4: Compose unlabeled trace items

Compose the items from the queue as scenarios, not one row per question.

- Never name the concept when the item tests tool selection or application. Naming is allowed only when the item directly tests a concept's meaning or anatomy.
- For 3 or more queue entries, compose 1 or 2 composite scenarios that chain concepts from different weeks, plus one known mistake. Grade each component concept separately. Record the scenario-to-concept mapping in the handoff, never in learner-facing text.
- Include at least one decoy or near miss whose surface vocabulary resembles a due concept but violates one of its conditions, so blind application fails.
- When the digest carries `prior_knowledge`, compose at least one cross-session collision. Pit a due concept against the learner's earlier verbatim model or an accepted graph proposition. Ask which is right and what changed. Quote the prior words exactly as the digest carries them. Never invent a past model and never announce the answer.
- For at least one due concept, mutate a load-bearing assumption and ask for the qualitative downstream behaviour. This is the perturbation.
- For the misapplication, present a plausible real-world use where a condition is violated. The learner names the broken assumption and what should have been done instead.
- For `concept` and `design` types, add a teach-the-clone item asking the learner to explain the unlabeled concept. Terse is fine, but the transcript must carry what it is, when and why it applies, the mechanism in one full causal clause, a failure regime, and the nearest-neighbour contrast. The failure-regime line is load-bearing. An example does not replace it. Do not dispatch `naive-student` yet. There is nothing to teach it until the learner answers.
- Request the 3-line qualitative trace: cue and principle, mechanism or knob turn, then direction and extreme check. Say plainly that keyword and telegraphic lines are welcome and that form is never graded, content is. All three lines are still required, but a phrase per line is the default. Do not dock brevity. A conclusion-only line fails as a missing mechanism, not as verbosity. Use no derivation or calculation prompts.
- The 3-line trace is the minimum, not a cap. A longer working trace with thinking out loud is welcome. Grade the trace and infer whether the item was solved rather than demanding a final answer in a fixed form.
- When the digest's `prior_knowledge.propositions` or `chains` name graph records an item retrieves, put their ids in that question's `targets[]`. Copy the ids verbatim from the digest. Never invent them. Carry the same ids onto the matching grade item and into `REVIEW_WRITES.grade_verdicts[].targets` so `review-clerk` records them with the attempt. Omit `targets` when the graph has no matching proposition. The ids never appear in learner-facing text.
- Retrieve from an inactive state. Interleave the queue and never re-ask a concept immediately after its verdict, because the item is still active. Retry later or in a fresh surface. Prefer items with the most decision points, meaning junctures where a not-yet-active proposition must be chosen. Aim for retrieval that succeeds with effort, about 85% per retrieval event. Rescue with the hint ladder rather than lowering the demand.

### Step 5: Present and verify the batch

Present the whole batch in one `[[TURN:quiz]]` message so the learner can answer in one reply. Before showing it, dispatch one `quiz-audit` with `context:"review"`, `questions_json` using types `qualitative`, `synthesis`, `misapplication`, `perturbation`, or `free_recall`, and `rendered_content` set to the exact full batch text. Any issue at any severity blocks. Fix and re-audit until `PASS`, with no cycle cap. Show no visuals in the batch: no widget and no diagram that cues the method until the answers are graded.

### Step 6: Grade the reply

Build grade items with the learner's trace for each item. If the batch contained a teach-the-clone item, dispatch `naive-student` now with the learner's teaching reply verbatim as `learner_transcript`, the concept, a seeded misconception, `prereq_level`, and a qualitative `target_task` drawn from the contrast the learner taught. Await `NAIVE_STUDENT_RECEIPT`.

Then dispatch one batched `grade-audit` with `items[]`, one entry per answer. Carry `pow` set to `perturbation`, `sabotage`, `clone`, or `none`, plus `attack`, `qtype`, `confidence`, `trace`, `tutor_turns`, and `naive_student_receipt` on clone items. Use the verifier's per-item `correct_verdict`. On `agrees:false`, re-dispatch the corrected batch once and emit that. Do not present verdicts yet.

### Step 7: Feedback and the mandatory question pause

Compose learner-facing feedback with the verdict per item, the exact step that passed or slipped, the battery outcome, and one micro-check when a repair is needed. Use prose plus the smallest visual that carries it: a table, a Mermaid causal chain, or a repair widget. Verify it with `fact-check` using `turn_kind:"grade_feedback"`, `grade_verdicts`, `visual_plan`, and `rendered_content` set to the exact feedback.

Present the feedback and pause in the same turn with an explicit invitation:

"Anything here that isn't clear, a verdict, the step you slipped on, or the repair? Ask now. If it's all clear, say 'no questions' and I'll save the session and ingest the results."

Stop the turn. Do not dispatch `review-clerk`, do not ingest, and do not present the completion summary while the pause is open. Silence or a bare acknowledgement is not an explicit "no questions". This is the mandatory question pause.

### Step 8: Inquiry loop

Answer every question as a normal tutoring turn with `fact-check` `turn_kind:"answer"` or `"repair"`, using the same visual discipline. If a question challenges a verdict, re-run `grade-audit` on that item and adopt the verifier's `correct_verdict`. Honor the hint discipline and "just tell me", using an autopsy patch with one reasoning step and its check and logging `just_tell_me`.

Use the R0-R5 ladder from `APPEND_SYSTEM.md` for every hint. Move one rung per request, address the first break in the learner's trace, keep statement repairs free, and meter solution information. The rung needed is a difficulty readout.

When a fail is diagnosed, classify the miss as `cue`, `discrimination`, `execution`, `careless`, or `structural`. Carry `miss_class` into the `REVIEW_WRITES.mistakes[]` row. `grade-audit` already returns it, so do not invent one. After answering, pause again with the same invitation. Advance only on an explicit "no questions", "all clear", or "go ahead". If the answer is ambiguous, ask once more.

### Step 9: Persist

The Reviewer writes no state files. Dispatch one `review-clerk` with a `REVIEW_WRITES` envelope carrying the exact transcript, verifier verdicts, and feedback pause inquiry:

`dispatch({ agent: "review-clerk", task: { "gate":"review_writes", "track":"...", "date":"YYYY-MM-DD", "concepts":[...], "transcript":"...", "grade_verdicts":[{"concept":..,"correct_verdict":"pass|fail","miss_class":"cue|discrimination|execution|careless|structural|null","pow":"perturbation|sabotage|clone|none","q_type":"<enum>","confidence":"sure|hunch|no-idea","hints":N,"feynman":"feynman_pass|feynman_fail|none","targets":["n_...","arg_..."]}], "dependency_events":[...], "mistakes":[{"concept","error_type","miss_class":"cue|discrimination|execution|careless|structural","self_attribution","evidence"}], "digest":"Learning System/.tmp/review-<session_id>-<track>.json" } })`

The transcript field carries the exact Q/A, learner answers, traces, verifier verdicts, and feedback or inquiry.

Review-clerk records attempts including battery outcomes, writes the Review notes and session note, updates the touched Active Concepts and Mistakes rows, runs `audit_state.py`, commits and pushes state only, and returns `REVIEW_CLERK_WRITES`.

### Step 10: Audit the writes

After review-clerk returns, dispatch one `review-session-audit` on the exact writes. Take `written_files` from the receipt's `reviews`, `session`, and `state` fields. Paths are enough.

A `PASS` releases the closing summary. An `ISSUES` verdict keeps it withheld with `REVIEW_SESSION_AUDIT_ISSUES` until the writes are fixed and a fresh audit returns zero issues. There is no cycle cap. Scope is fenced: state drift the review did not write is `context_notes`, never a blocking issue.

### Step 11: Completion summary

Verify the summary with `fact-check` (`turn_kind:"answer"`) when it is substantial. Present per-concept verdicts and mastery movement, ingested or enriched wiki pages, new concepts and next review dates, and the state-audit result. Note open mistakes and what clears them. Do not claim completion if the auditor has not returned `PASS`.

Review-clerk runs the state audit before it returns. Fold its `STATE_AUDIT_VERDICT: {"errors":N,"warnings":M}` verbatim. Review-clerk commits state only, meaning `Learning System/` and `Knowledge Wiki/`, per `Learning System/AGENTS.md`.

## Solo flow

Trigger: "solo", "AI-free check", or "closed-book". This is an unassisted operational check of the active track. It uses the same deterministic queue and close as the review flow, but there is no teaching, no hints, no repair prose, no widgets, and no MCQs.

1. Start `[[FLOW:solo]]`. Dispatch `review-scout` to build the due queue. Use it verbatim and check prerequisites.
2. Compose one closed-book batch from the queue. Use unlabeled operational items with the 3-line qualitative trace, at least one perturbation, one misapplication, one decoy or near miss, and one teach-the-clone item for a `concept` or `design` entry. Use no MCQs and no calculation or derivation prompts. When the digest's `prior_knowledge` names a matching proposition, attach graph `targets[]` to each question and its grade item. Carry them into `REVIEW_WRITES.grade_verdicts[].targets`.
3. Verify the batch with `quiz-audit` (`context:"solo"`). Then present it with this text: "Closed-book check. Work independently without hints or references. Include your 3-line qualitative trace for each item. Phrases and keywords are fine; form is never graded. Reply with your answers and traces."
4. When the learner replies, dispatch `naive-student` for the clone item, then one batched `grade-audit` with `items[]`, traces, `pow`, and `naive_student_receipt`. Report the verifier's Pass and Fail verdicts directly. Give no repairs and no teaching. The only allowed message while the check is open is a `[[TURN:none]]` one-line reminder.
5. Hand the durable writes to one `review-clerk` with `"mode":"solo"` so every attempt is recorded AI-free and feeds the independence gate. Then dispatch one `review-session-audit` on the exact writes. Report the score and updated mastery. The gate withholds `[[TURN:claims]]` as `SOLO_NO_TEACHING` and `[[TURN:ui]]` as `SOLO_NO_AIDS` by construction.

Intervals are type aware: memory uses 0, 1, 3, 7, 14, 30, and 60 days; concept uses 3, 7, 14, and 30 days; procedure uses 3, 7, and 14 days; design uses 14 and 28 days. Benchmark uses 1, 7, and 30 days, fixed regardless of result — each retrieval shot records one attempt and advances the ladder one step.

## Ingest flow

Trigger: "ingest" with content to add, not a review. Delegate to the `clerk` subagent. Clerk reads `Pending Ingest.json` when the ingest comes from a lesson. A standalone ingest passes the supplied content.

1. If `Learning System/Core/Pending Ingest.json` exists because of a lesson handoff, read it. It contains `{partial, status, resume_from, lesson_file, session_file, concepts, mistakes, source_url|source_file, created_at}`. A `/pause` handoff sets `partial:true`. A final lesson end sets `partial:false` and `status:"done"`. Use `lesson_file` as the source of content. Let `status`, `resume_from`, `concepts`, and `mistakes` drive the state reconciliation in step 7b.
2. Otherwise extract concepts from the supplied content.
3. Check for overlap with one bundle call using an alternation regex over candidate keywords: `python3 scripts/ops.py bundle "Learning System/Core/📚 Active Concepts.md@kw1|kw2|kw3"`. Use `#^## <track>` for the full track section.
4. On overlap, enrich the existing wiki page and insight row with genuinely new details. Set `last_reviewed` to today. Write the session note as enrichment, not a new ingest. Read only the target page's relevant section, listing headings first with `@^## `.
5. With no overlap, create a new concept with status `developing`, `last_reviewed` today, `next_review` plus 3 days, and `Last Q Type` set to `definitional`.
6. If the content is outside the focus area, ask about switching focus. Stagger schedules for multiple new concepts.
7. Persist everything in one apply call with the `ops.py apply` heredoc: the wiki pages, the `index.md` update, the `log.md` entry, and the session note.
8. Clerk then extracts and merges the knowledge graph with `graph-extract`, `graph.py merge`, and `graph.py status`. It reports the result in `CLERK_WRITES.graph`. The parent runs the independent `graph-audit` on those records.
9. Reconcile position state from the handoff for lesson handoffs. Use `Pending Ingest.json`'s `status`, `resume_from`, `concepts`, and `mistakes` as the single source for the position pointers in `MISSION.md`, the `CURRICULUM.md` row, `💡 Learning Profile.md` fields Current Focus and Current Position, and the `📚 Active Concepts.md` track header. Add handoff concepts missing from Active Concepts as new rows with status `developing`, today's date, plus 3 days, and `definitional`. Append handoff `mistakes[]` to `🧯 Mistakes.md` with canonical concept names. Sync touched Active Concepts `next_review` and `last_reviewed` from `Attempts.json`. Run `scripts/learner_history.py`. Surface but do not merge any disagreement with the lesson file. Keep these files out of the review-gate `target_files`, because the state audit covers them.
10. Run the independent review gate, owned by the parent. Clerk does not run it. When Clerk returns its `CLERK_WRITES: {"wiki":[...],"state":[...],"concepts":[...],"graph":{...},"commit":"..."}` receipt, the Tutor dispatches one `review-gate` on the wiki pages Clerk wrote. Use `target_files:[{"path":"Knowledge Wiki/wiki/<page>.md"}]` from `CLERK_WRITES.wiki`. Omit `content`, because the gate reads the files on disk. List the state files in `out_of_scope` and pass `lesson_ref` when this came from a lesson. Fold the verdict.
11. On any in-scope target issue at any severity, re-dispatch Clerk with the fix, which writes and commits, then re-review until the verifier returns zero issues. There is no cycle cap. Never re-dispatch review-gate for state or bookkeeping drift. Findings in MISSION, CURRICULUM, Learning Profile, Learner History, Mistakes, Attempts, lesson, session, log, and index are the state audit's job and are demoted to `context_notes`. Never hard-block on demoted review flags. The gate surfaces out-of-scope findings, so do not re-run them.
12. Run the independent graph audit, owned by the parent and enforced by the gate, when the Clerk wrote graph records. If `CLERK_WRITES.graph` lists any created or linked nodes or chains, dispatch one `graph-audit` with a `GATE:graph_audit` envelope: `{"gate":"graph_audit","session":"<session id>","written_nodes":[created plus linked node ids],"written_chains":[created plus linked chain ids],"material":[...],"lesson_ref":"..."}`. Take the id lists from the Clerk's receipt, the material used for extraction, and the lesson file. The ingest close is withheld until this audit returns `PASS` over every written id, with `NO_GRAPH_AUDIT_PASS`. An `ISSUES` verdict withholds it with `GRAPH_AUDIT_ISSUES` until the Clerk records a fix. A fix means retracting the offending id with a reason and re-merging a corrected record. A re-merged retracted id revives with its provenance unioned. A fresh audit must then return zero issues. Never hand-edit the ledgers. There is no cycle cap. Graph bookkeeping outside the written ids is `context_notes`, not a blocker.
13. Clerk runs the state audit before it returns with `python3 "$HOME/learning-pi/pi/audit_state.py" --root .`. It fixes the error or warning findings it touched using the `STATE_AUDIT_FIXES` hints, re-runs once, surfaces hint-less or unrelated findings, and reports `STATE_AUDIT_VERDICT: {"errors":N,"warnings":M}`. Fold that verbatim.
14. Close. If `Pending Ingest.json` has `partial:true` from a `/pause` handoff, ingest today's concepts and keep both the `.tmp/context-*.json` digest and the lesson `in-progress` state. Clear only the marker, then commit and push. The digest's 7-day TTL still applies. Only a final non-partial ingest deletes the consumed digest, clears the marker, and lets the curriculum row go `done`.
15. Write the final summary as a `[[TURN:none]]` turn. Start with the tag and fold in the Tutor's `REVIEW_GATE_VERDICT`, the `GRAPH_AUDIT_VERDICT` when graph records were written, and Clerk's `STATE_AUDIT_VERDICT` markers.

### Handwritten notes

If the source is an image such as handwritten notes or a photo of a page, transcribe it verbatim before extraction.

- Use a vision-capable model by attaching the image to the main session, or ask the user for the text.
- Transcribe verbatim and preserve structure such as headings, bullets, and diagrams in brackets. Allow light cleanup only: fix obvious spelling and expand unambiguous abbreviations such as `bc` to `because`. Do not rephrase, summarize, or interpret.
- Retry once on failure. If it still fails, tell the user. Never skip the image silently.

## End-of-session writes

These writes belong to Clerk for ingest or review-clerk for the review close. The Tutor and Reviewer main session never writes them. Apply them in the delegated agent.

1. Update Active Concepts with statuses, dates, new concepts, and open questions. Preserve existing rows.
2. On `consolidated`, move the concept to `Archive/Consolidated/[concept].md` with name, date, insight, wiki link, and related, then remove it from Active.
3. Write `Sessions/Session — [Topic] — [Date].md` with the date, topic, concepts, statuses, open questions, and a one-line interleaving summary.
4. Run the consistency check with one bundle call that re-greps only the touched rows: `ops.py bundle "Learning System/Core/📚 Active Concepts.md@<concept1>|<concept2>" "Knowledge Wiki/index.md@<title>" "Knowledge Wiki/log.md:-3"`. Verify today's `last_reviewed`, correct `next_review` and `Last Q Type`, all ingested concepts present, wiki pages in `index.md`, and the log entry present. Fix discrepancies in a single apply call. If the user claims stale dates are wrong, cross-check the session notes.
5. Refresh learner context with `python3 scripts/learner_history.py`, which regenerates `Core/Learner History.md`.
6. Confirm completion by saying what was saved and what is due next.

