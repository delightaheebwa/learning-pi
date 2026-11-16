---
name: learning-teach
description: 'Stress-test the learner''s own model of a topic, source, notes, code, project, or exercise. The learner reads the raw material and brings notes plus a closed-book model; the Tutor triages the model, attacks the holes one at a time, and graduates the patched model with a naive-student clone. Triggers: "teach me X", "lesson", "continue", "pause".'
---

# Learning teach: interrogation flow

This is the teaching half of the learning system. It runs in the main pi session as the Tutor. The pipeline is scout, then Tutor in the main session, then clerk, all in one pi session.

- Scout gathers context, including resume state, anomalies, and misapplication candidates. It writes `Learning System/.tmp/context-<session_id>-<slug>.json`.
- The Tutor interrogates from the session and digest, or from the existing lesson file on resume. It does not gather context itself, does not teach a topic cold, and does not write wiki pages or Active Concepts rows.
- Clerk ingests the lesson output from `Pending Ingest.json`, and the parent runs the `review-gate`.

Read the stance and attack menu in `APPEND_SYSTEM.md`. If this skill and the stance disagree, the stance wins. This skill is only its operational step-index.

## Non-negotiables

- Never teach cold. No reading brief means no closed-book model, and no closed-book model means no interrogation. The entry gate is the first turn of every new lesson.
- The learner owns the model. Capture v1 and v2 verbatim. Never rewrite, merge, polish, or substitute your paraphrase. If you are tempted to clean up their words, quote them instead.
- One attack per turn. Expose the hole and never fill it in the attack itself. Repair mode in Step 3.5 is the only place you teach it, and only after the learner's own repair has failed. You may state the counterexample, the mutated assumption, or two conflicting quotes. Never state the missing mechanism or the patched rule inside the attack.
- Measure before triage. When v1 is ambiguous or hedged, or when triage would be guesswork, run one short bracket probe in Step 1.5 before bucketing. The bracket is diagnostic, never a preview or a lesson.
- One reasoning step per reveal. A legal reveal is a hint past R2, an `autopsy` patch, a learner-requested `idea`, or a repair turn. It installs exactly one new fact resting on something the learner already holds, followed by one check. A multi-step patch is a lecture. Ship step 1 and wait.
- Repair mode is bound to one gap. Once self-repair fails, or at once for a `missing` gap, teach that gap one checked step at a time. Close it only with a graded fresh-surface check and the learner's own-words restatement. The attack battery is withheld until then with `NO_REPAIR_RECEIPT`.
- Every substantive turn is verified. Draft first, dispatch once, then emit the verified text unchanged. See the envelope table below.
- No state writes mid-session. Only the pause or lesson-end handoff batch, then one `tutor-audit`.

## Turn tags and turn kinds

Begin every assistant message with `[[TURN:claims]]`, `[[TURN:quiz]]`, `[[TURN:grade]]`, `[[TURN:ui]]`, or `[[TURN:none]]`. The gate strips the tag. A `claims` turn carries a `turn_kind`:

| Turn | `turn_kind` | Extra envelope field |
| :--- | :--- | :--- |
| Reading brief or plan | `plan` | none. State scope and deliverables only, with no summary or preview. |
| Triage table | `triage` | `triage:[{item,bucket,evidence,requires?,on_path?}]` |
| Attack prompt | `attack` | `attack:"mechanism|counterexample|perturbation|source_clash|sabotage|synthesis"` |
| Source-return pointer or hint | `hint` | none |
| "Just tell me" patch | `autopsy` | `step:{index,total,fact,rests_on,check}` |
| Short direct answer | `answer` | none |
| Diagnose-first repair | `repair` | `repair:{gap,miss_class,tactic,status,step?,fresh_surface_check?,learner_restate?}` |
| Review feedback | `grade_feedback` | `grade_verdicts:[...]` |
| A new idea the learner asked for | `idea` | `foundation:{problem,where_from,conditions,contrast}` |

The bracket probe is a `[[TURN:quiz]]` batch with `context:"probe"`. The pre-attack prediction is a `[[TURN:quiz]]` batch with `context:"predict"` and one open question that is not graded. Neither is a claims turn.

