---
description: Resume a paused interrogation at the first unresolved attack
---
[[FLOW:resume]]

Resume the paused interrogation. Load the `learning-teach` skill.

## Locate the session

Always dispatch `scout` with `{mode:"lesson", purpose:"resume"}` first. Do not search `Learning System/Lessons/`, `Sessions/`, or source material yourself.

Use the receipt's `lesson_file`, `session_file`, and `resume_from`. Never re-derive them from filenames. If `resume_from` is null or `status:"none"`, say no in-progress session exists and suggest `/lesson`. Surface any `failed_refs` or `contradictions` with a visible warning callout before resuming.

## Resume the interrogation

Read only the named lesson and session files. State the topic and open item, quoting the learner's last model verbatim. Do not re-teach and do not re-read the material for them.

Resume at the next unresolved attack in the triage's dependency order. That is an on-path row whose `requires` are all `solid`. If triage is complete, resume at graduation. Predict before each attack. Verify every attack, source return, hint, counterexample, and grade with the matching verifier. Allow one attack per turn. Pause after every grade and run one check on the repaired claim.

Begin every assistant message with a turn tag. Dispatch each verifier once in the foreground with `dispatch({ agent, task: { ...envelope... } })`. Emit the verified draft unchanged.
