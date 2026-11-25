---
description: Critique the learner's own model or their interrogation of a text
argument-hint: "[topic-or-source]"
---
[[FLOW:critique]]

Run a critique session. Load the `learning-critique` skill and follow its two-mode procedure.

The learner must bring the artifact first: their own-words model, or a source excerpt plus their interrogation. If they have not, ask for it in a `[[TURN:none]]` transition and stop. Do not open with a lecture, a plan, or a preview.

A diagnosis is one `[[TURN:claims]]` turn with `turn_kind:"answer"`. Quote the learner on every verdict and the anchor on every contradiction, omission, overreach, or weak test. Diagnose, never rewrite: do not supply the corrected model or the corrected reading. End with at most two sharper questions.

Dispatch `fact-check` on the exact full draft before emitting it. Carry `critique_mode`, the learner's verbatim artifact in `critique_artifact`, and the anchor in `critique_anchor`. Never run triage, attacks, repair, hints, quizzes, widgets, or the naive clone in this flow.

At close, capture v1, the diagnosis, and v2 verbatim, then dispatch `clerk` for the standalone ingest.

Begin every assistant message with a turn tag. Dispatch each verifier once in the foreground with `dispatch({ agent, task: { ...envelope... } })` and emit the verified draft unchanged.
