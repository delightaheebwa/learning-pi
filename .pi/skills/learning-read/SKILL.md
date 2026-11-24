---
name: learning-read
description: Run a Sung-style reading session. Use when the learner declares what they are about to read ("I'm going to read ...", "I'm reading ...", "reading session") and attaches the source text. Scope the reading, then check what the learner retrieves.
---

# Learning read: reading flow

This is the reading half of the learning system. It runs in the main pi session. It is lighter than the interrogation flow: no triage table, no attack battery, no repair ladder, no graduation clone. The learner reads the source, then retrieves it and diagnoses their own model.

Read the stance in `APPEND_SYSTEM.md`. Where this skill and the stance disagree, the stance wins.

## Pipeline

1. **Declare and attach.** The learner names the source and attaches the text. The scope comes from that text, never from memory.
2. **Session brief.** State where to stop reading, what the learner will be able to do, the benchmark, and the plain keywords. Then stop; the learner reads.
3. **Learner reads.** No session turns while they read.
4. **Free recall.** Closed book, the learner dumps what they remember. No interruption and no correction mid-dump.
5. **Confidence.** The learner marks each item `sure`, `hunch`, or `no-idea` before any feedback.
6. **Quoted check.** Return the itemized check against the attached text, with a source quote for every wrong or missing item.
7. **Model presentation.** The learner presents their mental model in any form. Do not restate it and do not redraw it.
8. **Diagnosis.** Return `right`, `wrong`, `missing`, and `misplaced` relations with quotes. Supply no corrected version.
9. **Close.** Record what was read, the benchmark, and the trajectory. Retrieval shots run at +1 day, +1 week, and +1 month.

## Turn kinds

A claims turn in this flow declares exactly one kind:

| Turn | `turn_kind` | Extra field |
| :--- | :--- | :--- |
| Session brief | `plan` | none |
| Free-recall check or model diagnosis | `answer` | none |

Any other kind, or a missing kind, is withheld with `FOUNDATION_INCOMPLETE` and a remedy naming the fix. The interview kinds (`triage`, `attack`, `autopsy`, `repair`, `idea`) do not apply here. `[[TURN:quiz]]`, `[[TURN:grade]]`, and `[[TURN:none]]` work as in the other flows, and every claims receipt still binds on `rendered_content`.

## Modules

| Module | Owns | Spec |
| :--- | :--- | :--- |
| `benchmark-session` | Session brief: stop point, outcome, 5 low / 5 mid / 5 high questions, plain keywords | `docs/specs/SPEC-benchmark-session.md` |
| `free-recall` | Closed-book dump, confidence before feedback, quoted check | `docs/specs/SPEC-free-recall.md` |
| `model-diagnose` | Model presentation and grounded diagnosis, never a rewrite | `docs/specs/SPEC-model-diagnose.md` |
| `benchmark-retrieval` | Fixed +1d / +1w / +1m shots, misses re-appear, scores vs 90 / 80 / 70 | `docs/specs/SPEC-benchmark-retrieval.md` |

## Phase 2 sections (skeleton)

These sections are placeholders. Each owning module fills its own; until then, the pipeline above is the whole flow.

### Session brief

One `[[TURN:claims]]` turn with `turn_kind:"plan"`, then stop until the learner has read. Four parts, in order:

1. **Scope.** Where to stop reading and why, sized to one sitting, taken from the attached text (chapter or section boundaries). Never invented.
2. **Outcome.** What the learner will *do* with the knowledge up to that point, as performance, not coverage: "predict how a fee change moves behavior", not "finish pages 1-24".
3. **Benchmark.** Exactly 15 questions: 5 low (recall/understand), 5 mid (apply), 5 high (evaluate/judge). Free recall only: no MCQ, no true/false. Mid and high are written at the level and cue-style of real use, real scenarios and decisions, not trivia. Label each on its own line, starting the line with its level so the labels stay greppable: `Low: ...`, `Mid: ...`, `High: ...`. Targets, from memory: 90% low, 80% mid, 70% high.
4. **Keywords.** The minimal necessary set of plain keywords from the scoped text. A flat list: no groupings, no relations, no connections. The learner does the connecting.

State the retrieval dates in one line: the benchmark returns at +1 day, +1 week, and +1 month.

No attached text: ask for the text and stop. Never generate questions from general knowledge of a title. No teaching in the brief: no answers, no explanations, no content summaries; gist-level orientation only.

### Free recall

Closed book, no interruption. The learner dumps everything they remember from the scoped reading, in any form: prose, list, rough map. Do not comment, correct, or complete anything mid-dump. If they ask "is this right?" mid-dump, decline and ask them to finish first.

After they signal the dump is complete, they mark each dumped item `sure`, `hunch`, or `no-idea` before any feedback is revealed.

Then one `[[TURN:claims]]` turn with `turn_kind:"answer"` returns the itemized check against the attached text:

- **wrong**: contradicts the source. Quote the source passage.
- **missing**: load-bearing content in the scoped text the dump omitted. Name it and quote it; never explain it into place.
- **right**: confirmed briefly. No re-teaching, no polished restatement.

Every verdict carries a source quote. `sure`-but-wrong items are the most urgent gaps: record them under a `priority_gaps` heading in the session handoff so retrieval prioritizes them. The same procedure runs verbatim at the start of every retrieval session (+1d/+1w/+1m) over the same scoped material.

Forbidden: feedback of any kind before dump-complete plus confidence marks; rewriting or "cleaning up" the learner's dump; filling gaps proactively.

### Model diagnosis

Placeholder, owned by `model-diagnose`. Fill with the four diagnosis buckets and the no-rewrite rule.

### Retrieval sessions

Placeholder, owned by `benchmark-retrieval`. Fill with the fixed shots, the rescoring rule, and the persistence shape.

## Every turn

Begin every assistant message with a turn tag. Dispatch each verifier once in the foreground with `dispatch({ agent, task: { ...envelope... } })` and emit the verified draft unchanged. No gate or tooling commentary in learner-visible text.
