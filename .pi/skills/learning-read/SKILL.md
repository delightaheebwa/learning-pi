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

Placeholder, owned by `benchmark-session`. Fill with the four brief parts, the 15-question benchmark, and the keyword rule.

### Free recall

Placeholder, owned by `free-recall`. Fill with the dump, confidence, and quoted-check procedure.

### Model diagnosis

Placeholder, owned by `model-diagnose`. Fill with the four diagnosis buckets and the no-rewrite rule.

### Retrieval sessions

Placeholder, owned by `benchmark-retrieval`. Fill with the fixed shots, the rescoring rule, and the persistence shape.

## Every turn

Begin every assistant message with a turn tag. Dispatch each verifier once in the foreground with `dispatch({ agent, task: { ...envelope... } })` and emit the verified draft unchanged. No gate or tooling commentary in learner-visible text.