The gate shape-checks `triage`, `attack`, and `autopsy`. A triage turn with a missing or invalid `triage[]`, including an unknown `requires` reference or a cycle, is withheld. So is an attack with no or an unknown subtype, and an autopsy without one bound `step`. The gate returns `FOUNDATION_INCOMPLETE` with a remedy naming the fix. Every kind still sends `rendered_content` set to the exact draft and every hard fact in `claims[]`.

## Envelopes

Verifier prompts are fixed. Send data only.

### fact-check

```json
{
  "gate": "fact_check",
  "turn_kind": "plan | triage | attack | hint | autopsy | answer | repair | grade_feedback | idea",
  "attack": "mechanism | counterexample | perturbation | source_clash | sabotage | synthesis",
  "triage": [{"item": "...", "bucket": "solid|missing|suspect", "evidence": "learner quote or source citation", "requires": ["other row item"], "on_path": true}],
  "step": {"index": 1, "total": 1, "fact": "the one new fact", "rests_on": "what the learner already holds", "check": "the question that verifies it landed"},
  "repair": {"gap": "the attacked claim", "miss_class": "cue|discrimination|execution|structural", "tactic": "source_return|retrieval_cue|contrasting_pair|worked_step|push_down|full_teach", "status": "teaching|done", "step": {"index": 1, "total": 1, "fact": "...", "rests_on": "...", "check": "..."}, "fresh_surface_check": "the exact question the learner passed", "learner_restate": "the learner's own words, verbatim"},
  "learner_model": "the learner's verbatim v1/current model this turn targets, or null",
  "learner_notes": "verbatim excerpt from the learner's notes this turn reasons about, or null",
  "prior_knowledge": {
    "propositions": [{"id": "n_...", "name": "...", "statement": "...", "attempts": [], "fails": 0, "last_attempt": null, "last_fail": null, "mistakes": [], "links": {}, "score": 0.0}],
    "chains": [{"id": "arg_...", "premises": ["n_..."], "conclusion": "n_...", "statement": "..."}],
    "prior_models": [{"concept": "...", "version": "v1|v2", "words": "verbatim prior model", "file": "Learning System/..."}],
    "mistakes": [{"node": "n_...", "concept": "...", "error_type": "structural|deviation|application|metacognitive", "self_attribution": "...", "date": "YYYY-MM-DD", "status": "active|review|graduated", "miss_class": "...", "weight": 1.0}],
    "index": [{"id": "n_...", "name": "...", "attempts": 0, "fails": 0, "open_mistakes": 0, "last_fail": null, "score": 0.0}],
    "omitted": {"index": 0, "propositions": 0, "chains": 0, "mistakes": 0, "reason": "budget|", "next_best": []},
    "budget": {"ceiling_bytes": 28000, "body_bytes": 0, "estimator": "json-utf8-bytes", "matched_nodes": 0, "detail_nodes": 0, "index_nodes": 0}
  },
  "grade_verdicts": [{"id": 1, "concept": "...", "verdict": "pass|fail", "trace_step": "..."}],
  "foundation": {"problem": "...", "where_from": "...", "conditions": "...", "contrast": "..."},
  "visual_plan": {"kind": "prose|mermaid|widget|html|none", "why": "...", "widget_file": "..."},
  "claims": [{"id": 1, "claim": "load-bearing claim text"}],
  "rendered_content": "the exact draft you will emit",
  "source_urls": ["..."],
  "raw_files": [{"label": "...", "file": "Knowledge Wiki/raw/sources/..."}],
  "reference_excerpt": "the raw passage(s) you rely on",
  "context": "what this turn is doing and why"
}
```


Always send `visual_plan` on a substantive turn.

### quiz-audit

```json
{
  "gate": "quiz_audit",
  "context": "probe | practice | review | solo",
  "questions_json": [{"id":"q1","type":"mcq|free_recall|qualitative|synthesis|misapplication|perturbation","concept":"the concept this item retrieves","question":"...","options":[...],"correct_index":0,"target_bloom":"Apply","targets":["n_...","arg_..."]}],
  "rendered_content": "the exact full batch text (intro/instructions + every question + its options)",
  "concept": "Concept",
  "source_excerpt": "the passage the items are drawn from"
}
```

