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

## Procedures

The pipeline above is the order; these sections are the procedures each step follows.

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

The learner presents their mental model in any form: prose, list, ASCII, mermaid, or a photographed drawn map. A photo goes through the existing photo → excalidraw ingestion path documented in `state/Knowledge Wiki/AGENTS.md`; its rules apply as written.

One presentation yields exactly one `[[TURN:claims]]` turn with `turn_kind:"answer"`. Four buckets:

- **right**: relations that match the source. Confirm briefly; no re-teaching, no polished restatement.
- **wrong**: links or claims that contradict the source. Quote the learner's words, quote the source, say what is wrong. Supply no corrected version.
- **missing**: load-bearing concepts from the scoped text that the model omits. Name each and quote it; never explain it into place.
- **misplaced**: relations present but wrong in direction or level (A-drives-B where the source says B-modulates-A). Quote both the learner's version and the source's version.

Every verdict quotes the learner's verbatim words and the source passage. An invented or paraphrased "you said…" is `PRIOR_UNGROUNDED`, the same standard as every other flow.

The learner revises and re-presents; each re-presentation gets one fresh diagnosis turn. The loop closes when a re-presented model draws only `right` verdicts, or `missing` items the learner consciously parks in their own words. Parked items stay parked, recorded with those words. The final model version, verbatim, plus the diagnosis history enters the session handoff.

The forbidden move: pi never rewrites, redraws, restates in cleaner prose, or "cleans up" the learner's model. Correct a single link if it is wrong, but only as a quoted verdict; never return a restructured model. No attack battery, no hint ladder, no repair mode, no graduation clones in this flow.

### Retrieval sessions

A benchmark session runs inside the review flow, not the reading flow. When a queue entry's `type` is `benchmark`, its concept name is the benchmark-ledger key and the session replaces the standard discriminative item:

1. **Dump and confidence.** Open with the Free recall procedure above, cited not restated: closed book, no interruption, confidence marks per dumped item, then the quoted check over the session's scoped material.
2. **Ledger questions.** Read the 15 questions from `Learning System/Core/🎯 Benchmarks.json` under the entry's concept name, level labels included. Ask them as written. Never invent, reword, or substitute a question; a missing ledger entry is reported and stops the session.
3. **One batch.** Ask all 15 in one `[[TURN:quiz]]` with `qtype:"free-recall"`. No answer, cue, hint, or grading before the learner has attempted every question and rated confidence.
4. **Grade.** Grade per question against the ledger's `source` and `scope`, then return the quoted check with a source quote for every miss and `sure`-but-wrong answers flagged as priority gaps.
5. **Score report.** Close with the hit rate per level (low, mid, high) against this shot's 90/80/70 targets, plus the trajectory across the shots taken so far.

The +1d / +1w / +1m dates are fixed. A miss re-appears at the next shot without resetting the clock, and the third shot graduates the session. Benchmark items are exempt from the concept/design clone mandate; that exemption is type-gated and otherwise unchanged.

At reading-session close (pipeline step 9), dispatch the `clerk` with the session name, the session date, and the 15-question JSON. The clerk seeds the retrieval track with `ops.py benchmark "<session name>" --date <session date> --questions-file <path>`, writes the session note, and commits state.

## Every turn

Begin every assistant message with a turn tag. Dispatch each verifier once in the foreground with `dispatch({ agent, task: { ...envelope... } })` and emit the verified draft unchanged. No gate or tooling commentary in learner-visible text.
