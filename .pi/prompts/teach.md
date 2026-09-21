---
description: Teach me a topic (probe -> plan -> teach)
argument-hint: "<topic>"
---
[[FLOW:teach]]
Teach me about: $ARGUMENTS

First call the `scout` subagent to gather context for this topic, then load the `learning-teach` skill and run the probe -> plan -> teach loop in this session. Dispatch foreground `fact-check` / `quiz-audit` subagents exactly as the skill requires — do not bypass the gate. Derive the current position from `Learning System/CURRICULUM.md` and `Learning System/MISSION.md`; stop and report if they disagree.

Honor the checkpoint pause protocol: teach one checkpoint's idea, pause and invite questions, then give its practice; after grading, pause again before the next checkpoint. Surface any source contradiction loudly. Write no `Learning System/` files mid-lesson — batch them at the pause/lesson-end handoff, then dispatch one foreground `tutor-audit` on that batch before the summary.

Begin every assistant message with a turn tag on its first line — `[[TURN:claims]]` (teaching/plan), `[[TURN:quiz]]` (questions), `[[TURN:grade]]` (grading), or `[[TURN:none]]`. The gate strips the tag before the learner sees it. Dropped `grade`/`quiz`/`claims` tags are recovered from a bound verifier receipt, but still tag every turn.

Dispatch each verifier ONCE per turn as a foreground call (`async: false`) and wait for its verdict before emitting. Never re-dispatch a verifier for the same draft: if a message is withheld, re-emit the verified draft (or fix the tag) — do not re-verify. Re-verification is only for a materially corrected draft after an `ISSUES` verdict. Hints are `claims` turns too, and their `rendered_content` must carry the method only — never the final answer.
