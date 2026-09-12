---
description: Teach me a topic (probe -> plan -> teach)
argument-hint: "<topic>"
---
Teach me about: $ARGUMENTS

First call the `scout` subagent to gather context for this topic, then load the `learning-teach` skill and run the probe -> plan -> teach loop in this session. Dispatch foreground `fact-check` / `quiz-audit` subagents exactly as the skill requires — do not bypass the gate. Derive the current position from `Learning System/CURRICULUM.md` and `Learning System/MISSION.md`; stop and report if they disagree.