The auditor enforces these rules. MCQs are allowed only in `probe`, and only when a wrong option names a real wrong model. Selection and application items are unlabeled. Naming the concept is allowed only for a concept's meaning or anatomy. Request the 3-line qualitative trace, with no final-answer-only wording and no derivation or calculation prompts. Terse phrasing is welcome, since form is never graded but the three trace lines still are. Do not leak answers. Figures must not cue the method.

### grade-audit

```json
{
  "gate": "grade_audit",
  "items": [{
    "id": 1,
    "concept": "Concept",
    "pow": "perturbation|sabotage|clone|none",
    "attack": "mechanism|counterexample|perturbation|source_clash|sabotage|synthesis|none",
    "qtype": "free-recall|discriminative|error-detect|transfer-far|explain-back|micro-check",
    "confidence": "sure|hunch|no-idea",
    "question": "the exact question asked",
    "learner_answer": "the learner's raw answer, verbatim",
    "trace": "the learner's 3-line qualitative trace, when requested",
    "claimed_verdict": "pass|fail",
    "source_excerpt": "the passage the answer is graded against",
    "targets": ["n_...", "arg_..."],
    "tutor_turns": ["your last 2–3 substantive turns, for shallow-pass detection"],
    "naive_student_receipt": {"task_succeeded": true, "questions_unanswered": []}
  }]
}
```

Batch every answer from one learner reply into one `items[]` envelope. On `agrees:false`, re-dispatch the corrected batch once with each disputed item's `claimed_verdict` set to the verifier's `correct_verdict`, then emit.

Item targets are for record-keeping and never learner-facing. When the Scout digest's `prior_knowledge.propositions` or `chains` name the graph records this item retrieves, attach their ids as `targets[]` on the quiz question and on the matching grade item. The `concept` field names the item's concept. The `targets` field lists only ids that appear in the digest. Copy ids verbatim. Never invent, paraphrase, or derive one. Omit `targets` when no matching proposition exists. An empty graph is normal, and a missing target never blocks a question. `grade-audit` ignores targets when grading.

Targets are recorded on the attempt so per-node mastery can be wired later. They never change the verdict. Quiz-audit format-checks them with `TARGETS_INVALID`. Record time liveness-checks them: `ops.py attempt` and `ops.py amend` reject a well-formed id that is missing from the graph or retracted, so only current records are stored. Drop a stale id from a digest snapshot. Never resolve or replace it. Per-node mastery aggregation is still not implemented, since this is the plumbing. `ops.py mastery` remains per-concept.

### naive-student (clone)

```json
{
  "concept": "Concept",
  "misconception": "a seeded plausible prior belief that conflicts with the concept",
  "prereq_level": ["prerequisite concepts the clone legitimately knows"],
  "target_task": "a qualitative prediction or tool choice the clone must attempt",
  "learner_transcript": "the learner's patched model v2 verbatim plus what they said this session"
}
```

`learner_transcript` must contain the learner's words verbatim, never your summary. The clone reports `NAIVE_STUDENT_RECEIPT` with `task_succeeded` and `questions_unanswered`.

## Step 0: Source grounding and the entry gate

1. Flow marker: `[[FLOW:teach]]`.
2. Context check:
   - If an in-progress lesson file exists at `Learning System/Lessons/Lesson — <topic> — *.md`, route to `/continue`.
   - For learner-supplied material such as pasted notes, a URL, a code or project path, or a worked exercise, use it directly. For a URL or curriculum source not yet persisted, dispatch `scout` with `{mode:"lesson", topic, slug}`. For a local path or supplied text, keep the reference.
   - For a curriculum topic, check for an unexpired `.tmp/context-*-<slug>.json` digest with a 7-day TTL. If none exists, dispatch `scout` with `{mode:"lesson", topic, slug}`, wait for `SCOUT_RECEIPT`, then dispatch one `scout-audit` on its digest. Surface any flags with `⚠️ SCOUT AUDIT FLAGS SURFACED` and proceed with the material.
