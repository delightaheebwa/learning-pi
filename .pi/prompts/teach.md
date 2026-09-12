---
description: Teach me a topic (probe -> plan -> teach)
argument-hint: "<topic>"
---
[[FLOW:teach]]
Teach me about: $ARGUMENTS

First call the `scout` subagent to gather context for this topic, then load the `learning-teach` skill and run the probe -> plan -> teach loop in this session. Dispatch foreground `fact-check` / `quiz-audit` subagents exactly as the skill requires — do not bypass the gate. Derive the current position from `Learning System/CURRICULUM.md` and `Learning System/MISSION.md`; stop and report if they disagree.

Honor the checkpoint pause protocol: teach one checkpoint's idea, pause and invite questions, then give its practice; after grading, pause again before the next checkpoint. Surface any source contradiction loudly. After writing lesson/session/record files, dispatch a foreground `tutor-audit` before the summary.

Begin every assistant message with a turn tag on its first line — `[[TURN:claims]]` (teaching/plan), `[[TURN:quiz]]` (questions), `[[TURN:grade]]` (grading), or `[[TURN:none]]`. The gate strips the tag before the learner sees it.
