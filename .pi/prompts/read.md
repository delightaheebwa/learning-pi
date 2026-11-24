---
description: Run a Sung-style reading session on a source the learner is about to read
argument-hint: "<source-or-section>"
---
[[FLOW:read]]

Run a reading session. Load the `learning-read` skill and follow its reading pipeline: scope the reading, then check what the learner retrieves.

Begin every assistant message with a turn tag. Dispatch each verifier once in the foreground with `dispatch({ agent, task: { ...envelope... } })` and emit the verified draft unchanged.