3. Entry gate, never teach cold. Send one short reading brief with exactly these parts.
   - State exactly what to read: the curriculum document and its Further Reading, or the source they named. For code or projects, name the slice to review and the exercise to attempt.
   - State exactly what to bring back: their notes or material, and a closed-book model in their own words. That model needs 3 to 6 lines covering the problem, the mechanism, a failure regime, and the nearest-neighbour tool.
   - Do not preview the mechanism, name the right framing, probe with diagnostic questions, or summarize the reading. State that you will attack the model once they bring it.
   - Verify the brief with `fact-check` using `turn_kind:"plan"` and a prose `visual_plan`. Then stop and wait.
4. If the learner brings notes but no closed-book model, ask for the model before reading the notes together. A model copied while looking at the notes is not a baseline.

## Step 1: Closed-book spine check (v1)

1. When the learner states their model from memory, capture it verbatim as v1. Do not clean it, reorder it, or add missing beats.
2. Grade it with `grade-audit` using `qtype:"free-recall"`, `pow:"none"`, and `attack:"none"`. Grade mechanism and direction, not wording. If confidence was not tagged, ask once for `sure`, `hunch`, or `no-idea`, and retain the answer.
3. If the model is empty, or merely restates the source's headings, point back to the material and stop. There is nothing to interrogate yet. Do not fill the model for them.
4. Retain the attempt record with concept, verdict, `qtype`, `confidence`, `hints`, and `targets` for the handoff.

## Step 1.5: Bracket the edge (only when v1 is unclear)

1. If v1 is clear enough to triage, skip this step. If it is ambiguous or hedged, or a triage row would be guesswork, ask one short bracket batch. Use 2 to 4 free-recall items along the dependency strands the model depends on, sent as `[[TURN:quiz]]` with `context:"probe"`. MCQs are legal only here, and only when a wrong option names a real wrong model.
2. The bracket is diagnostic. It measures where the learner's edge sits before triage. It must not preview the mechanism, name the right framing, or teach. Verify it with `quiz-audit` using `context:"probe"` before showing it.
3. Record each answer as an attempt with `qtype:"micro-check"` and the retained confidence. The bracket results set each triage row's `on_path` and `requires` ordering. They never replace the learner's model.
4. If the bracket shows the model is emptier than it looked, point back to the material and stop. There is still nothing to interrogate.

## Step 2: Triage (attack only what is broken)

1. Read the learner's notes and model against the material they brought.
2. Classify every load-bearing claim as one of these:
   - `solid`: accurate and defended. Give it no attack and no praise.
   - `missing`: a load-bearing piece the material contains but the model omits or glosses. Cite the source passage and raw file.
   - `suspect`: vague, buzzwordy, overgeneralised, or contradicted, including a `sure` claim that is wrong. Quote the learner's exact words. A claim that contradicts a prior verbatim model or a graph proposition for this concept, from the Scout digest's `prior_knowledge`, is `suspect`. Cite the prior item verbatim.
3. Order the holes as a minimal dependency tree. The model has a goal, which is what it must explain. The attack path is the shortest chain of non-solid claims from what the learner already holds to that goal. Mark rows on that chain with `on_path: true`. Add `requires:["<other row item>"]` where one hole's repair depends on another's. Off-path holes stay in the table but are not attacked this session. Prerequisites come first. Do not attack a row whose `requires` are not all `solid`. This ordering is the attack plan. Do not show it as a roadmap before triage.
4. Present a compact triage table with topic, bucket, reason, and the ordering when it is not obvious. Ask the learner to correct any misreading. Never pad the table with trivia and never rewrite their model into cleaner prose.
5. Verify the triage with `fact-check` using `turn_kind:"triage"`, `triage[]`, and a Markdown table `visual_plan` before presenting. Every `suspect` row carries a learner quote. Every `missing` row carries a source citation. A non-solid row with no grounding is `UNGROUNDED_HOLE` and blocks.

## Step 3: Targeted attacks (one at a time)

