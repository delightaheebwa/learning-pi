---
description: Resume a paused interrogation at the first unresolved attack
---
[[FLOW:resume]]
Resume the paused interrogation. Load the `learning-teach` skill.

Always dispatch `scout` with `{mode:"lesson", purpose:"resume"}` first — do not search `Learning System/Lessons/`, `Sessions/`, or source material yourself. Use the receipt's `lesson_file`, `session_file`, and `resume_from` (`Checkpoint N/M, mini K/L`); never re-derive them from filenames. If `resume_from` is null or `status:"none"`, say no in-progress session exists and suggest `/lesson`. Surface any `failed_refs`/`contradictions` with a visible `⚠️` callout before resuming.

Read only the named lesson/session files. State the topic and open item, quoting the learner's last model verbatim. Do not re-teach and do not re-read the material for them: resume at the next unresolved attack (or at graduation if triage is complete). Verify every attack, source-return, hint, counterexample, and grade with the matching verifier; one attack per turn; pause after every grade.

Begin every assistant message with a turn tag; dispatch each verifier once with `dispatch({ agent, task: { ...envelope... } })` (foreground) and emit the verified draft unchanged.
