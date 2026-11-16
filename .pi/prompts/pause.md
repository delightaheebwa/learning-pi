---
description: Pause the interrogation and bank the model plus open attacks
---
[[FLOW:resume]]

Pause the interrogation cleanly. Load the `learning-teach` skill and run its pause protocol.

1. Write the partial handoff batch once. Write the lesson file with `Status: Paused at Checkpoint N/M, mini K/L` and a `## Resume` section naming the next unresolved attack in dependency order and its exact source pointer. Write the session note and the learning record. Write `Pending Ingest.json` with `partial:true`, `status:"in-progress"`, `resume_from`, `learner_model:{v1,v2}` verbatim, `triage`, `open_attacks`, `repair_steps`, `concepts`, `mistakes`, `attempts`, and `dependency_events`.
2. Dispatch one foreground `tutor-audit` on the batch. Fix issues and re-audit until zero issues.
3. Tell the learner the model and open attacks are banked. Tell them to run `/ingest` to sync the wiki and state. Tell them `/continue` picks up at the first unresolved attack with no re-reading.

Begin every assistant message with a turn tag. Never write state outside this handoff batch.