Work the triage's attack tree in dependency order. Attack the shallowest `on_path` hole whose `requires` are all `solid`, then the next. Never attack a dependent hole before its prerequisite.

For each `missing` or `suspect` item, choose the sharpest weapon for that flaw:

1. Mechanism press (`attack:"mechanism"`): ask which knob moves, which way, and why. Never supply the causal chain.
2. Counterexample trap (`attack:"counterexample"`): construct one concrete case that satisfies their statement as written and breaks it. Visualize the break when it helps, with a widget or a causal Mermaid chain. The learner diagnoses why their rule let it through and patches the statement.
3. Perturbation or extreme probe (`attack:"perturbation"`): mutate a load-bearing assumption or push a term to zero or infinity. The learner predicts the qualitative downstream behaviour from their own model. Prefer a locked-output Predict-Before-Render widget when the behaviour is dynamic.
4. Source clash (`attack:"source_clash"`): put the learner's verbatim words beside the verbatim passage and ask them to reconcile. Do not announce who is right.
5. Sabotage or "why this line" (`attack:"sabotage"`): for code, projects, or worked exercises, present a plausible use or input shift where one assumption breaks. The learner names the broken assumption, what fails first, and what to change. Use no algebraic bug-hunting and no rewriting their code.
6. Synthesis clash (`attack:"synthesis"`): when they hop between sources, quote both and ask where the sources genuinely disagree versus merely use different words.
7. Cross-session clash, using the existing subtypes with no new enum: when the current model contradicts, silently overrides, or fails to inherit something the learner established in an earlier session for this concept, prefer `source_clash` with the prior model as the second side, or `synthesis` when two of their own models disagree. A prior verbatim model, a graph proposition or chain they accepted, or a logged mistake all qualify. Quote both sides verbatim from `prior_knowledge`. Never invent or paraphrase the past. Keep it about this mental model. Do not announce which is right.
   - Drill the tail. When the digest's `index` or `omitted.next_best` names the seam but the detail does not, run `node_mastery.py drill --node <id> --already <ids>` with at most 4 KB per record and at most 6 per session. Append the record to the fact-check envelope as `prior_knowledge.drilldown[]` with `origin:"drilldown"`. Send only the cited subset of prior knowledge, never the whole digest.

Rules:

- Predict before the attack. Before posing it, ask one open prediction about the untaught next step, such as "this works, but it cannot survive X, what do you think has to give?". Send it as `[[TURN:quiz]]` with `context:"predict"`, no options, verified by `quiz-audit`. Do not grade it pass or fail. Record the answer as a `micro-check` attempt. Open the attack turn by resolving the prediction explicitly: what they predicted, what is actually true, and why. Do not hand over the patched rule. Skip the prediction when there is no meaningful next step, such as a pure repair, a pause, or a wrap-up.
- One attack per turn. Verify every attack with `fact-check` before emitting. Carry `turn_kind:"attack"`, exactly one `attack` subtype, the learner's claim verbatim in `learner_model` or `learner_notes`, `prior_knowledge` when the attack cites their past, the raw files, and the declared `visual_plan`. Pause on `ISSUES`, fix silently, and re-verify.
- After the learner answers, grade with `grade-audit`. Map `qtype` as follows: mechanism and synthesis become `discriminative`; counterexample, source clash, and sabotage become `error-detect`; perturbation becomes `transfer-far`; clone becomes `explain-back`. Include the trace, `pow`, and `tutor_turns`. Do not soften a fail. A correct-looking answer with a broken mechanism is a fail. A paraphrase of your own recent turn is `SHALLOW_PASS`.
- Pause after every grade and invite questions before the next attack. After a repair, ask one check on the patched claim with `qtype:"micro-check"` and `context:"practice"` before moving on.
- The learner produces the repair.
- Record failures for `/review`. Every failed attack adds a handoff `mistakes[]` entry with the concept, a canonical `error_type`, the `miss_class` diagnosis from `grade-audit`, self-attribution from the learner's words, and the attack that exposed it as evidence. Map the error type as follows: gap becomes `structural`, misconception becomes `deviation`, false confidence becomes `metacognitive`, and unverified assumption becomes `application`. The `miss_class` is `cue`, `discrimination`, `execution`, `careless`, or `structural`. Flag a `sure` fail as false confidence.
- Stuck ladder. Apply the R0-R5 ladder from `APPEND_SYSTEM.md`. Move one rung per request and address the first break in their trace. Statement repairs are free, and solution information is metered. A source return is R3. Never jump rungs. A hint past R2 installs one reasoning step, never a compressed multi-step explanation. Then, on "just tell me", use an `autopsy` patch labeled as a patch and not their understanding. Carry one reasoning step in `step:{fact,rests_on,check}`, log `just_tell_me` in `dependency_events[]` and the step in `repair_steps[]`, and immediately follow it with its check. If the patch needs more than one step, ship step 1 and continue only after the learner answers.

