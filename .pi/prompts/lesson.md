---
description: Run the next curriculum lesson
---
[[FLOW:teach]]
Run the next curriculum lesson. Derive the next lesson from `Learning System/CURRICULUM.md`, `Learning System/MISSION.md`, and `Learning System/Lessons/`; if they disagree, stop and report. Call the `scout` subagent to gather context for a new lesson, then load the `learning-teach` skill and run the probe -> plan -> teach loop in this session.

Begin every assistant message with a turn tag on its first line — `[[TURN:claims]]` (teaching/plan), `[[TURN:quiz]]` (questions), `[[TURN:grade]]` (grading), or `[[TURN:none]]`. The gate strips the tag before the learner sees it.
