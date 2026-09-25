---
description: Teach me a topic (probe -> plan -> teach)
argument-hint: "<topic>"
---
[[FLOW:teach]]
Teach me about: $ARGUMENTS

First call the `scout` subagent to gather context for this topic, then load the `learning-teach` skill and run the probe -> plan -> teach loop in this session. Dispatch foreground `fact-check` / `quiz-audit` / `grade-audit` subagents exactly as the skill requires — do not bypass the gate — and when one learner reply answers several questions, grade them in ONE batched `grade-audit` envelope (`items[]`), not one subagent per answer. Derive the current position from `Learning System/CURRICULUM.md` and `Learning System/MISSION.md`; stop and report if they disagree.

Honor the mini-checkpoint pause protocol: deliver a checkpoint as a sequence of mini-checkpoints — one atomic idea per message, pausing after each to invite questions/tangents before the next piece; only after the last mini-checkpoint give the checkpoint's single practice, then pause again after grading. Never dump a whole checkpoint at once. Deliver each mini-checkpoint's idea through elicit → attempt → consolidate — one grounded prediction question, then at most two guiding questions, then the clean statement — and always honor "just tell me". Keep turns answer-first and about one screen; never skip a step in a worked example. Surface any source contradiction loudly. Write no `Learning System/` files mid-lesson — batch them at the pause/lesson-end handoff, then dispatch one foreground `tutor-audit` on that batch before the summary.

Begin every assistant message with a turn tag on its first line — `[[TURN:claims]]` (teaching/plan), `[[TURN:quiz]]` (questions), `[[TURN:grade]]` (grading), or `[[TURN:none]]`. The gate strips the tag before the learner sees it. Dropped `grade`/`quiz`/`claims` tags are recovered from a bound verifier receipt, but still tag every turn.

Dispatch each verifier ONCE per turn as a foreground call (`async: false`) and wait for its verdict before emitting. Never re-dispatch a verifier for the same draft: if a message is withheld, re-emit the verified draft (or fix the tag) — do not re-verify. Re-verification is only for a materially corrected draft after an `ISSUES` verdict. Hints are `claims` turns too, and their `rendered_content` must carry the method only — never the final answer.