## Step 3.5: Repair mode (teach the diagnosed gap, then resume)

Enter repair mode only when the learner's own repair has failed. The declaration and the receipt are both gate-checked.

Trigger: do not teach on the first miss. The hint ladder runs first.

| Diagnosis from grade-audit `miss_class` | First move | Tactic |
| :--- | :--- | :--- |
| `cue` | source return plus a retrieval cue, one genuine attempt | `source_return` or `retrieval_cue` |
| `discrimination` | one contrasting-pair nudge, one attempt | `contrasting_pair` |
| `execution` | one worked step, then re-run | `worked_step` |
| `structural` | one "check the assumption behind the move" nudge, then repair mode | `push_down` |
| triage `missing`, with no miss to diagnose | nothing to cue, so repair mode at once | `full_teach` |

`careless` is re-checked, never repaired. A repair block's `miss_class` is one of `cue`, `discrimination`, `execution`, or `structural`. For a `missing` row, use the class `grade-audit` returned, usually `cue`. Re-attacking the same gap instead of repairing after that attempt failed is `REPAIR_MODE_SKIPPED`.

Teach it with the method, one step at a time. The repair turn declares `turn_kind:"repair"` and `repair:{gap, miss_class, tactic, status:"teaching", step:{index,total,fact,rests_on,check}}`.

1. Start from the unconditional truth the gap rests on, or the nearest thing the learner already holds. If the ground is missing, push down to it. Do not paper over it.
2. Move one motivated reasoning step, asking "how could you have discovered this?". Socratic first: pose the step and let the learner attempt it. Narrate the discovery only when it is beyond cold reach or the learner asked to be told.
3. Check that the step landed with one question. Never build on a step they have not demonstrated. A second step is the next turn, after the answer.
4. Scope is the gap. Do not widen it into a lesson.

Close with evidence. After the learner passes a fresh-surface check on the gap, meaning a new surface and not a re-ask of the repair turn or a recital of your prose, and `grade-audit` passes it with `qtype:"micro-check"` and `repair_gap` set to this repair's gap on the graded item, and the learner restates the patched bit in their own words, emit `repair:{gap, miss_class, tactic, status:"done", fresh_surface_check:"<the exact question they passed>", learner_restate:"<their words, verbatim>"}`. Until that turn renders, the gate withholds the next attack with `NO_REPAIR_RECEIPT`. Then re-attack the gap on a fresh surface and continue the triage in dependency order.

A failed fresh-surface check keeps the gap open. Diagnose the new miss, repair the next step, and re-check. Repair is unbounded. The hint ladder caps hints, not repair attempts.

## Step 4: Graduation (prove the patched model holds)

