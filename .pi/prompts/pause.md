---
description: Pause the interrogation and bank the model + open attacks
---
[[FLOW:resume]]
Pause the interrogation cleanly. Load the `learning-teach` skill and run its pause protocol.

1. Write the partial handoff batch once: lesson file with `Status: Paused at Checkpoint N/M, mini K/L` and a `## Resume` section naming the next unresolved attack (in dependency order) + exact source pointer; session note; learning record; `Pending Ingest.json` with `partial:true`, `status:"in-progress"`, `resume_from`, `learner_model:{v1,v2}` (verbatim), `triage`, `open_attacks`, `repair_steps`, `concepts`, `mistakes`, `attempts`, `dependency_events`.
2. Dispatch ONE foreground `tutor-audit` on the batch; fix and re-audit until zero issues.
3. Tell the learner the model and open attacks are banked, run `/ingest` to sync the wiki/state, and `/continue` picks up at the first unresolved attack with no re-reading.

Begin every assistant message with a turn tag. Never write state outside this handoff batch.