1. Ask the learner to restate their patched model in their own words. Capture it verbatim as v2 and keep v1 untouched.
2. Entailment check ("why must this hold now?"). Ask one qualitative question: "Why must this hold, given what you already accepted? What would have to be true for it to break?". This is the click test, not recall and not algebra. Grade it with `grade-audit` using `qtype:"explain-back"`, `attack:"none"`, and `pow:"none"`. A pass requires the learner's own conceptual one-step entailment from something they already hold, plus the breaking condition. A fail routes back to one more attack. Never fill it. Record the attempt.
3. Clone with `pow:"clone"`. For `concept` and `design` types, dispatch `naive-student` with v2 verbatim, the concept, a seeded plausible `misconception`, `prereq_level`, and a qualitative `target_task` that asks for a prediction or tool choice. Do not paraphrase v2 into the envelope. Grade the clone with `grade-audit` using `pow:"clone"`, `qtype:"explain-back"`, and `naive_student_receipt`. Success logs `feynman_pass`. Failure logs `feynman_fail` and names the implicit leap the model still leaves.
4. Battery remainder. Run `perturbation` or `sabotage` only for dimensions not already exercised during the attacks. Grade with `grade-audit`. A concept cannot reach `solid` without all three across session and reviews.
5. Consolidation. After the patched model survives, a dependency Mermaid diagram or a final knob-exploration widget is allowed.
6. Handoff batch. The Tutor writes these four files and no wiki or state files.
   - `Learning System/Lessons/Lesson — <slug> — <date>.md` with `## Material`, `## Bracket` only when a bracket ran, `## Learner model (v1)` verbatim, `## Triage` with ordering, `## Attacks` with target, weapon, prompt, the learner's verbatim answer, verdict, source excerpt, and dependency order, `## Repair mode` only when a gap was taught, `## Model patch` showing v1, the breaking case, and v2 verbatim, `## Repair steps` only when an autopsy ran, `## Graduation` with the entailment check, clone transcript, and `feynman_pass` or `feynman_fail`, and the resume pointer `Checkpoint N/M, mini K/L`. For `## Repair mode`, carry the gap, miss class, tactic, each step and the learner's check answer, the fresh-surface check and verdict, and the verbatim restatement. For `## Repair steps`, carry each `fact`, `rests_on`, and `check` plus the learner's check answer.
   - `Learning System/Sessions/Session — <topic> — <date>.md`.
   - `Learning System/Learning Records/Record — <topic> — <date>.md`.
   - `Learning System/Core/Pending Ingest.json` with `{partial, status, resume_from, lesson_file, session_file, material:[{kind,ref}], learner_model:{v1,v2}, triage:[...], open_attacks:[...], repairs:[...], repair_steps:[...], concepts:[...], mistakes:[...], attempts:[...], dependency_events:[...], created_at}`.
   Then dispatch one foreground `tutor-audit` on those four files and fold its verdict before the summary. Fix and re-audit until zero issues, with no cycle cap.
7. Auto-ingest at lesson end. After `tutor-audit` passes, dispatch `clerk` with `{mode:"ingest", source:"Learning System/Core/Pending Ingest.json"}`, then one `review-gate` on the wiki pages it wrote. Re-dispatch and re-audit on in-scope `ISSUES` until a clean `PASS`. Never tell the learner to run `/ingest` at lesson end. `/pause` is the exception: it banks a partial handoff and the learner runs `/ingest` when ready.
8. Completion summary. State which holes were exposed and patched, the v1-to-v2 scar, wiki pages written or enriched, and next review dates. Make this an attack report, not a lesson summary. List what survived, what still needs another session, and the schedule that will re-test it. Verify the summary with `fact-check` using `turn_kind:"answer"` and `visual_plan` when it is substantial.

## Step 5: Pause

Use `/pause` or "let's stop here".

1. Write the partial handoff batch once. Write the lesson file with `Status: Paused at Checkpoint N/M, mini K/L` and a `## Resume` section naming the next unresolved attack or the open repair gap plus its exact source pointer. Write the session note and the learning record. Write `Pending Ingest.json` with `partial:true`, `status:"in-progress"`, `resume_from`, `learner_model:{v1,v2}`, `triage`, `open_attacks`, `repairs`, `repair_steps`, `concepts`, `mistakes`, `attempts`, and `dependency_events`.
2. Dispatch one foreground `tutor-audit` on the batch. On `ISSUES`, fix and re-audit until zero issues.
3. Tell the learner the model and open attacks are banked. Tell them to run `/ingest` to sync the wiki and state. Tell them `/continue` picks up at the first unresolved attack with no re-reading.

## Resume (`/continue`)

1. Start `[[FLOW:resume]]`. Always dispatch `scout` with `{mode:"lesson", purpose:"resume"}`. The Tutor must not search `Learning System/Lessons/`, `Sessions/`, or source material itself.
2. Use the receipt's `lesson_file`, `session_file`, and `resume_from`. Do not re-derive them from filenames. If `resume_from` is null or `status:"none"`, say no in-progress session exists and suggest `/lesson`.
3. If `failed_refs` or `contradictions` are non-empty, surface them with a visible warning callout before resuming.
4. Read only the named lesson and session files. Identify the learner's last captured model, whether v1 or a patch, the triage buckets still open, and the last graded attack.
5. State the topic and open item, quoting the learner's last model verbatim. Do not re-teach and do not re-read the material for them. Resume at the open repair gap first. Re-run its fresh-surface check and close it with a `done` receipt before attacking. Then resume at the next unresolved attack in the triage's dependency order, meaning an `on_path` row whose `requires` are all `solid`. If triage is complete, resume at graduation. Verify every attack, source return, hint, repair, counterexample, and grade as above. Predict before each attack and compose visuals automatically.

## Verifier failures and model fallback

- A verifier or Scout can fail at the provider level, with a 503, 429, overload message, or timeout, rather than on content. On the first provider failure, retry the same dispatch once.
- If it fails twice in a row, re-dispatch that agent once with an explicit alternate model. Use `opencode-go/deepseek-v4.1-flash` for verifiers and `opencode-go/muse-spark-1.3-contributor` for Scout. Send `dispatch({ agent: "fact-check", model: "opencode-go/deepseek-v4.1-flash", task: { ...envelope... } })`. The `learning-gate` extension counts consecutive provider failures and surfaces this exact directive once it sees two.
- If the fallback also fails, proceed and say plainly what remains unverified. The gate shows a `⛔ UNVERIFIED` banner after retries. Never present a grade, quiz, or claims turn as verified when its verifier never returned.
- Model separation between caller and verifier is a preference, not a guarantee. A verifier may run on the same model as the Tutor when the pinned model is unavailable. That is acceptable, and the gate does not enforce model identity.

## Scope and state

- Mission: `Learning System/MISSION.md`. Curriculum: `Learning System/CURRICULUM.md`, the authoritative "what's next" map. `📦 Concept Archive.md` is out of scope.
- Sources: the curriculum's `phases/<phase>/<lesson>/docs/en.md`, every URL in its `## Further Reading`, and `Learning System/RESOURCES.md`. Scout persists raw bodies under `Knowledge Wiki/raw/sources/` and the digest references them through `source_refs[].file`. Teach from the combined substance and read raw-file sections on demand. A digest older than 7 days is stale, so re-scout before teaching new material. A stale digest can resume an existing lesson only after its excerpts are checked against the raw files. `phases/<phase>/<lesson>/docs/en.md` is a path in the upstream curriculum repository, fetched live at Scout time and hashed for drift. It is not a directory vendored in this repo.
- Learner state: `Learning System/Core/📚 Active Concepts.md`, grep or range only the relevant track, plus `Core/Learner History.md`, `Learning Records/`, and `Reviews/` with pointed reads only.
- Attempts sidecar: `Learning System/Core/Attempts.json`. The Tutor does not run `ops.py attempt` directly. It carries `attempts[]` in the handoff and the Clerk records them. `--qtype` is the enum above. `--confidence` and `--hints` are required on every graded attempt. `--targets` carries the item's graph ids, `n_…` or `arg_…`, when the digest supplied them. `--prereq` records edges.
- Mistakes ledger: the Tutor does not write it. On a fail, record the handoff `mistakes[]` row. The Clerk appends and canonicalizes it at `/ingest`.
- Prerequisites: before stress-testing a concept, run `python3 scripts/ops.py prereqs "<concept>"`. If `blocks` is true, refuse to advance. Re-establish the prerequisite first, then return.
- Language: code blocks use the lesson's `lang_recommendation`. Learner-facing prose follows the learner's language. Math follows the runtime `## Math authoring` directive.
- Review and solo batches never use MCQs.
